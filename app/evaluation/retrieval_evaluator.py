import json

with open(
    "app/evaluation/evaluation_dataset.json",
    "r",
    encoding="utf-8"
) as f:
    test_cases = json.load(f)
    
# print(test_cases)
from app.database import session_local
from app.services.retrieval_service import retrieve_chunks
from app.evaluation.retreival_metrics import (
    recall_at_k,
    mrr_score,
    hit_rate
)

db = session_local()

total_recall = 0
total_mrr = 0
total_hit_rate = 0

for test in test_cases:
    question = test["question"]
    expected_keyword = test["expected_chunk_keyword"]

    retrieved_chunks = retrieve_chunks(
        question=question,
        db=db,
        user_id=5
    )
    # print("retrieve chunks",retrieved_chunks)
    
    total_recall += recall_at_k(
        retrieved_chunks,
        expected_keyword
    )

    total_mrr += mrr_score(
        retrieved_chunks,
        expected_keyword
    )

    total_hit_rate += hit_rate(
        retrieved_chunks,
        expected_keyword
    )
    
    
total_questions = len(test_cases)

print("\n===== Retrieval Evaluation =====")

print(
    f"Recall@K: {total_recall / total_questions:.4f}"
)

print(
    f"MRR: {total_mrr / total_questions:.4f}"
)

print(
    f"Hit Rate: {total_hit_rate / total_questions:.4f}"
)


# Step 6: Add debugging (recommended)

# Before calculating metrics, print retrieved chunks:
print("\nQuestion:", question)

for idx, chunk in enumerate(retrieved_chunks):
    print(f"\nChunk {idx+1}:")
    print(chunk[:200])