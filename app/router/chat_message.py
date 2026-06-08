from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse   
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.oauth2 import get_current_user
from app.models import Chat, Message
from app.schema import MessageRequest

from app.services.embedding import generate_embedding
from app.services.cross_encoder import rerank
from app.services.llm import generate_answer, generate_answer_stream  

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

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
    
    #verifying user
    chat = db.query(Chat).filter(
    Chat.id == chat_id,
    Chat.owner_id == current_user.id).first()

    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat not found")
    
    #saving user message
    user_message = Message(
    chat_id=chat_id,
    role="user",
    content=request.query)
    
    db.add(user_message)
    db.commit()
    
    # seeing cache
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
        
    #creating query embedding
    query_embedding = generate_embedding(request.query)
    
    #retrieing chunks
    rows = db.execute(
    text("""
    SELECT dc.chunk_text, dc.embedding
    FROM document_chunks dc
    JOIN documents d
    ON dc.document_id = d.id
    WHERE d.owner_id = :user_id
    """),
    {"user_id": current_user.id}).fetchall()
    
    
    if len(rows) == 0:
        raise HTTPException(
            status_code=400,
            detail="No document chunks found. Please upload a document first."
        )
    
    # testing
    print("CURRENT USER:", current_user.id)
    print("ROWS FOUND:", len(rows))
    # print(rows)
    
    
    rows = db.execute(
    text("""
        SELECT dc.chunk_text
        FROM document_chunks dc
        JOIN documents d
        ON dc.document_id = d.id
        WHERE d.owner_id = :user_id
        ORDER BY dc.embedding <=> CAST(:query_embedding AS vector)
        LIMIT 10
    """),
    {
        "user_id": current_user.id,
        "query_embedding": str(query_embedding)
    }
).fetchall()
    
    # print(rows)
    
    retrieved_chunks = [row[0] for row in rows]

    #rerank
    final_chunks = rerank(
    request.query,
    retrieved_chunks,
    top_k=3)
    
    #loading chat history
    previous_messages = db.query(Message).filter(
    Message.chat_id == chat_id).order_by(Message.created_at.asc()).all()
    
    #format history
    history = ""
    for msg in previous_messages[-6:]:
        history += f"{msg.role}: {msg.content}\n"
    
    #final prompt
    context = "\n\n".join(final_chunks)

    final_prompt = f"""
    You are a helpful AI assistant. give short and straightforward answer for each que

    Conversation History:
    {history}

    Retrieved Context:
    {context}

    Current User Question:
    {request.query}

    Answer naturally and clearly.
    donot hallucinate and if context not found say directly that i dont know much about it
    """
    
    #calling llm
    answer = generate_answer(final_prompt)
    
    # caching our response
    redis_client.set(
    cache_key,answer,ex=3600)
    
    #saving ai response
    assistant_message = Message(
    chat_id=chat_id,
    role="assistant",
    content=answer
    )
    
    print(answer)

    db.add(assistant_message)
    db.commit()
    
    #returning response
    return {
    "chat_id": chat_id,
    "response": answer,
    "retrieved_chunks": final_chunks}
    
    
# NEW — streaming route
@router.post("/{chat_id}/message/stream")
def send_message_stream(
    chat_id: int,
    request: MessageRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Step 1 — verify chat belongs to user
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.owner_id == current_user.id
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Step 2 — save user message
    user_message = Message(
        chat_id=chat_id,
        role="user",
        content=request.query
    )
    db.add(user_message)
    db.commit()

    # Step 3 — embed query
    query_embedding = generate_embedding(request.query)

    # Step 4 — retrieve chunks (same as your existing code)
    rows = db.execute(
        text("""
            SELECT dc.chunk_text, dc.embedding
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            WHERE d.owner_id = :user_id
        """),
        {"user_id": current_user.id}
    ).fetchall()

    if not rows:
        raise HTTPException(
            status_code=400,
            detail="No document chunks found. Please upload a document first."
        )

    rows = db.execute(
    text("""
        SELECT dc.chunk_text
        FROM document_chunks dc
        JOIN documents d
        ON dc.document_id = d.id
        WHERE d.owner_id = :user_id
        ORDER BY dc.embedding <=> CAST(:query_embedding AS vector)
        LIMIT 10
    """),
    {
        "user_id": current_user.id,
        "query_embedding": str(query_embedding)
    }
    ).fetchall()

    # print(rows)

    retrieved_chunks = [row[0] for row in rows]

    # Step 6 — rerank
    final_chunks = rerank(request.query, retrieved_chunks, top_k=3)

    # Step 7 — build history (your existing logic)
    previous_messages = db.query(Message).filter(
        Message.chat_id == chat_id
    ).order_by(Message.created_at.asc()).all()

    history = ""
    for msg in previous_messages[-6:]:
        history += f"{msg.role}: {msg.content}\n"

    # Step 8 — build prompt (your existing prompt)
    context = "\n\n".join(final_chunks)
    final_prompt = f"""
    You are a helpful AI assistant. give short and straightforward answer for each question.

    Conversation History:
    {history}

    Retrieved Context:
    {context}

    Current User Question:
    {request.query}

    Answer naturally and clearly.
    Do not hallucinate. If context not found say directly that you don't know.
    """

    # Step 9 — stream response while collecting full answer for DB
    full_answer = []

    def stream_generator():
        for token in generate_answer_stream(final_prompt):
            full_answer.append(token)
            # SSE format — frontend reads this
            yield f"data: {token}\n\n"

        # stream finished — save complete answer to DB
        complete_answer = "".join(full_answer)
        assistant_message = Message(
            chat_id=chat_id,
            role="assistant",
            content=complete_answer
        )
        db.add(assistant_message)
        db.commit()

        # signal frontend that stream is done
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"   # important for nginx
        }
    )