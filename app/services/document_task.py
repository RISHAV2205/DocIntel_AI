from app.celery_app import celery_app
from app.database import session_local
from app import models
from app.services.text_extractor import extract_text
from app.services.document_processor import process_extracted_text
from app.services.embedding import EmbeddingService
from app.services.storage import download_file   # ✅ NEW
import os
import tempfile
from app.core.logging import get_logger

logger = get_logger(__name__)



# bind=True — gives access to self (the task instance itself). Needed because we call self.retry() later.
@celery_app.task(bind=True, max_retries=3)
def process_document_task(self, document_id: int):
    db = session_local()
    logger.info(f"Started processing document {document_id}")
    try:
        document = db.query(models.Document).filter(
            models.Document.id == document_id
        ).first()
        if not document:
            logger.error(f"Document {document_id} not found")
            return {"error": "Document not found"}

        document.status = "processing"
        logger.info(f"Document {document_id} status changed to processing")
        db.commit()

        # Step 1 — download file from S3
        file_bytes = download_file(document.file_path)
        logger.info("File downloaded successfully")

        # save to temp file — extract_text() expects a file path
        file_ext = os.path.splitext(document.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            tmp.write(file_bytes)
            temp_file_path = tmp.name

        # Step 2 — extract text
        logger.info("Starting text extraction")
        text_path = extract_text(temp_file_path)
        document.extracted_text_path = text_path
        db.commit()

        os.remove(temp_file_path)

        # Step 3 — clean and chunk
        chunks = process_extracted_text(text_path)
        logger.info(f"Created {len(chunks)} chunks")

        # Step 4 — embed and store
        embedding_service = EmbeddingService()
        batch_size = 32
        for batch_start in range(0, len(chunks), batch_size):
            batch = chunks[batch_start:batch_start + batch_size]
            logger.info(f"Generating embeddings for batch "f"{batch_start // batch_size + 1}")
            embeddings = embedding_service.generate_embeddings_batch(batch)
            for i, (chunk_text, vector) in enumerate(zip(batch, embeddings)):
                chunk = models.DocumentChunk(
                    document_id=document.id,
                    chunk_index=batch_start + i,
                    chunk_text=chunk_text,
                    embedding=vector
                )
                db.add(chunk)
            db.commit()
            logger.info(f"Document {document_id} embedded successfully")

        document.status = "ready"
        db.commit()
        logger.info("document task completed...")
        return {"status": "ready", "document_id": document_id}

    except Exception as e:
        logger.exception(f"Processing failed for document {document_id}")
        document = db.query(models.Document).filter(
            models.Document.id == document_id
        ).first()
        if document:
            document.status = "failed"
            db.commit()

        raise self.retry(exc=e, countdown=5)

    finally:
        db.close()
