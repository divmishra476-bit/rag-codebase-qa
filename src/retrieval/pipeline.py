# src/retrieval/pipeline.py
from src.retrieval.hybrid import reciprocal_rank_fusion
from src.retrieval.reranker import Reranker

def retrieve(query: str, embedder, vector_store, keyword_store, id_to_text: dict, id_to_meta: dict, reranker: Reranker, top_k: int = 5) -> list[str]:
    """Full retrieval pipeline: hybrid search -> RRF -> rerank. Returns chunk IDs only."""

    query_vector = embedder.embed_texts([query])[0]

    vector_ids = vector_store.query(query_vector, top_k=10)["ids"][0]
    keyword_ids = [doc_id for doc_id, score in keyword_store.query(query, top_k=10)]

    merged = reciprocal_rank_fusion(vector_ids, keyword_ids)
    top_merged_ids = [doc_id for doc_id, score in merged[:10]]

    candidates = [
        {"id": doc_id, "text": id_to_text[doc_id], "meta": id_to_meta[doc_id]}
        for doc_id in top_merged_ids
    ]

    reranked = reranker.rerank(query, candidates, top_k=top_k)

    return [r["id"] for r in reranked]