from sentence_transformers import CrossEncoder

model = CrossEncoder(
    'cross-encoder/ms-marco-MiniLM-L-6-v2'
)

def rerank(query, chunks, top_k=5):

    pairs = []

    for chunk in chunks:
        pairs.append((query, chunk))
    scores = model.predict(pairs)
    scored_chunks = list(zip(chunks, scores))

    scored_chunks.sort(
        key=lambda x: x[1],
        reverse=True
    )

    top_chunks = [
        chunk
        for chunk, score in scored_chunks[:top_k]
    ]

    return top_chunks