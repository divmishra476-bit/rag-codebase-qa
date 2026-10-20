# test_eval.py
from src.ingestion.embedder import Embedder
from src.ingestion.storage import VectorStore, KeywordStore
from src.retrieval.reranker import Reranker
from src.retrieval.pipeline import retrieve
from eval.eval_set_v2 import NEW_SET as EVAL_SET
from eval.run_eval import run_retrieval_eval

# Read the saved index (built by build_index.py), do NOT rebuild it here
vector_store = VectorStore()
ids, texts, metadatas = vector_store.get_all()
print(f"Loaded {len(ids)} chunks from saved index")

id_to_text = dict(zip(ids, texts))
id_to_meta = dict(zip(ids, metadatas))
keyword_store = KeywordStore(texts, ids)

embedder = Embedder()
reranker = Reranker()


def retrieve_fn(query: str) -> list[str]:
    return retrieve(query, embedder, vector_store, keyword_store, id_to_text, id_to_meta, reranker)


results = run_retrieval_eval(EVAL_SET, retrieve_fn)

print(f"\n=== EVAL RESULTS (full repo index) ===")
print(f"Recall@5: {results['recall_at_k']:.2%}")
print(f"Hits: {results['hits']}/{results['total_cases']}\n")

for r in results["details"]:
    status = "HIT " if r["hit"] else "MISS"
    print(f"{status} - '{r['query']}'")
    print(f"   expected: {r['expected']}")
    print(f"   got top 5: {r['retrieved_top_5']}\n")