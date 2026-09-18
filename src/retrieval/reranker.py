# src/retrieval/reranker.py
from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
        """
        candidates: list of dicts, each must have a 'text' key.
        Returns the same dicts, re-sorted by relevance, trimmed to top_k.
        """
        pairs = [[query, c["text"]] for c in candidates]
        scores = self.model.predict(pairs)

        for c, score in zip(candidates, scores):
            c["rerank_score"] = float(score)

        reranked = sorted(candidates, key=lambda c: c["rerank_score"], reverse=True)
        return reranked[:top_k]