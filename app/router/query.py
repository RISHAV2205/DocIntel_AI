from fastapi import APIRouter,Depends
from pydantic import BaseModel
from app.oauth2 import get_current_user
from app.services.embedding import generate_embedding
from app.database import get_db
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sqlalchemy import text
import json
from app.services.retrieval_service import retrieve_chunks
from app.services.llm import generate_answer
from app.services.cross_encoder import rerank

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

    top_chunks,top_scores=retrieve_chunks(rows,query_embedding)
    reranked_chunks=rerank(request.query,top_chunks)
    ans= generate_answer(request.query, reranked_chunks)
    

    # Step 5: Return result
    return {
        "query": request.query,
        "result":ans
    }