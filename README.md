# rag-codebase-qa

A production-oriented Retrieval-Augmented Generation (RAG) pipeline for asking questions about a software codebase.

The system ingests a repository, creates code-aware chunks, generates embeddings, performs hybrid retrieval, reranks the retrieved results, and uses an LLM to generate answers from the relevant code context.

## Architecture

```text
Repository
    │
    ▼
┌──────────────┐
│   Ingestion  │
│              │
│ Repo Loader  │
│ AST Chunking │
│ Doc Chunking │
│ Embeddings   │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│     Storage      │
│ Vector + BM25    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    Retrieval     │
│                  │
│ Hybrid Search    │
│ RRF              │
│ Reranking        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    Generation    │
│                  │
│ Prompt Builder   │
│ LLM Generation   │
└────────┬─────────┘
         │
         ▼
       Answer

Key Features
Repository-aware code ingestion
AST-based chunking for Python code
Separate document chunking
Semantic embeddings
Hybrid retrieval combining vector and lexical search
Reciprocal Rank Fusion (RRF)
Cross-encoder reranking
Context-aware prompt construction
LLM-based answer generation
Retrieval evaluation pipeline
Retrieval Pipeline

The retrieval stage is designed as a multi-step pipeline:

A user submits a question about the codebase.
The query is searched using semantic and lexical retrieval.
Results from different retrieval methods are combined using Reciprocal Rank Fusion (RRF).
Retrieved candidates are reranked for better relevance.
The highest-quality context is passed to the generation stage.

This separates retrieval quality from generation and makes the system easier to evaluate and improve.

Evaluation

The project includes a retrieval evaluation setup for measuring retrieval quality against a predefined evaluation set.

Current evaluation checkpoint:

Recall@5: 83.33% (5/6 queries)

The remaining failed query was a timeout case.

Project Structure
rag-codebase-qa/
│
├── src/
│   ├── ingestion/
│   │   ├── loader.py
│   │   ├── chunker.py
│   │   ├── doc_chunker.py
│   │   ├── embedder.py
│   │   └── storage.py
│   │
│   ├── retrieval/
│   │   ├── hybrid.py
│   │   ├── pipeline.py
│   │   └── reranker.py
│   │
│   ├── generation/
│   │   ├── generator.py
│   │   └── prompt_builder.py
│   │
│   └── config.py
│
├── eval/
│   └── ...
│
└── README.md

Tech Stack

Python
Sentence Transformers
ChromaDB
BM25
Cross-Encoder Reranking
AST-based code parsing
Large Language Models
Why Code-Aware Chunking?

Traditional text chunking can split source code at arbitrary boundaries.

This project uses Python's Abstract Syntax Tree (AST) to identify meaningful code structures such as functions, methods, and classes.

This preserves more useful semantic boundaries for code retrieval.

Retrieval Design

The system uses both:

Semantic Retrieval

Embeddings are used to find code that is semantically related to the user's question.

Lexical Retrieval

BM25 provides keyword-based retrieval, which is useful when queries contain exact function names, class names, variables, or technical terms.

Hybrid Retrieval

The two retrieval signals are combined using Reciprocal Rank Fusion (RRF).

Reranking

Retrieved candidates are passed through a reranker to improve the ordering of the most relevant context before generation.

Goals

The project focuses on building a RAG system with an emphasis on:

Retrieval quality
Code-aware document processing
Modular architecture
Evaluation-driven development
Separating retrieval, reranking, and generation stages
Status

This project is actively being developed and evaluated.



## Key engineering decisions

- **AST-based code chunking** — splits Python files at real function/class/method boundaries (not fixed character counts), preserving complete, meaningful code units with accurate line numbers for citation.
- **Hybrid search (vector + BM25), merged with Reciprocal Rank Fusion** — semantic search alone misses exact keyword matches; BM25 alone misses conceptual matches. RRF combines both ranking signals without one method silently overriding the other.
- **Cross-encoder re-ranking** — refines the top hybrid candidates with a model trained specifically for query-document relevance.
- **Config-driven, no hardcoded secrets** — all models, retrieval parameters, and API keys live in `.env` / `src/config.py` via `pydantic-settings`.
- **Structured request tracing** — every query logs per-stage latency, retrieved chunk IDs, and answer length as JSON for real debugging.
- **No orchestration framework (LangChain/CrewAI)** — every component is implemented directly, so every design decision is one I can explain and defend.

## Documented findings from evaluation

1. **Re-ranker bias toward private methods** — the cross-encoder sometimes ranks internal/private methods (`_send_single_request`) above the correct public API method (`Client.request`). Mitigated by passing the top 5 candidates to the LLM rather than only the top 1 — the LLM correctly identified the right method despite imperfect ranking.
2. **Short-chunk retrieval weakness** — terse code (e.g., 2-line property getters/setters) carries weak semantic signal. Attempted a naive chunk-enrichment fix (prepending a generic header); this **reduced** recall from 83% to 50% by diluting previously-working chunks — reverted, and documented as a case where a plausible fix made things measurably worse.

## Setup

```bash
git clone https://github.com/divmishra476-bit/rag-codebase-qa.git
cd rag-codebase-qa
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key_here" > .env
git clone https://github.com/encode/httpx.git test-repo
pytest tests/ -v
```

## Known limitations / future work

- Currently supports Python codebases only — chunking relies on Python's `ast` module.
- Evaluation set is currently 6 questions — a larger set (30-50) would give more statistically meaningful numbers.
- Not yet deployed as a live API (FastAPI layer in progress).
- Agentic retrieval (function-calling to decide *when* to retrieve) considered as a stretch goal for a follow-up project.
- API currently indexes a single module (httpx/_client.py); full-repo indexing is the next step.
