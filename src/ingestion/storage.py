# src/ingestion/storage.py
import chromadb
from rank_bm25 import BM25Okapi

class VectorStore:
    """Wraps ChromaDB — stores chunk text + embeddings for semantic search."""

    def __init__(self, collection_name: str = "codebase_chunks", persist_path: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_chunks(self, ids: list[str], texts: list[str], embeddings: list[list[float]], metadatas: list[dict]):
        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def query(self, query_embedding: list[float], top_k: int = 10):
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )
class KeywordStore:
    """Wraps BM25 — stores tokenized chunk text for keyword search."""

    def __init__(self, texts: list[str], ids: list[str]):
        self.ids = ids
        self.tokenized_texts = [text.lower().split() for text in texts]
        self.bm25 = BM25Okapi(self.tokenized_texts)

    def query(self, query_text: str, top_k: int = 10):
        tokenized_query = query_text.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        ranked = sorted(zip(self.ids, scores), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]