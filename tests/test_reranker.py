from src.retrieval.reranker import Reranker

def test_rerank_returns_top_k_results():
    reranker = Reranker()
    candidates = [
        {"id": "1", "text": "def close(self): pass"},
        {"id": "2", "text": "def request(self, method, url): pass"},
    ]
    results = reranker.rerank("how do I make a request", candidates, top_k=1)
    assert len(results) == 1
    assert "rerank_score" in results[0]