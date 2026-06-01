from sentence_transformers import SentenceTransformer
from sentence_transformers import CrossEncoder

print("Loading Embedding Model...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Loading Reranker Model...")

reranker_model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

print("Models Loaded Successfully")