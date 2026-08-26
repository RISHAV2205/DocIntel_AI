import os

import requests
from dotenv import load_dotenv

load_dotenv()


class EmbeddingService:
    """Generates single and batch embeddings through the Jina API."""

    EMBEDDING_URL = "https://api.jina.ai/v1/embeddings"
    MODEL = "jina-embeddings-v2-base-en"
    DIMENSION = 768

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("JINA_API_KEY")
        if not self.api_key:
            raise ValueError("JINA_API_KEY is not configured.")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def generate_embedding(self, text: str) -> list[float]:
        """Generate an embedding for one query or document string."""
        return self.generate_embeddings_batch([text])[0]

    def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of document chunks."""
        if not texts:
            return []

        response = requests.post(
            self.EMBEDDING_URL,
            headers=self.headers,
            json={"input": texts, "model": self.MODEL},
            timeout=30,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Jina embedding error: {response.status_code} - {response.text}"
            )

        data = sorted(response.json()["data"], key=lambda item: item["index"])
        return [item["embedding"] for item in data]
