import os

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models import Document
from app.services.document_task import process_document_task
from app.services.storage import delete_file, upload_file


class DocumentIngestionService:
    """Coordinates validation, storage, persistence, and task scheduling for uploads."""

    ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}

    def __init__(self, db: Session):
        self.db = db

    def ingest(self, file: UploadFile, user_id: int) -> dict:
        filename = self._validate_file(file)
        file_bytes = file.file.read()

        storage_key = self._upload_to_storage(file_bytes, filename, user_id)
        document = self._create_document(filename, storage_key, user_id)

        try:
            process_document_task.delay(document.id)
        except Exception:
            self._remove_failed_upload(document, storage_key)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Document processing could not be scheduled. The upload was rolled back.",
            )

        return {
            "id": document.id,
            "filename": document.filename,
            "status": document.status,
            "message": "Document uploaded. Processing in background.",
        }

    def _validate_file(self, file: UploadFile) -> str:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A filename is required.",
            )

        extension = os.path.splitext(file.filename)[1].lower()
        if extension not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type. Upload a PDF, TXT, or DOCX file.",
            )

        return file.filename

    def _upload_to_storage(
        self, file_bytes: bytes, filename: str, user_id: int
    ) -> str:
        try:
            return upload_file(
                file_bytes=file_bytes,
                filename=filename,
                user_id=user_id,
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to store the document. Please try again.",
            )

    def _create_document(
        self, filename: str, storage_key: str, user_id: int
    ) -> Document:
        document = Document(
            filename=filename,
            file_path=storage_key,
            owner_id=user_id,
            status="queued",
        )
        try:
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
            return document
        except Exception:
            self.db.rollback()
            self._delete_from_storage(storage_key)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save document metadata. Please try again.",
            )

    def _remove_failed_upload(self, document: Document, storage_key: str) -> None:
        self.db.delete(document)
        self.db.commit()
        self._delete_from_storage(storage_key)

    @staticmethod
    def _delete_from_storage(storage_key: str) -> None:
        try:
            delete_file(storage_key)
        except Exception:
            pass
