# test_hybrid.py
from src.ingestion.loader import load_repo_files
from src.ingestion.chunker import chunk_python_file
from src.ingestion.embedder import Embedder
from src.ingestion.storage import VectorStore, KeywordStore
from src.retrieval.hybrid import reciprocal_rank_fusion

files = load_repo_files("test-repo")
code_files = [f for f in files if f.file_type == "code"]
target = next(f for f in code_files if "_client" in f.path)
chunks = chunk_python_file(target.path, target.content)

texts = [c.content for c in chunks]
ids = [f"{c.file_path}:{c.start_line}" for c in chunks]
metadatas = [{"file_path": c.file_path, "chunk_type": c.chunk_type, "name": c.name} for c in chunks]

embedder = Embedder()
vectors = embedder.embed_texts(texts)

vector_store = VectorStore()
vector_store.add_chunks(ids, texts, vectors, metadatas)
keyword_store = KeywordStore(texts, ids)

query = "how do I make an HTTP request"
query_vector = embedder.embed_texts([query])[0]

vector_result = vector_store.query(query_vector, top_k=10)
vector_ids = vector_result["ids"][0]

keyword_result = keyword_store.query(query, top_k=10)
keyword_ids = [doc_id for doc_id, score in keyword_result]

merged = reciprocal_rank_fusion(vector_ids, keyword_ids)

print("Merged (hybrid) ranking:")
for doc_id, score in merged[:10]:
    print(f"  {doc_id} — combined score {score:.4f}")