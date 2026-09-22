# src/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API keys
    groq_api_key: str

    # Models
    embedding_model: str = "BAAI/bge-large-en-v1.5"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    generation_model: str = "openai/gpt-oss-20b"

    # Retrieval tuning
    hybrid_top_k: int = 10       # how many candidates each of vector/BM25 search returns
    rerank_top_k: int = 5        # how many final chunks go to the LLM
    rrf_k: int = 60              # RRF damping constant

    # Generation
    max_tokens: int = 1024

    # Storage
    chroma_persist_path: str = "./chroma_db"

    class Config:
        env_file = ".env"

settings = Settings()