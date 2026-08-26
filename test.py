# test_jina.py
import sys
sys.path.append(".")

from app.services.embedding import EmbeddingService
from app.services.cross_encoder import rerank

print("Testing embedding...")
embedding_service = EmbeddingService()
emb = embedding_service.generate_embedding("what is machine learning")
print(f"Dimension: {len(emb)}")   # must be 768

print("\nTesting batch embedding...")
embs = embedding_service.generate_embeddings_batch(["hello world", "machine learning", "deep learning"])
print(f"Batch: {len(embs)} embeddings, each {len(embs[0])} dim")

print("\nTesting reranker...")
query = "what is machine learning"
chunks = [
    "Machine learning is a subset of AI that learns from data",
    "Paris is the capital of France",
    "Neural networks are inspired by the human brain",
    "The weather today is sunny and warm"
]
result = rerank(query, chunks, top_k=2)
print(f"Top 2 reranked chunks:")
for i, r in enumerate(result):
    print(f"{i+1}. {r[:80]}")
