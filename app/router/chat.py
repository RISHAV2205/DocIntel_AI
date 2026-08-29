from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Chat
from app.oauth2 import get_current_user
from app.schema import ChatCreate
from app.models import Message
from app.core.logging import get_logger

logger = get_logger(__name__)

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
    logger.info("Chat created: chat_id=%s user_id=%s", new_chat.id, current_user.id)
    return {
        "chat_id": new_chat.id,
        "title": new_chat.title
    }
  
  
# getting all chat of a current user  
@router.get("/")
def get_user_chats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    chats = db.query(Chat).filter(
        Chat.owner_id == current_user.id
    ).order_by(Chat.created_at.desc()).all()
    logger.info("Chats listed: user_id=%s count=%s", current_user.id, len(chats))

    return chats


# geting all messages for persistent chatting
@router.get("/{chat_id}/messages")
def get_chat_messages(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.owner_id == current_user.id
    ).first()

    if not chat:
        logger.warning("Chat messages requested for inaccessible chat: chat_id=%s user_id=%s", chat_id, current_user.id)
        raise HTTPException(
            status_code=404,
            detail="Chat not found"
        )

    messages = db.query(Message).filter(
        Message.chat_id == chat_id
    ).order_by(Message.created_at.asc()).all()
    logger.info("Chat messages listed: chat_id=%s user_id=%s count=%s", chat_id, current_user.id, len(messages))

    return messages


@router.delete("/{chat_id}")
def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    # Find chat belonging to current user

    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.owner_id == current_user.id
    ).first()

    if not chat:
        logger.warning("Delete requested for inaccessible chat: chat_id=%s user_id=%s", chat_id, current_user.id)
        raise HTTPException(
            status_code=404,
            detail="Chat not found"
        )

    # Delete all messages of chat first

    db.query(Message).filter(
        Message.chat_id == chat_id
    ).delete()

    # Delete chat

    db.delete(chat)

    db.commit()
    logger.info("Chat deleted: chat_id=%s user_id=%s", chat_id, current_user.id)

    return {
        "message": "Chat deleted successfully"
    }
