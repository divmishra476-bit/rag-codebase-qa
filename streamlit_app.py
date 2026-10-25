import streamlit as st
from src.retrieval.pipeline import retrieve
from src.observability.tracer import Tracer
from src.api.main import (
    vector_store,
    keyword_store,
    embedder,
    reranker,
    generator,
    id_to_text,
    id_to_meta,
)

# Page configuration
st.set_page_config(
    page_title="HTTPX Codebase Q&A",
    page_icon="⚡",
    layout="wide"
)

# Sidebar with engineering details (Recruiter ko impress karne ke liye)
with st.sidebar:
    st.title("⚡ Project Info")
    st.markdown("""
    **RAG Architecture:**
    - **AST Chunker** (Code) + Heading Chunker (Docs)
    - **Hybrid Search:** Dense (BGE-Large) + BM25
    - **Fusion:** Reciprocal Rank Fusion (RRF)
    - **Reranker:** Cross-Encoder (`ms-marco-MiniLM-L-6-v2`)
    - **LLM:** Groq API (Streamed)
    - **Eval Recall@5:** ~92.8% on target repo (`httpx`)
    """)
    st.info("Built from scratch without LangChain/LlamaIndex.")

st.title("🔍 HTTPX Codebase Q&A")
st.caption("Ask questions about the `httpx` codebase (architecture, client requests, timeouts, etc.) with exact file/line citations.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "citations" in msg:
            with st.expander("📚 Retrieved Citations & Code Context"):
                for cite in msg["citations"]:
                    st.markdown(f"**`{cite['id']}`**")
                    st.code(cite["text"][:300] + ("..." if len(cite["text"]) > 300 else ""))

# Handle user input
user_query = st.chat_input("E.g., How do I configure timeouts in httpx?")

if user_query:
    # 1. Display user query
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # 2. Assistant streaming response
    with st.chat_message("assistant"):
        with st.spinner("Searching codebase & reranking..."):
            tracer = Tracer(user_query)
            retrieved_ids = retrieve(
                user_query,
                embedder,
                vector_store,
                keyword_store,
                id_to_text,
                id_to_meta,
                reranker,
                tracer=tracer,
            )
            retrieved_chunks = [
                {"id": doc_id, "text": id_to_text[doc_id], "meta": id_to_meta[doc_id]}
                for doc_id in retrieved_ids
            ]

        # Stream the LLM response live (typing effect)
        def token_stream():
            full_text = ""
            for piece in generator.stream_answer(user_query, retrieved_chunks):
                full_text += piece
                yield piece
            tracer.finish(retrieved_ids, full_text)

        response_text = st.write_stream(token_stream())

        # Show citations in expander
        with st.expander("📚 Retrieved Citations & Code Context"):
            for chunk in retrieved_chunks:
                st.markdown(f"**`{chunk['id']}`**")
                st.code(chunk["text"][:300] + ("..." if len(chunk["text"]) > 300 else ""))

        # Save to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_text,
            "citations": retrieved_chunks
        })