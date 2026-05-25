import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://router.huggingface.co/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}


# def generate_answer(query, chunks):

#     context = "\n\n".join(chunks)
#     prompt = f"""
#     Answer the question only using the provided context.

#     Context:
#     {context}

#     Question:
#     {query}
#     """

#     payload = {
#         "model": "deepseek-ai/DeepSeek-V4-Flash",
        
#         "messages": [
#             {
#                 "role": "system",
#                 "content": "You are a helpful AI document assistant."
#             },
#             {
#                 "role": "user",
#                 "content": prompt
#             }
#         ],

#         "max_tokens": 200,
#         "temperature": 0.5
#     }

#     response = requests.post(
#         API_URL,
#         headers=headers,
#         json=payload
#     )

#     print("STATUS:", response.status_code)
#     print("RAW RESPONSE:", response.text)

#     if response.status_code != 200:
#         return {
#             "error": response.text
#         }

#     result = response.json()

#     return result["choices"][0]["message"]["content"]


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