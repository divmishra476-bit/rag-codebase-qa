from src.ingestion.embedder import Embedder

embedder = Embedder()

texts = [
    "def create_user(email, password): ...",
    "how do I register a new account",
    "The weather is nice today",
]

vectors = embedder.embed_texts(texts)

print(f"Got {len(vectors)} vectors")
print(f"Each vector has {len(vectors[0])} numbers")
print(f"First few numbers: {vectors[0][:5]}")