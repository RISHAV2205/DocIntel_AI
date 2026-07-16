from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.oauth2 import get_current_user
from app.schema import MessageRequest
from app.services.chat_service import ChatMessageService


router = APIRouter(
    prefix="/chat",
    tags=["Chat Messages"],
)


@router.post("/{chat_id}/message")
def send_message(
    chat_id: int,
    request: MessageRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ChatMessageService(db)
    return service.send_message(chat_id, current_user.id, request.query)


@router.post("/{chat_id}/message/stream")
def send_message_stream(
    chat_id: int,
    request: MessageRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ChatMessageService(db)
    stream = service.prepare_stream(chat_id, current_user.id, request.query)
    return StreamingResponse(
        stream,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
