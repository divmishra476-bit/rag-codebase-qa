# src/api/main.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.ingestion.loader import load_repo_files
from src.ingestion.chunker import chunk_python_file
from src.ingestion.embedder import Embedder
from src.ingestion.storage import VectorStore, KeywordStore
from src.retrieval.reranker import Reranker
from src.retrieval.pipeline import retrieve
from src.generation.generator import Generator
from src.observability.tracer import Tracer

app = FastAPI(title="Codebase Q&A RAG API")

# Build the index once, when the server starts
files = load_repo_files("test-repo")
code_files = [f for f in files if f.file_type == "code"]
target = next(f for f in code_files if "_client" in f.path)
chunks = chunk_python_file(target.path, target.content)

texts = [c.content for c in chunks]
ids = [f"{c.file_path}:{c.start_line}" for c in chunks]
metadatas = [
    {"file_path": c.file_path, "chunk_type": c.chunk_type, "name": c.name,
     "start_line": c.start_line, "end_line": c.end_line}
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
generator = Generator()


class QueryRequest(BaseModel):
    question: str


@app.post("/ask")
def ask(request: QueryRequest):
    query = request.question
    tracer = Tracer(query)

    retrieved_ids = retrieve(query, embedder, vector_store, keyword_store, id_to_text, id_to_meta, reranker, tracer=tracer)
    retrieved_chunks = [
        {"id": doc_id, "text": id_to_text[doc_id], "meta": id_to_meta[doc_id]}
        for doc_id in retrieved_ids
    ]

    def generate():
        full_answer = ""
        for piece in generator.stream_answer(query, retrieved_chunks):
            full_answer += piece
            yield piece
        tracer.finish(retrieved_ids, full_answer)

    return StreamingResponse(generate(), media_type="text/plain")


@app.get("/health")
def health():
    return {"status": "ok"}