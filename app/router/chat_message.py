from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.oauth2 import get_current_user
from app.models import Chat, Message
from app.schema import MessageRequest

from app.services.llm import generate_answer, generate_answer_stream
from app.services.retrieval_service import retrieve_chunks
from app.services.redis_client import redis_client

router = APIRouter(
    prefix="/chat",
    tags=["Chat Messages"]
)


@router.post("/{chat_id}/message")
def send_message(
    chat_id: int,
    request: MessageRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # verify chat belongs to user
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.owner_id == current_user.id
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # save user message
    user_message = Message(
        chat_id=chat_id,
        role="user",
        content=request.query
    )
    db.add(user_message)
    db.commit()

    # check Redis cache first
    cache_key = f"user:{current_user.id}:query:{request.query}"
    cached_answer = redis_client.get(cache_key)

    if cached_answer:
        assistant_message = Message(
            chat_id=chat_id,
            role="assistant",
            content=cached_answer
        )
        db.add(assistant_message)
        db.commit()
        return {
            "chat_id": chat_id,
            "response": cached_answer,
            "source": "redis_cache"
        }

    # hybrid search — vector + BM25 + RRF
    final_chunks = retrieve_chunks(
        question=request.query,
        db=db,
        user_id=current_user.id,
        top_k=10,
        final_k=5
    )

    if not final_chunks:
        raise HTTPException(
            status_code=400,
            detail="No document chunks found. Please upload a document first."
        )

    # build chat history (last 6 messages)
    previous_messages = db.query(Message).filter(
        Message.chat_id == chat_id
    ).order_by(Message.created_at.asc()).all()

    history = ""
    for msg in previous_messages[-6:]:
        history += f"{msg.role}: {msg.content}\n"

    # build prompt
    context = "\n\n".join(final_chunks)
    final_prompt = f"""
    You are a helpful AI assistant. Give short and straightforward answers strictly from the context. Do not hallucinate.

    Conversation History:
    {history}

    Retrieved Context:
    {context}

    Current User Question:
    {request.query}

    Answer naturally and clearly. If context not found say directly that you don't know.
    """

    # call LLM
    answer = generate_answer(final_prompt)

    # cache response for 1 hour
    redis_client.set(cache_key, answer, ex=3600)

    # save assistant response
    assistant_message = Message(
        chat_id=chat_id,
        role="assistant",
        content=answer
    )
    db.add(assistant_message)
    db.commit()

    return {
        "chat_id": chat_id,
        "response": answer,
        "retrieved_chunks": final_chunks
    }


@router.post("/{chat_id}/message/stream")
def send_message_stream(
    chat_id: int,
    request: MessageRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # verify chat belongs to user
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.owner_id == current_user.id
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # save user message
    user_message = Message(
        chat_id=chat_id,
        role="user",
        content=request.query
    )
    db.add(user_message)
    db.commit()

    # hybrid search
    final_chunks = retrieve_chunks(
        question=request.query,
        db=db,
        user_id=current_user.id,
        top_k=10,
        final_k=5
    )

    if not final_chunks:
        raise HTTPException(
            status_code=400,
            detail="No document chunks found. Please upload a document first."
        )

    # build history
    previous_messages = db.query(Message).filter(
        Message.chat_id == chat_id
    ).order_by(Message.created_at.asc()).all()

    history = ""
    for msg in previous_messages[-6:]:
        history += f"{msg.role}: {msg.content}\n"

    # build prompt
    context = "\n\n".join(final_chunks)
    final_prompt = f"""
    You are a helpful AI assistant. Give short and straightforward answers strictly from the context. Do not hallucinate.

    Conversation History:
    {history}

    Retrieved Context:
    {context}

    Current User Question:
    {request.query}

    Answer naturally and clearly. If context not found say directly that you don't know.
    """

    full_answer = []

    def stream_generator():
        for token in generate_answer_stream(final_prompt):
            full_answer.append(token)
            yield f"data: {token}\n\n"

        complete_answer = "".join(full_answer)
        assistant_message = Message(
            chat_id=chat_id,
            role="assistant",
            content=complete_answer
        )
        db.add(assistant_message)
        db.commit()

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )