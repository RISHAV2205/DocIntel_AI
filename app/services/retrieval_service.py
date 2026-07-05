from sqlalchemy import text

from app.services.embedding import generate_embedding,generate_embeddings_batch
from app.services.cross_encoder import rerank

def retrieve_chunks(
    question,
    db,
    user_id,
    top_k_retrieval=10,
    top_k_rerank=3
):

    query_embedding = generate_embedding(question)

    rows = db.execute(
        text("""
            SELECT dc.chunk_text
            FROM document_chunks dc
            JOIN documents d
            ON dc.document_id = d.id
            WHERE d.owner_id = :user_id
            ORDER BY dc.embedding <=> CAST(:query_embedding AS vector)
            LIMIT :limit
        """),
        {
            "user_id": user_id,
            "query_embedding": str(query_embedding),
            "limit": top_k_retrieval
        }
    ).fetchall()

    retrieved_chunks = [row[0] for row in rows]
    # print(retrieve_chunks)

    final_chunks = rerank(
        question,
        retrieved_chunks,
        top_k=top_k_rerank
    )

    return final_chunks