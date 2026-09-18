# test_storage.py
from src.ingestion.loader import load_repo_files
from src.ingestion.chunker import chunk_python_file
from src.ingestion.embedder import Embedder
from src.ingestion.storage import VectorStore, KeywordStore

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

print(f"Stored {len(chunks)} chunks in both vector and keyword stores")

# Try a real semantic query
query = "how do I make an HTTP request"
query_vector = embedder.embed_texts([query])[0]
results = vector_store.query(query_vector, top_k=3)
print(f"\nTop vector search results for '{query}':")
for doc_id, meta in zip(results["ids"][0], results["metadatas"][0]):
    print(f"  {doc_id} — {meta['name']} ({meta['chunk_type']})")

# Try the same query with BM25
keyword_results = keyword_store.query(query, top_k=3)
print(f"\nTop BM25 results for '{query}':")
for doc_id, score in keyword_results:
    print(f"  {doc_id} — score {score:.2f}")