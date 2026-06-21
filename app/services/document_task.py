from app.celery_app import celery_app
from app.database import session_local
from app import models
from app.services.text_extractor import extract_text
from app.services.document_processor import process_extracted_text
from app.services.embedding import generate_embedding
from app.services.storage import download_file   # ✅ NEW
import os
import tempfile

# bind=True — gives access to self (the task instance itself). Needed because we call self.retry() later.
@celery_app.task(bind=True, max_retries=3)
def process_document_task(self, document_id: int):
    db = session_local()

    try:
        document = db.query(models.Document).filter(
            models.Document.id == document_id
        ).first()

        if not document:
            return {"error": "Document not found"}

        document.status = "processing"
        db.commit()

        # Step 1 — download file from S3
        file_bytes = download_file(document.file_path)

        # save to temp file — extract_text() expects a file path
        file_ext = os.path.splitext(document.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            tmp.write(file_bytes)
            temp_file_path = tmp.name

        # Step 2 — extract text
        text_path = extract_text(temp_file_path)
        document.extracted_text_path = text_path
        db.commit()

        os.remove(temp_file_path)

        # Step 3 — clean and chunk
        chunks = process_extracted_text(text_path)

        # Step 4 — embed and store
        for i, chunk_text in enumerate(chunks):
            vector = generate_embedding(chunk_text)
            chunk = models.DocumentChunk(
                document_id=document.id,
                chunk_index=i,
                chunk_text=chunk_text,
                embedding=vector
            )
            db.add(chunk)

        db.commit()

        document.status = "ready"
        db.commit()

        return {"status": "ready", "document_id": document_id}

    except Exception as e:
        document = db.query(models.Document).filter(
            models.Document.id == document_id
        ).first()
        if document:
            document.status = "failed"
            db.commit()

        raise self.retry(exc=e, countdown=5)

    finally:
        db.close()