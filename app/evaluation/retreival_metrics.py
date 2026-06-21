def recall_at_k(
    retrieved_chunks,
    expected_keyword
):
    for chunk in retrieved_chunks:
        if expected_keyword.lower() in chunk.lower():
            return 1

    return 0

def mrr_score(
    retrieved_chunks,
    expected_keyword
):
    for idx, chunk in enumerate(
        retrieved_chunks
    ):
        if expected_keyword.lower() in chunk.lower():
            return 1 / (idx + 1)
    return 0

def hit_rate(
    retrieved_chunks,
    expected_keyword
):
    return recall_at_k(
        retrieved_chunks,
        expected_keyword
    )