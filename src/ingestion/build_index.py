# src/ingestion/build_index.py
import shutil
import sys

from src.config import settings
from src.ingestion.indexer import collect_chunks
from src.ingestion.embedder import Embedder
from src.ingestion.storage import VectorStore

BATCH = 500


def main(repo_path: str):
    shutil.rmtree(settings.chroma_persist_path, ignore_errors=True)

    records = collect_chunks(repo_path)
    print(f"Collected {len(records)} chunks from {repo_path}")

    texts = [r["text"] for r in records]
    vectors = Embedder().embed_texts(texts)

    store = VectorStore()
    for i in range(0, len(records), BATCH):
        batch = records[i:i + BATCH]
        store.add_chunks(
            ids=[r["id"] for r in batch],
            texts=[r["text"] for r in batch],
            embeddings=vectors[i:i + BATCH],
            metadatas=[r["meta"] for r in batch],
        )

    print(f"Done. Indexed {len(records)} chunks into {settings.chroma_persist_path}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "test-repo")