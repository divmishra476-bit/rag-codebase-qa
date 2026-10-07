from src.retrieval.hybrid import reciprocal_rank_fusion

def test_rrf_ranks_items_in_both_lists_higher():
    vector_results = ["a", "b", "c"]
    keyword_results = ["b", "a", "d"]
    merged = reciprocal_rank_fusion(vector_results, keyword_results)
    merged_ids = [doc_id for doc_id, score in merged]
    assert merged_ids.index("a") < merged_ids.index("c")
    assert merged_ids.index("b") < merged_ids.index("d")

def test_rrf_includes_all_unique_ids():
    merged = reciprocal_rank_fusion(["a", "b"], ["c", "d"])
    merged_ids = {doc_id for doc_id, score in merged}
    assert merged_ids == {"a", "b", "c", "d"}

def test_rrf_handles_empty_lists():
    merged = reciprocal_rank_fusion([], [])
    assert merged == []