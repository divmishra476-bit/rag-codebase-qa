# tests/test_embedder.py
from src.ingestion.embedder import Embedder

def test_embed_texts_returns_correct_number_of_vectors():
    embedder = Embedder()
    texts = ["hello world", "how do I make a request"]
    vectors = embedder.embed_texts(texts)
    assert len(vectors) == 2

def test_embed_texts_returns_vectors_of_consistent_length():
    embedder = Embedder()
    texts = ["short text", "a slightly longer piece of text here"]
    vectors = embedder.embed_texts(texts)
    assert len(vectors[0]) == len(vectors[1])
    assert len(vectors[0]) > 0