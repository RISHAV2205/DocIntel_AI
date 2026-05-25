from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Chat
from app.oauth2 import get_current_user
from app.schema import ChatCreate

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@router.post("/create")
def create_chat(
    request: ChatCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    new_chat = Chat(
    owner_id=current_user.id,
    title=request.title
)
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return {
        "chat_id": new_chat.id,
        "title": new_chat.title
    }