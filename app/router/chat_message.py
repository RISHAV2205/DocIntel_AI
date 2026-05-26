from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.oauth2 import get_current_user
from app.models import Chat, Message
from app.schema import MessageRequest

from app.services.embedding import generate_embedding
from app.services.cross_encoder import rerank
from app.services.llm import generate_answer

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

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
    
    # preparing embeding
    texts = []
    embeddings = []
    for row in rows:
        texts.append(row[0])
        embeddings.append(row[1])
    embeddings = np.array(embeddings)
    
    #vector similarity
    similarities = cosine_similarity(
    [query_embedding],
    embeddings)[0]
    
    #initial top 10
    k = 10
    top_indices = similarities.argsort()[-k:][::-1]
    retrieved_chunks = [
        texts[i]
        for i in top_indices
    ]

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
    """
    
    #calling llm
    answer = generate_answer(final_prompt)
    
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