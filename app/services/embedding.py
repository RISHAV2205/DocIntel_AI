import os
import requests
from dotenv import load_dotenv

load_dotenv()

JINA_API_KEY = os.getenv("JINA_API_KEY")
JINA_EMBEDDING_URL = "https://api.jina.ai/v1/embeddings"
EMBEDDING_MODEL = "jina-embeddings-v2-base-en"
EMBEDDING_DIM = 768

headers = {
    "Authorization": f"Bearer {JINA_API_KEY}",
    "Content-Type": "application/json"
}


def generate_embedding(text: str) -> list[float]:
    """Single embedding — used at query time."""
    payload = {
        "input": [text],
        "model": EMBEDDING_MODEL
    }
    response = requests.post(JINA_EMBEDDING_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"Jina embedding error: {response.status_code} - {response.text}")

    return response.json()["data"][0]["embedding"]


def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Batch embedding — used in Celery task for document chunks."""
    payload = {
        "input": texts,
        "model": EMBEDDING_MODEL
    }
    response = requests.post(JINA_EMBEDDING_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"Jina batch error: {response.status_code} - {response.text}")

    data = sorted(response.json()["data"], key=lambda x: x["index"])
    return [item["embedding"] for item in data]