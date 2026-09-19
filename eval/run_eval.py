# eval/run_eval.py

def recall_at_k(retrieved_ids: list[str], expected_ids: list[str]) -> bool:
    return any(exp_id in retrieved_ids for exp_id in expected_ids)


def run_retrieval_eval(eval_set, retrieve_fn) -> dict:
    results = []
    hits = 0

    for case in eval_set:
        query = case["query"]
        expected = case["expected_chunk_ids"]

        retrieved = retrieve_fn(query)
        hit = recall_at_k(retrieved, expected)
        hits += hit

        results.append({
            "query": query,
            "expected": expected,
            "retrieved_top_5": retrieved[:5],
            "hit": hit,
        })

    total = len(results)
    recall = hits / total if total > 0 else 0

    return {
        "recall_at_k": recall,
        "total_cases": total,
        "hits": hits,
        "details": results,
    }