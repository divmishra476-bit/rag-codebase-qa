from sentence_transformers import SentenceTransformer
from src.config import settings

class Embedder:
    def __init__(self, model_name: str = None):
        self.model = SentenceTransformer(model_name or settings.embedding_model)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()