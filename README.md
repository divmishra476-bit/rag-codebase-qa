# 🔍 Codebase Q&A — Grounded RAG from Scratch

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://rag-codebase-app-vjnyxtdshllzwrfeqsqcjr.streamlit.app)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/divmishra476-bit/rag-codebase-qa/actions/workflows/ci.yml/badge.svg)](https://github.com/divmishra476-bit/rag-codebase-qa/actions)
[![Recall@5](https://img.shields.io/badge/Recall%405-92.86%25-brightgreen.svg)](#4-evaluation--benchmarks)

> 🚀 **Live Demo:** [rag-codebase-app-vjnyxtdshllzwrfeqsqcjr.streamlit.app](https://rag-codebase-app-vjnyxtdshllzwrfeqsqcjr.streamlit.app)

A Retrieval-Augmented Generation (RAG) system that answers natural-language questions about a software codebase (`httpx`) with exact file and line citations. Built completely from scratch with **no LangChain or orchestration frameworks**, ensuring every chunking, retrieval, and reranking decision is transparent and measurable.

---

## 📑 Table of Contents (Index)

1. [Overview](#1-overview)
2. [System Architecture](#2-system-architecture)
3. [Key Features](#3-key-features)
4. [Evaluation & Benchmarks](#4-evaluation--benchmarks)
5. [Key Engineering Decisions](#5-key-engineering-decisions)
6. [Tech Stack & Project Layout](#6-tech-stack--project-layout)
7. [Local Setup & Quickstart](#7-local-setup--quickstart)
8. [Known Limitations](#8-known-limitations)

---

## 1. Overview

- **Problem:** Generic LLMs hallucinate internal APIs, method signatures, and configuration flags when answering questions about a specific codebase.
- **Solution:** A grounded RAG system that indexes repository source code and documentation, retrieves context using a hybrid search + cross-encoder pipeline, and streams answers with verifiable `file:line` citations.
- **Target Repository:** `httpx` (978 pre-computed chunks covering full code and docs).
- **Core Philosophy:** Zero third-party RAG abstractions (No LangChain / LlamaIndex). All storage, retrieval math, fusion, and prompt templates are written in pure Python.

---

## 2. System Architecture

The pipeline is strictly decoupled into an **Offline Ingestion Stage** and an **Online Serving Stage**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. OFFLINE INGESTION (Run once via build_index.py)                     │
│                                                                        │
│ Repo Files ──► Loader ──► AST Chunker (Code) / Heading Chunker (Docs)  │
│                                 │                                      │
│                                 ├──► ChromaDB (Dense Vector Store)     │
│                                 └──► BM25 (Sparse Keyword Store)       │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼─────────────────────────────────────┐
│ 2. ONLINE SERVING (Streamlit UI / FastAPI /ask)                        │
│                                                                        │
│ User Query ──► Hybrid Search (Dense BGE-Large + BM25)                  │
│                     │                                                  │
│                     ▼                                                  │
│           Reciprocal Rank Fusion (RRF)                                 │
│                     │                                                  │
│                     ▼                                                  │
│           Cross-Encoder Reranker (ms-marco-MiniLM-L-6-v2)              │
│                     │                                                  │
│                     ▼                                                  │
│           Grounded Prompt Builder (Strict Citation Constraints)        │
│                     │                                                  │
│                     ▼                                                  │
│           Groq LLM (Streamed Response + JSON Request Trace)            │
└────────────────────────────────────────────────────────────────────────┘

3. Key Features
AST-Based Code Chunking: Uses Python's native ast module to split at function, class, and method boundaries instead of arbitrary token cuts, keeping syntax blocks and accurate line citations intact.
Document Heading Chunking: Splits Markdown/RST documentation by logical headers (#, ##, ###) to preserve conceptual cohesion.
Hybrid Retrieval with RRF: Fuses dense semantic search (BAAI/bge-large-en-v1.5) and sparse keyword search (rank_bm25) using Reciprocal Rank Fusion.
Two-Stage Reranking: Applies a cross-encoder model (ms-marco-MiniLM-L-6-v2) on fused candidates to minimize false positives before prompting the LLM.
Strict Grounded Prompting: Configured prompt template that instructs the LLM to only use provided context and cite file paths and line ranges.
Dual Serving Interfaces:
Interactive Streamlit Web UI with real-time token streaming and expandable citation drawers.
Production FastAPI service (POST /ask with StreamingResponse, GET /health).
Observability: JSON request tracing measuring per-stage latency (embed_query, hybrid_search, rerank, total_latency_ms).
4. Evaluation & Benchmarks
4.1. Retrieval Accuracy (Recall@5)
Retrieval quality is measured on the full repository index (978 chunks) using a pre-registered question set (eval/eval_set_v2.py):
Result: 13 / 14 = 92.86% Recall@5 (95% CI roughly 69% to 99%).
Pre-registered Ground Truth: Expected chunks were selected via keyword matching and committed to Git prior to running evaluation to prevent confirmation bias.
The Single Miss: For "what exceptions can httpx raise", the retriever returned docs/exceptions.md:1 and docs/quickstart.md:495. Both answer the query, but ground truth strictly expected docs/exceptions.md:40. It is reported as a miss and left unedited.
4.2. Latency & Memory Profile
Measured on standard CPU runtime:
Stage	Latency	Description
Query Embedding	~408 ms	BAAI/bge-large-en-v1.5 dense vector creation
Hybrid Search	~28 ms	ChromaDB vector search + BM25 keyword query
RRF Merging	< 2 ms	Merging ranked lists
Cross-Encoder Rerank	~2,012 ms	Cross-attention scoring of top candidates (primary bottleneck)
Total Retrieval Latency	~2.45 s	Time before first LLM token stream
Empirical Memory Usage: Baseline: 48 MB ──► Startup (Models + Index): ~1,836 MB ──► Peak RAM: ~1,955 MB (~1.95 GB). Runs comfortably within free 2.7 GB container limits.
5. Key Engineering Decisions
Why AST over Fixed Chunks? Fixed character chunking splits functions midway, breaking AST structure and giving wrong line citations. AST parsing guarantees complete functional blocks.
Why Hybrid Search (Dense + BM25)? Dense search understands concepts (e.g., "how to pause requests" ──► timeout), while BM25 handles exact identifiers (e.g., Client.send()). RRF merges both without arbitrary score weighting.
Why Cross-Encoder Reranking? Bi-encoders embed query and documents separately. Cross-encoders examine them simultaneously, dramatically filtering out borderline irrelevant context at the expense of CPU latency.
Why Pre-computed Storage? Generating dense embeddings on CPU is slow. Indexing is an offline task; serving is an online task that loads pre-built ChromaDB files instantly.
Why No LangChain? Raw implementations provide deterministic memory consumption, zero abstraction overhead, and total control over debugging.
6. Tech Stack & Project Layout
Tech Stack
Language & Runtime: Python 3.12
Embeddings & Reranker: sentence-transformers (bge-large-en-v1.5, ms-marco-MiniLM-L-6-v2)
Storage: ChromaDB (persistent HNSW) + rank_bm25
LLM Provider: Groq Cloud API (openai/gpt-oss-20b, streamed)
Serving: Streamlit (Frontend) + FastAPI & Uvicorn (Backend API)
CI & Testing: pytest (14 unit/integration tests) + GitHub Actions CI
Directory Structure
code
Text
rag-codebase-qa/
├── chroma_db/               # Committed pre-built vector & metadata index (10.2 MB)
├── src/
│   ├── config.py            # Typed settings via pydantic-settings
│   ├── api/main.py          # FastAPI application (POST /ask, GET /health)
│   ├── ingestion/
│   │   ├── loader.py        # File discovery
│   │   ├── chunker.py       # AST chunker for Python
│   │   ├── doc_chunker.py   # Heading chunker for Markdown/RST
│   │   ├── build_index.py   # Offline index builder
│   │   └── storage.py       # ChromaDB + BM25 interfaces
│   ├── retrieval/
│   │   ├── hybrid.py        # Reciprocal Rank Fusion implementation
│   │   ├── reranker.py      # Cross-encoder inference wrapper
│   │   └── pipeline.py      # Coordinated retrieval pipeline
│   ├── generation/
│   │   ├── prompt_builder.py# Grounded prompt engineering
│   │   └── generator.py     # Groq API streaming client
│   └── observability/
│       └── tracer.py        # Structured JSON logger
├── eval/                    # Evaluation sets and runner scripts
├── tests/                   # Pytest test suite
├── streamlit_app.py         # Streamlit web application
├── requirements.txt         # Pinned project dependencies
└── measure_ram.py           # Physical RAM measurement script
7. Local Setup & Quickstart
Step 1: Clone Repository & Create Virtual Environment
code
Powershell
git clone https://github.com/divmishra476-bit/rag-codebase-qa.git
cd rag-codebase-qa
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
Step 2: Configure Environment Variables
Create a .env file in the project root:
code
Env
GROQ_API_KEY=your_groq_api_key_here
Step 3: Run the Application
Launch Streamlit Web UI (Interactive Chat):
code
Powershell
python -m streamlit run streamlit_app.py
Open http://localhost:8501 in your browser.
Launch FastAPI Backend (REST API):
code
Powershell
uvicorn src.api.main:app
API docs available at http://localhost:8000/docs.
Step 4: Run Tests
code
Powershell
pytest tests/ -v
8. Known Limitations
Python-Only Code Parsing: AST chunking uses Python's standard ast library. Multi-language support (JavaScript, Go, Rust) requires integrating tree-sitter.
Documentation Over-Retrieval: Generic natural language queries can cause documentation chunks to outrank specific source code implementations.
Static Index: Index updates currently require running build_index.py again; incremental real-time file updates are not implemented.

