# test_doc_chunker.py
from src.ingestion.loader import load_repo_files
from src.ingestion.doc_chunker import chunk_markdown_file

files = load_repo_files("test-repo")
doc_files = [f for f in files if f.file_type == "doc"]

target = next(f for f in doc_files if f.path.lower() == "readme.md")

chunks = chunk_markdown_file(target.path, target.content)
print(f"File: {target.path}")
print(f"Found {len(chunks)} sections")

for c in chunks[:5]:
    print(f"\n--- [{c.heading}] (lines {c.start_line}-{c.end_line}) ---")
    print(c.content[:150])