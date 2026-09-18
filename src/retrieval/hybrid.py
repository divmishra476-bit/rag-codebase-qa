# src/retrieval/hybrid.py

def reciprocal_rank_fusion(
    vector_results: list[str],
    keyword_results: list[str],
    k: int = 60,
) -> list[tuple[str, float]]:
    """
    Merge two ranked lists of chunk IDs into one combined ranking.
    vector_results and keyword_results are lists of chunk IDs, best match first.
    """
    scores = {}

    for rank, doc_id in enumerate(vector_results):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)

    for rank, doc_id in enumerate(keyword_results):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)

    merged = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return merged