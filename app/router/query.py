from fastapi import APIRouter,Depends
from pydantic import BaseModel
from app.oauth2 import get_current_user
from app.services.embedding import EmbeddingService
from app.database import get_db
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sqlalchemy import text
import json
from app.services.retrieval_service import retrieve_chunks
from app.services.llm import generate_answer
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Request Schema
class QueryRequest(BaseModel):
    query: str


@router.post("/query")
def retrieve_chunks(request: QueryRequest,conn=Depends(get_db),current_user = Depends(get_current_user)):
    logger.info("Document query received: user_id=%s query_length=%s", current_user.id, len(request.query))
    # Step 1: Convert query → embedding
    embedding_service = EmbeddingService()
    query_embedding = embedding_service.generate_embedding(request.query)

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
        logger.info("Document query has no indexed chunks: user_id=%s", current_user.id)
        return {"message": "No documents found"}

    top_chunks,top_scores=retrieve_chunks(rows,query_embedding)
    ans= generate_answer(request.query, top_chunks)
    logger.info("Document query completed: user_id=%s retrieved_chunks=%s", current_user.id, len(top_chunks))
    

    # Step 5: Return result
    return {
        "query": request.query,
        "result":ans
    }
