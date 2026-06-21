from app.services.ai_models import reranker_model

def rerank(query, chunks, top_k=5):

    pairs = []
    # print(chunks)
    for chunk in chunks:
        pairs.append((query, chunk))
    scores = reranker_model.predict(pairs)
    scored_chunks = list(zip(chunks, scores))
    # print(scores)
    scored_chunks.sort(
        key=lambda x: x[1],
        reverse=True
    )

    top_chunks = [
        chunk
        for chunk, score in scored_chunks[:top_k]
    ]
    return top_chunks