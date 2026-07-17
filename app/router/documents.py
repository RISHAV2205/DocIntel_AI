from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from app.oauth2 import get_current_user
from app.models import Document
from app.services.document_ingestion import DocumentIngestionService
from app.services.storage import delete_file

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    ingestion_service = DocumentIngestionService(db)
    return ingestion_service.ingest(file, current_user.id)


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
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        delete_file(document.file_path)
    except Exception:
        pass

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
