from app.celery_app import celery_app
from app.database import session_local
from app import models
from app.services.text_extractor import extract_text
from app.services.document_processor import process_extracted_text
from app.services.embedding import generate_embedding


@celery_app.task(bind=True, max_retries=3)
def process_document_task(self, document_id: int):
    """
    Background task that:
    1. Extracts text from file
    2. Cleans and chunks text
    3. Generates embeddings
    4. Stores chunks in DB
    5. Updates document status
    """
    db = session_local()

    try:
        # fetch document from DB
        document = db.query(models.Document).filter(
            models.Document.id == document_id
        ).first()

        if not document:
            return {"error": "Document not found"}

        # update status to processing
        document.status = "processing"
        db.commit()

        # Step 1 — extract text
        text_path = extract_text(document.file_path)
        document.extracted_text_path = text_path
        db.commit()

        # Step 2 — clean and chunk
        chunks = process_extracted_text(text_path)

        # Step 3 — generate embeddings and store chunks
        for i, chunk_text in enumerate(chunks):
            vector = generate_embedding(chunk_text)
            chunk = models.DocumentChunk(
                document_id=document.id,
                chunk_index=i,
                chunk_text=chunk_text,
                embedding=vector
            )
            db.add(chunk)

        # commit all chunks at once
        db.commit()

        # Step 4 — mark as ready
        document.status = "ready"
        db.commit()

        print(f"Document {document_id} processed successfully")
        return {"status": "ready", "document_id": document_id}

    except Exception as e:
        # mark as failed
        document = db.query(models.Document).filter(
            models.Document.id == document_id
        ).first()
        if document:
            document.status = "failed"
            db.commit()

        # retry up to 3 times
        raise self.retry(exc=e, countdown=5)

    finally:
        db.close()