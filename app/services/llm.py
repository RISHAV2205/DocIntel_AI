import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://router.huggingface.co/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}



def generate_answer(prompt):
    payload = {
        "model": "deepseek-ai/DeepSeek-V4-Flash",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 300,
        "temperature": 0.5
    }
    response = requests.post(
        API_URL,
        headers=headers,
        json=payload
    )

    print("STATUS:", response.status_code)
    print("RAW RESPONSE:", response.text)

    if response.status_code != 200:
        return "LLM Error"

    result = response.json()

    answer = result["choices"][0]["message"]["content"]

    return answer


# NEW — streaming version
def generate_answer_stream(prompt: str):
    """
    Generator function — yields one token at a time.
    HuggingFace router supports OpenAI-compatible SSE streaming.
    """
    payload = {
        "model": "deepseek-ai/DeepSeek-V4-Flash",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100,
        "temperature": 0.5,
        "stream": True   # this is the only change in payload
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        stream=True      # tell requests to not download all at once
    )

    if response.status_code != 200:
        yield "LLM Error"
        return

    # HuggingFace returns SSE lines like:
    # data: {"choices": [{"delta": {"content": "Hello"}}]}
    # data: [DONE]

    for line in response.iter_lines():
        if not line:
            continue

        # decode bytes to string
        line = line.decode("utf-8")

        # skip empty or non-data lines
        if not line.startswith("data:"):
            continue

        # remove "data: " prefix
        data_str = line[len("data:"):].strip()

        # stream is done
        if data_str == "[DONE]":
            break

        try:
            data = json.loads(data_str)
            if not data.get("choices"):
                continue

            token = data["choices"][0]["delta"].get("content", "")
            if token:
                yield token
        except (json.JSONDecodeError, KeyError):
            continue