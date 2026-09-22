from sentence_transformers import CrossEncoder
from src.config import settings

class Reranker:
    def __init__(self, model_name: str = None):
        self.model = CrossEncoder(model_name or settings.reranker_model)

    def rerank(self, query: str, candidates: list[dict], top_k: int = None) -> list[dict]:
        top_k = top_k or settings.rerank_top_k
        pairs = [[query, c["text"]] for c in candidates]
        scores = self.model.predict(pairs)
        for c, score in zip(candidates, scores):
            c["rerank_score"] = float(score)
        reranked = sorted(candidates, key=lambda c: c["rerank_score"], reverse=True)
        return reranked[:top_k]