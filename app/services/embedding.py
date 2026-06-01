# embeddings.py
from app.services.ai_models import embedding_model

def generate_embedding(text: str):

    embedding = embedding_model.encode(text)
    return embedding.tolist()