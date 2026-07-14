import json

from app.database import session_local
from app.services.retrieval_service import retrieve_chunks

from app.evaluation.retreival_metrics import (
    recall_at_k,
    precision_at_k,
    context_recall,
    mrr_score,
    hit_rate
)

# -----------------------------
# Load Evaluation Dataset
# -----------------------------
with open(
    "app/evaluation/evaluation_dataset.json",
    "r",
    encoding="utf-8"
) as f:
    test_cases = json.load(f)

db = session_local()

# -----------------------------
# Overall Metrics
# -----------------------------
total_recall = 0
total_precision = 0
total_context_recall = 0
total_mrr = 0
total_hit_rate = 0

k = 3

print("\n================ Retrieval Evaluation ================\n")

# -----------------------------
# Evaluate Every Question
# -----------------------------
for idx, test in enumerate(test_cases, start=1):

    question = test["question"]
    ground_truth_keywords = test["ground_truth_keywords"]

    retrieved_chunks = retrieve_chunks(
        question=question,
        db=db,
        user_id=5,
        top_k=10,
    )

    recall = recall_at_k(
        retrieved_chunks,
        ground_truth_keywords
    )

    precision = precision_at_k(
        retrieved_chunks,
        ground_truth_keywords,
        k
    )

    ctx_recall = context_recall(
        retrieved_chunks,
        ground_truth_keywords
    )

    mrr = mrr_score(
        retrieved_chunks,
        ground_truth_keywords
    )

    hit = hit_rate(
        retrieved_chunks,
        ground_truth_keywords
    )

    total_recall += recall
    total_precision += precision
    total_context_recall += ctx_recall
    total_mrr += mrr
    total_hit_rate += hit

    # print(f"Question {idx}: {question}")
    # print(f"Recall@{k}:       {recall:.2f}")
    # print(f"Precision@{k}:    {precision:.2f}")
    # print(f"Context Recall:   {ctx_recall:.2f}")
    # print(f"MRR:              {mrr:.2f}")
    # print(f"Hit Rate:         {hit:.2f}")

    # print("\nRetrieved Chunks\n")

    # for i, chunk in enumerate(retrieved_chunks, start=1):
    #     print(f"Chunk {i}:")
    #     print(chunk[:250])
    #     print()

    # print("-" * 80)

# -----------------------------
# Average Metrics
# -----------------------------
n = len(test_cases)

print("\n================ Average Retrieval Metrics ================\n")

print(f"Recall@{k}       : {total_recall / n:.4f}")
print(f"Precision@{k}    : {total_precision / n:.4f}")
print(f"Context Recall   : {total_context_recall / n:.4f}")
print(f"MRR              : {total_mrr / n:.4f}")
print(f"Hit Rate         : {total_hit_rate / n:.4f}")

print("\n===========================================================")