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

Future improvements will focus on retrieval quality, evaluation coverage, latency, and production deployment.
