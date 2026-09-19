from src.ingestion.loader import load_repo_files
from src.ingestion.chunker import chunk_python_file
from src.ingestion.embedder import Embedder
from src.ingestion.storage import VectorStore, KeywordStore
from src.retrieval.reranker import Reranker
from src.retrieval.pipeline import retrieve
from src.generation.prompt_builder import build_prompt, SYSTEM_PROMPT

files = load_repo_files("test-repo")
code_files = [f for f in files if f.file_type == "code"]
target = next(f for f in code_files if "_client" in f.path)
chunks = chunk_python_file(target.path, target.content)

texts = [c.content for c in chunks]
ids = [f"{c.file_path}:{c.start_line}" for c in chunks]
metadatas = [
    {
        "file_path": c.file_path,
        "chunk_type": c.chunk_type,
        "name": c.name,
        "start_line": c.start_line,
        "end_line": c.end_line,
    }
    for c in chunks
]
id_to_text = dict(zip(ids, texts))
id_to_meta = dict(zip(ids, metadatas))

embedder = Embedder()
vectors = embedder.embed_texts(texts)
vector_store = VectorStore()
vector_store.add_chunks(ids, texts, vectors, metadatas)
keyword_store = KeywordStore(texts, ids)
reranker = Reranker()

query = "how do I make an HTTP request"
retrieved_ids = retrieve(query, embedder, vector_store, keyword_store, id_to_text, id_to_meta, reranker)

retrieved_chunks = [
    {"id": doc_id, "text": id_to_text[doc_id], "meta": id_to_meta[doc_id]}
    for doc_id in retrieved_ids
]

prompt = build_prompt(query, retrieved_chunks)
print("=== SYSTEM PROMPT ===")
print(SYSTEM_PROMPT)
print("\n=== USER PROMPT ===")
print(prompt)