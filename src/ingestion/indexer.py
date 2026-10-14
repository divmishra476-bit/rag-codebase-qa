# src/ingestion/indexer.py
from src.ingestion.loader import load_repo_files
from src.ingestion.chunker import chunk_python_file
from src.ingestion.doc_chunker import chunk_markdown_file


def collect_chunks(repo_path: str) -> list[dict]:
    """Load a whole repo and return every chunk (code + docs) as {id, text, meta}."""
    records = {}

    for f in load_repo_files(repo_path):
        if f.file_type == "code":
            for c in chunk_python_file(f.path, f.content):
                chunk_id = f"{c.file_path}:{c.start_line}"
                records[chunk_id] = {
                    "id": chunk_id,
                    "text": c.content,
                    "meta": {
                        "file_path": c.file_path,
                        "chunk_type": c.chunk_type,
                        "name": c.name,
                        "start_line": c.start_line,
                        "end_line": c.end_line,
                    },
                }
        else:
            for c in chunk_markdown_file(f.path, f.content):
                chunk_id = f"{c.file_path}:{c.start_line}"
                records[chunk_id] = {
                    "id": chunk_id,
                    "text": c.content,
                    "meta": {
                        "file_path": c.file_path,
                        "chunk_type": c.chunk_type,
                        "name": c.heading,
                        "start_line": c.start_line,
                        "end_line": c.end_line,
                    },
                }

    return list(records.values())