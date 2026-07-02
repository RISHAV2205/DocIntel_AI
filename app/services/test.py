import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = (
    "https://api-inference.huggingface.co/models/"
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

payload = {
    "inputs": {
        "source_sentence": "What is FastAPI?",
        "sentences": [
            "FastAPI is a Python web framework.",
            "Cats are beautiful animals.",
            "FastAPI supports asynchronous programming."
        ]
    }
}

response = requests.post(
    API_URL,
    headers=headers,
    json=payload,
    timeout=60
)

print("Status:", response.status_code)
print(response.text)