from llm import generate_answer

chunks = [
    "AI Powered Document Analyzer Hub uses FastAPI and PostgreSQL.",
    "Embeddings are generated using sentence transformers."
]

query = "how computr are generated"

response = generate_answer(query, chunks)

print(response)