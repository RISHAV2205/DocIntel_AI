from sqlalchemy import text
from app.services.embedding import generate_embedding
from rank_bm25 import BM25Okapi


def tokenize(text: str) -> list[str]:
    """
    Simple tokenizer — lowercase and split by whitespace.
    BM25 works on token lists not raw strings.
    "Machine Learning" → ["machine", "learning"]
    """
    return text.lower().split()


def retrieve_chunks(
    question: str,
    db,
    user_id: int,
    top_k: int = 10,      # candidates from each search method
    final_k: int = 5      # final chunks after fusion
) -> list[str]:

    # ─────────────────────────────────────────
    # STEP 1 — Fetch ALL chunks for this user
    # ─────────────────────────────────────────
    # We need all chunks to build BM25 index
    # pgvector handles its own indexing internally
    rows = db.execute(
        text("""
            SELECT dc.id, dc.chunk_text
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            WHERE d.owner_id = :user_id
        """),
        {"user_id": user_id}
    ).fetchall()

    if not rows:
        return []

    # separate IDs and texts
    chunk_ids = [row[0] for row in rows]
    chunk_texts = [row[1] for row in rows]

    # ─────────────────────────────────────────
    # STEP 2 — Vector Search via pgvector
    # ─────────────────────────────────────────
    # Embed the query using Jina API
    # Then find top_k most similar chunks using cosine distance
    # <=> is pgvector cosine distance operator
    # Lower distance = more similar
    query_embedding = generate_embedding(question)

    vector_rows = db.execute(
        text("""
            SELECT dc.id, dc.chunk_text
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            WHERE d.owner_id = :user_id
            ORDER BY dc.embedding <=> CAST(:query_embedding AS vector)
            LIMIT :limit
        """),
        {
            "user_id": user_id,
            "query_embedding": str(query_embedding),
            "limit": top_k
        }
    ).fetchall()

    # map chunk_id → rank position in vector results
    # rank 0 = most similar, rank 1 = second most similar, etc.
    vector_ranks = {}
    for rank, row in enumerate(vector_rows):
        vector_ranks[row[0]] = rank

    # ─────────────────────────────────────────
    # STEP 3 — BM25 Keyword Search
    # ─────────────────────────────────────────
    # Build BM25 index from all chunk texts
    # BM25 scores based on:
    # - How many times query words appear in chunk
    # - How rare those words are across all chunks
    # - Length of the chunk

    tokenized_corpus = [tokenize(text) for text in chunk_texts]
    bm25 = BM25Okapi(tokenized_corpus)

    # score every chunk against the query
    query_tokens = tokenize(question)
    bm25_scores = bm25.get_scores(query_tokens)

    # get top_k indices sorted by BM25 score (highest first)
    import numpy as np
    bm25_top_indices = np.argsort(bm25_scores)[::-1][:top_k]

    # map chunk_id → rank position in BM25 results
    bm25_ranks = {}
    for rank, idx in enumerate(bm25_top_indices):
        chunk_id = chunk_ids[idx]
        bm25_ranks[chunk_id] = rank

    # ─────────────────────────────────────────
    # STEP 4 — RRF Fusion
    # ─────────────────────────────────────────
    # Reciprocal Rank Fusion combines both ranked lists
    # Formula: score = 1/(rank + K) for each list
    # K=60 is standard constant that prevents top ranks
    # from dominating too much
    #
    # Example:
    # Chunk A → rank 0 in vector, rank 2 in BM25
    #   score = 1/(0+60) + 1/(2+60) = 0.0166 + 0.0161 = 0.0327
    #
    # Chunk B → rank 1 in vector, not in BM25
    #   score = 1/(1+60) + 0 = 0.0163
    #
    # Chunk A scores higher because it appeared in BOTH lists

    K = 60
    all_chunk_ids = set(vector_ranks.keys()) | set(bm25_ranks.keys())

    rrf_scores = {}
    for chunk_id in all_chunk_ids:
        score = 0.0
        if chunk_id in vector_ranks:
            score += 1.0 / (K + vector_ranks[chunk_id] + 1)
        if chunk_id in bm25_ranks:
            score += 1.0 / (K + bm25_ranks[chunk_id] + 1)
        rrf_scores[chunk_id] = score

    # sort all chunks by RRF score descending
    sorted_chunk_ids = sorted(
        rrf_scores.keys(),
        key=lambda cid: rrf_scores[cid],
        reverse=True
    )[:final_k]

    # ─────────────────────────────────────────
    # STEP 5 — Return Final Chunks
    # ─────────────────────────────────────────
    # Build lookup map for quick access
    chunk_map = {chunk_ids[i]: chunk_texts[i] for i in range(len(chunk_ids))}

    final_chunks = [
        chunk_map[cid]
        for cid in sorted_chunk_ids
        if cid in chunk_map
    ]

    return final_chunks