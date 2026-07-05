# from app.services.ai_models import reranker_model

# def rerank(query, chunks, top_k=5):

#     pairs = []
#     # print(chunks)
#     for chunk in chunks:
#         pairs.append((query, chunk))
#     scores = reranker_model.predict(pairs)
#     scored_chunks = list(zip(chunks, scores))
#     # print(scores)
#     scored_chunks.sort(
#         key=lambda x: x[1],
#         reverse=True
#     )

#     top_chunks = [
#         chunk
#         for chunk, score in scored_chunks[:top_k]
#     ]
#     return top_chunks



import os
import requests
from dotenv import load_dotenv

load_dotenv()

JINA_API_KEY = os.getenv("JINA_API_KEY")
JINA_RERANK_URL = "https://api.jina.ai/v1/rerank"
RERANK_MODEL = "jina-reranker-v2-base-multilingual"

headers = {
    "Authorization": f"Bearer {JINA_API_KEY}",
    "Content-Type": "application/json"
}


def rerank(query: str, chunks: list[str], top_k: int = 3) -> list[str]:
    """
    Reranks chunks using Jina Reranker API.
    Returns top_k most relevant chunks sorted by score.
    """
    if not chunks:
        return []

    payload = {
        "model": RERANK_MODEL,
        "query": query,
        "documents": chunks,
        "top_n": top_k
    }

    response = requests.post(JINA_RERANK_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"Reranker error: {response.status_code} - {response.text}")
        return chunks[:top_k]   # fallback — return first N chunks without reranking

    results = response.json()["results"]

    # results already sorted by relevance score
    return [result["document"]["text"] for result in results]