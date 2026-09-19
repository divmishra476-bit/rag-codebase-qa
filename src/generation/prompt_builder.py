# src/generation/prompt_builder.py

SYSTEM_PROMPT = """You are a helpful assistant that answers questions about a codebase.
You will be given relevant code/documentation snippets and a question.
Answer ONLY using the provided snippets. If the snippets don't contain enough
information to answer confidently, say so clearly instead of guessing.
Always cite the file path and line numbers for any claim you make."""


def build_prompt(query: str, chunks: list[dict]) -> str:
    """
    chunks: list of dicts, each with 'id', 'text', and 'meta'
    (file_path, name, chunk_type, start_line, end_line)
    Returns the full user-turn prompt to send to Claude.
    """
    context_blocks = []

    for c in chunks:
        meta = c["meta"]
        block = (
            f"--- {meta['file_path']} "
            f"(lines {meta['start_line']}-{meta['end_line']}, "
            f"{meta['chunk_type']}: {meta['name']}) ---\n"
            f"{c['text']}"
        )
        context_blocks.append(block)

    context = "\n\n".join(context_blocks)

    prompt = f"""Here are relevant code snippets from the codebase:

{context}

Question: {query}

Answer the question using only the snippets above. Cite file paths and line numbers."""

    return prompt