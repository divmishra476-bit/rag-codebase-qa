# src/api/main.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.ingestion.embedder import Embedder
from src.ingestion.storage import VectorStore, KeywordStore
from src.retrieval.reranker import Reranker
from src.retrieval.pipeline import retrieve
from src.generation.generator import Generator
from src.observability.tracer import Tracer

app = FastAPI(title="Codebase Q&A RAG API")

# Load the saved index (built once with: python -m src.ingestion.build_index test-repo)
vector_store = VectorStore()
ids, texts, metadatas = vector_store.get_all()
if not ids:
    raise RuntimeError("Index is empty. Run: python -m src.ingestion.build_index test-repo")

id_to_text = dict(zip(ids, texts))
id_to_meta = dict(zip(ids, metadatas))
keyword_store = KeywordStore(texts, ids)

embedder = Embedder()
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