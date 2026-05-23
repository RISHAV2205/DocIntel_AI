import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
def similarity_search(rows,query_embedding):
    texts = []
    embeddings = []
    for row in rows:
        texts.append(row[0])
        embeddings.append(row[1])
    embeddings = np.array(embeddings)
    # Step 3: Compute similarity
    similarities = cosine_similarity([query_embedding], embeddings)[0]
    # Step 4: Get Top-K
    k = 20
    top_indices = similarities.argsort()[-k:][::-1]

    top_chunks = [texts[i] for i in top_indices]
    top_scores = [float(similarities[i]) for i in top_indices]
    
    return top_chunks,top_scores
