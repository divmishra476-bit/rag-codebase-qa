# test_reranker.py
from src.ingestion.loader import load_repo_files
from src.ingestion.chunker import chunk_python_file
from src.ingestion.embedder import Embedder
from src.ingestion.storage import VectorStore, KeywordStore
from src.retrieval.hybrid import reciprocal_rank_fusion
from src.retrieval.reranker import Reranker

files = load_repo_files("test-repo")
code_files = [f for f in files if f.file_type == "code"]
target = next(f for f in code_files if "_client" in f.path)
chunks = chunk_python_file(target.path, target.content)

texts = [c.content for c in chunks]
ids = [f"{c.file_path}:{c.start_line}" for c in chunks]
metadatas = [{"file_path": c.file_path, "chunk_type": c.chunk_type, "name": c.name} for c in chunks]

# build a lookup so we can get chunk text back from its id later
id_to_text = dict(zip(ids, texts))
id_to_meta = dict(zip(ids, metadatas))

embedder = Embedder()
vectors = embedder.embed_texts(texts)

vector_store = VectorStore()
vector_store.add_chunks(ids, texts, vectors, metadatas)
keyword_store = KeywordStore(texts, ids)

query = "how do I make an HTTP request"
query_vector = embedder.embed_texts([query])[0]

vector_ids = vector_store.query(query_vector, top_k=10)["ids"][0]
keyword_ids = [doc_id for doc_id, score in keyword_store.query(query, top_k=10)]

merged = reciprocal_rank_fusion(vector_ids, keyword_ids)
top_merged_ids = [doc_id for doc_id, score in merged[:10]]

# build candidate dicts with actual text, ready for reranking
candidates = [
    {"id": doc_id, "text": id_to_text[doc_id], "meta": id_to_meta[doc_id]}
    for doc_id in top_merged_ids
]

reranker = Reranker()
final_results = reranker.rerank(query, candidates, top_k=5)

print(f"Final re-ranked top 5 for '{query}':\n")
for r in final_results:
    print(f"  {r['id']} — {r['meta']['name']} — rerank score {r['rerank_score']:.4f}")