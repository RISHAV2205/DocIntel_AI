from fastapi import APIRouter,Depends
from pydantic import BaseModel
from app.oauth2 import get_current_user
from app.services.embedding import generate_embedding
from app.database import get_db
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sqlalchemy import text
import json
from app.services.llm import generate_answer

router = APIRouter()

# Request Schema
class QueryRequest(BaseModel):
    query: str


@router.post("/query")
def retrieve_chunks(request: QueryRequest,conn=Depends(get_db),current_user = Depends(get_current_user)):
    print(current_user)
    # Step 1: Convert query → embedding
    query_embedding = generate_embedding(request.query)

    # Step 2: Fetch stored chunks + embeddings
    rows = conn.execute(
    text("""
        SELECT dc.chunk_text, dc.embedding
        FROM document_chunks dc
        JOIN documents d ON dc.document_id = d.id
        WHERE d.owner_id = :user_id
    """),
    {"user_id": current_user.id}
).fetchall()


    # Edge case: no data
    if len(rows) == 0:
        return {"message": "No documents found"}

    texts = []
    embeddings = []

    for row in rows:
        texts.append(row[0])
        embeddings.append(row[1])

    embeddings = np.array(embeddings)

    # Step 3: Compute similarity
    similarities = cosine_similarity([query_embedding], embeddings)[0]

    # Step 4: Get Top-K
    k = 3
    top_indices = similarities.argsort()[-k:][::-1]

    top_chunks = [texts[i] for i in top_indices]
    top_scores = [float(similarities[i]) for i in top_indices]
    
    ans= generate_answer(request.query, top_chunks)

    # Step 5: Return result
    return {
        "query": request.query,
        "result":ans
    }