from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
import os
import shutil
from app import models
from app.database import get_db
from app.oauth2 import get_current_user
from app.services.text_extractor import extract_text
from app.services.document_processor import process_extracted_text
from app.services.document_task import process_document_task
from app.models import Document

# for embedding
from app.services.embedding import generate_embedding


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

UPLOAD_DIR = "app/uploads"

@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # validate file type
    allowed_extensions = [".pdf", ".txt", ".docx"]
    file_ext = os.path.splitext(file.filename)[1]

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type"
        )

    # save file to disk
    file_path = f"{UPLOAD_DIR}/{current_user.id}_{file.filename}"
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save file"
        )

    # create DB record with status queued
    new_document = models.Document(
        filename=file.filename,
        file_path=file_path,
        owner_id=current_user.id,
        status="queued"           # ✅ queued instead of uploaded
    )
    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    # fire background task — returns immediately
    process_document_task.delay(new_document.id)   # ✅ non-blocking

    # return instantly — no waiting for processing
    return {
        "id": new_document.id,
        "filename": new_document.filename,
        "status": new_document.status,   # returns "queued"
        "message": "Document uploaded. Processing in background."
    }


# status check endpoint — user polls this to see progress
@router.get("/{document_id}/status")
def get_document_status(
    document_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": document.id,
        "filename": document.filename,
        "status": document.status    # queued | processing | ready | failed
    }

    
    
# deleting document
@router.delete("/delete-docs/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.owner_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # delete uploaded file
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    # delete extracted text
    if document.extracted_text_path and os.path.exists(document.extracted_text_path):
        os.remove(document.extracted_text_path)

    # delete document (chunks will delete automatically if cascade is set)
    db.delete(document)
    db.commit()

    return {"message": "Document deleted successfully"}

@router.get("/")
def get_documents(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    documents = db.query(Document).filter(
        Document.owner_id == current_user.id
    ).all()

    return documents