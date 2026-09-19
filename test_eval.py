# test_eval.py
from src.ingestion.loader import load_repo_files
from src.ingestion.chunker import chunk_python_file
from src.ingestion.embedder import Embedder
from src.ingestion.storage import VectorStore, KeywordStore
from src.retrieval.reranker import Reranker
from src.retrieval.pipeline import retrieve
from eval.eval_set import EVAL_SET
from eval.run_eval import run_retrieval_eval

files = load_repo_files("test-repo")
code_files = [f for f in files if f.file_type == "code"]
target = next(f for f in code_files if "_client" in f.path)
chunks = chunk_python_file(target.path, target.content)

texts = [c.content for c in chunks]
ids = [f"{c.file_path}:{c.start_line}" for c in chunks]
metadatas = [{"file_path": c.file_path, "chunk_type": c.chunk_type, "name": c.name} for c in chunks]

id_to_text = dict(zip(ids, texts))
id_to_meta = dict(zip(ids, metadatas))

embedder = Embedder()
vectors = embedder.embed_texts(texts)  # embed the enriched text

vector_store = VectorStore()
vector_store.add_chunks(ids, texts, vectors, metadatas)  # store enriched text as the searchable "document"
keyword_store = KeywordStore(texts, ids)  # BM25 also indexes enriched text
reranker = Reranker()

def retrieve_fn(query: str) -> list[str]:
    return retrieve(query, embedder, vector_store, keyword_store, id_to_text, id_to_meta, reranker)

results = run_retrieval_eval(EVAL_SET, retrieve_fn)

print(f"\n=== EVAL RESULTS (with chunk enrichment) ===")
print(f"Recall@5: {results['recall_at_k']:.2%}")
print(f"Hits: {results['hits']}/{results['total_cases']}\n")

for r in results["details"]:
    status = "✅ HIT" if r["hit"] else "❌ MISS"
    print(f"{status} — '{r['query']}'")
    print(f"   expected: {r['expected']}")
    print(f"   got top 5: {r['retrieved_top_5']}\n")