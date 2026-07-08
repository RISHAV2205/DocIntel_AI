from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
import os
from app import models
from app.database import get_db
from app.oauth2 import get_current_user
from app.services.document_task import process_document_task
from app.models import Document
from app.services.storage import upload_file, delete_file 

# for embedding
from app.services.embedding import generate_embedding

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
    allowed_extensions = [".pdf", ".txt", ".docx"]
    file_ext = os.path.splitext(file.filename)[1]

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type"
        )
    # read entire file
    file_bytes = file.file.read()
    print(file_bytes)

    try:
        storage_key = upload_file(
            file_bytes=file_bytes,
            filename=file.filename,
            user_id=current_user.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

    new_document = models.Document(
        filename=file.filename,
        file_path=storage_key,
        owner_id=current_user.id,
        status="queued"
    )
    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    process_document_task.delay(new_document.id)

    return {
        "id": new_document.id,
        "filename": new_document.filename,
        "status": new_document.status,
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