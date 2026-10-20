# rag-codebase-qa

A Retrieval-Augmented Generation (RAG) system that answers natural-language questions about a software repository (code and docs), with file and line citations. Built from scratch, with no LangChain or other orchestration framework, so every retrieval and generation decision is implemented and measured directly.

Target repository for development and evaluation: [httpx](https://github.com/encode/httpx) (978 chunks of code and docs).

## What it does

Ask "how does httpx handle authentication" and get a streamed answer grounded in the repository's own source and documentation, citing files and line ranges, instead of the LLM's general training knowledge.

## Architecture

```text
Ingestion (run once, build_index.py)
  Repo files -> Loader -> Chunker (AST for code, headings for docs)
             -> Embedder -> ChromaDB (vectors) + BM25 (keywords)

Query (per request, FastAPI /ask)
  Question -> Hybrid search (vector + BM25) -> Reciprocal Rank Fusion
           -> Cross-encoder re-ranking -> Grounded prompt
           -> LLM (streamed) -> Answer with citations
           -> Per-request trace (latency per stage, chunk IDs)
```

## Features

- AST-based chunking of Python code (functions, classes, methods) with line numbers
- Heading-based chunking of Markdown and reStructuredText docs
- Hybrid retrieval: dense vectors (ChromaDB) plus BM25, merged with Reciprocal Rank Fusion
- Cross-encoder re-ranking of the merged candidates
- Grounded prompt that tells the LLM to answer only from the retrieved chunks and cite file and lines
- Streaming answers over HTTP (FastAPI `StreamingResponse`)
- Per-request tracing: latency per stage, retrieved chunk IDs, answer length (JSON lines)
- Config via `.env` and `pydantic-settings`, no hardcoded secrets
- Pytest suite and GitHub Actions CI
- Retrieval evaluation with a pre-registered question set

## Evaluation

Retrieval is measured with **Recall@5**: is at least one correct chunk in the top 5 results? Evaluated on the full index (978 chunks of code and docs).

**Current result: 13/14 = 92.86% Recall@5** on `eval/eval_set_v2.py`.

The expected chunks were picked with plain keyword search (not the retriever) and committed to Git *before* the eval was run, so results could not influence the ground truth. With only 14 questions the 95% confidence interval is wide (roughly 69% to 99%).

The one miss: "what exceptions can httpx raise" returned `docs/exceptions.md:1` and `docs/quickstart.md:495`. Both arguably answer the question, but the ground truth listed only `docs/exceptions.md:40`. It is reported as a miss and left unchanged.

### Limitations of this number

- 12 of the 14 questions are answered by docs; only 2 test code retrieval, so code retrieval is under-tested.
- A known failure is not in this set: "how do I make an HTTP request" retrieves several docs chunks, and `Client.request` falls out of the top 5 on the full index (it was in the top 5 on the earlier single-file index).
- Ground truth is my judgement of what directly answers a question; borderline chunks were left out.
- Only retrieval is evaluated. Answer quality from the LLM is not systematically measured.

### History

- Single-module index (88 chunks, 6 questions): 83.33%.
- The same 6 questions on the full index: 50%. Reading the retrieved chunks showed two misses were stale ground truth (docs that directly answer the question were not in the index when the questions were written) and one was a real regression (above). The expected IDs for those two were widened after seeing results, so the later 5/6 figure is not used as evidence.
- Naive chunk enrichment (prepending a generic header to every chunk) dropped the single-module score from 83% to 50% and was reverted.
- Observed on the single-module index only (not re-checked on the full index): the cross-encoder sometimes ranked private methods (`_send_single_request`) above the public `Client.request`.

## Performance

One sample request on a CPU-only laptop: about 5.0 s end to end, of which re-ranking is about 2.3 s, query embedding about 0.5 s and hybrid search about 0.03 s. Re-ranking is the slowest retrieval stage. This is one measurement, not a benchmark.

## Key engineering decisions

- **AST-based code chunking**: splits at real function, class and method boundaries instead of fixed character counts, keeping complete code units and accurate line numbers for citation.
- **Hybrid search with Reciprocal Rank Fusion**: semantic search misses exact identifiers, and BM25 misses conceptual matches. RRF combines both rankings without one silently overriding the other.
- **Cross-encoder re-ranking**: re-scores the top candidates against the query. Costs latency (see Performance).
- **Index built once, loaded at startup**: embedding is slow on CPU, so `build_index.py` builds and saves the index and the API only loads it.
- **Config-driven**: models, retrieval parameters and API keys live in `.env` and `src/config.py`.
- **Structured request tracing**: every query logs per-stage latency and the retrieved chunk IDs for debugging.
- **No orchestration framework**: every component is implemented directly.

## Tech stack

Python 3.12, sentence-transformers (`BAAI/bge-large-en-v1.5`), ChromaDB, rank_bm25, cross-encoder (`ms-marco-MiniLM-L-6-v2`), FastAPI and uvicorn, Groq API (`openai/gpt-oss-20b`), pydantic-settings, pytest, GitHub Actions.

## Project structure

```text
src/
  config.py              settings (.env)
  api/main.py            FastAPI app: POST /ask (streaming), GET /health
  ingestion/
    loader.py            reads repo files
    chunker.py           AST chunking for Python
    doc_chunker.py       heading-based chunking for docs
    indexer.py           chunks a whole repo (code + docs)
    build_index.py       embeds and saves the index (run once)
    embedder.py          sentence-transformers wrapper
    storage.py           ChromaDB + BM25 stores
  retrieval/
    hybrid.py            Reciprocal Rank Fusion
    reranker.py          cross-encoder re-ranking
    pipeline.py          full retrieval pipeline
  generation/
    prompt_builder.py    grounded prompt with citations
    generator.py         LLM calls (streaming and non-streaming)
  observability/tracer.py   per-request tracing
tests/                   pytest suite
eval/                    eval sets and runner
.github/workflows/       CI
```

The `test_*.py` files in the repository root are manual exploration scripts from development. The automated tests are in `tests/`.

## Setup

```bash
git clone https://github.com/divmishra476-bit/rag-codebase-qa.git
cd rag-codebase-qa
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Create a file named .env containing one line:
# GROQ_API_KEY=your_key_here

# Clone the repository to index
git clone https://github.com/encode/httpx.git test-repo

# Build the index once (can take a while on CPU)
python -m src.ingestion.build_index test-repo

# Start the API, then open http://localhost:8000/docs and try POST /ask
uvicorn src.api.main:app

# Run the tests and the retrieval eval
pytest tests/ -v
python test_eval.py
```

## Known limitations

- Chunking relies on Python's `ast` module, so only Python code is chunked. Other languages would need a parser such as tree-sitter.
- The eval set is small (14 questions) and docs-heavy; see Evaluation.
- Known retrieval weakness: broad questions such as "how do I make an HTTP request" can be outranked by docs chunks.
- The API runs locally only. There is no public deployment and no frontend.
- Rebuilding the index replaces the previous one; there is no incremental update.
- The LLM is a free-tier model on Groq. Swapping providers means changing `generator.py`.
