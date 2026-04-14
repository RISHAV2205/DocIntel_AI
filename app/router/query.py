# main.py or routes/query.py

from fastapi import APIRouter, Depends
from app.embedding import get_embedding
from app.database import get_connection
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from openai import OpenAI

router = APIRouter()
client = OpenAI(api_key="YOUR_API_KEY")


@router.post("/query")
def query_rag(request: QueryRequest):
    
    # Step 1: Convert query to embedding
    query_embedding = get_embedding(request.query)

    # Step 2: Fetch embeddings from DB
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT chunk_text, embedding 
        FROM document_chunks
    """)
    
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    texts = []
    embeddings = []

    for text, emb in rows:
        texts.append(text)
        embeddings.append(emb)

    embeddings = np.array(embeddings)

    # Step 3: Similarity Search
    similarities = cosine_similarity([query_embedding], embeddings)[0]

    # Step 4: Get Top-K
    k = 3
    top_indices = similarities.argsort()[-k:][::-1]
    top_chunks = [texts[i] for i in top_indices]

    # Step 5: Build Context
    context = "\n\n".join(top_chunks)

    # Step 6: LLM Prompt
    prompt = f"""
    Answer strictly based on the context below.
    If the answer is not present, say "Not found".

    Context:
    {context}

    Question:
    {request.query}
    """

    # Step 7: Generate Answer
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    answer = response.choices[0].message.content

    return {
        "query": request.query,
        "answer": answer,
        "top_chunks": top_chunks  # optional (good for debugging)
    }