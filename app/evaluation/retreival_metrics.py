def _is_relevant(chunk: str, ground_truth_keywords: list[str]) -> bool:
    """
    Returns True if any ground truth keyword is present
    inside the retrieved chunk.
    """

    chunk = chunk.lower()

    return any(
        keyword.lower() in chunk
        for keyword in ground_truth_keywords
    )


# ---------------------------------------------------
# Recall@K
# ---------------------------------------------------

def recall_at_k(
    retrieved_chunks,
    ground_truth_keywords,
    k=3,
):
    """
    Binary Recall@K

    Returns:
        1 if at least one relevant chunk is retrieved
        else 0
    """

    retrieved = retrieved_chunks[:k]

    for chunk in retrieved:
        if _is_relevant(chunk, ground_truth_keywords):
            return 1

    return 0


# ---------------------------------------------------
# Precision@K
# ---------------------------------------------------

def precision_at_k(
    retrieved_chunks,
    ground_truth_keywords,
    k=3,
):
    """
    Precision@K

    Precision =
    Relevant Retrieved / K
    """

    retrieved = retrieved_chunks[:k]

    relevant = sum(
        _is_relevant(chunk, ground_truth_keywords)
        for chunk in retrieved
    )

    return relevant / k if k else 0


# ---------------------------------------------------
# MRR
# ---------------------------------------------------

def mrr_score(
    retrieved_chunks,
    ground_truth_keywords,
):
    """
    Mean Reciprocal Rank

    Returns reciprocal rank of first relevant chunk.
    """

    for idx, chunk in enumerate(retrieved_chunks):

        if _is_relevant(chunk, ground_truth_keywords):

            return 1 / (idx + 1)

    return 0


# ---------------------------------------------------
# Hit Rate
# ---------------------------------------------------

def hit_rate(
    retrieved_chunks,
    ground_truth_keywords,
    k=3,
):
    """
    Hit Rate

    Returns 1 if at least one relevant chunk exists.
    """

    return recall_at_k(
        retrieved_chunks,
        ground_truth_keywords,
        k,
    )


# ---------------------------------------------------
# Context Recall
# ---------------------------------------------------

def context_recall(
    retrieved_chunks,
    ground_truth_keywords,
):
    """
    Context Recall

    Percentage of ground-truth concepts
    covered by retrieved chunks.
    """

    if not ground_truth_keywords:
        return 0

    retrieved_text = " ".join(
        chunk.lower()
        for chunk in retrieved_chunks
    )

    found = sum(
        keyword.lower() in retrieved_text
        for keyword in ground_truth_keywords
    )

    return found / len(ground_truth_keywords)