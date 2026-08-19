from src.ingestion.loader import load_repo_files
from src.ingestion.chunker import chunk_python_file

files = load_repo_files("test-repo")
code_files = [f for f in files if f.file_type == "code"]

# pick a file likely to have classes — _client.py or _api.py are good bets
target = next(f for f in code_files if "_client" in f.path)

chunks = chunk_python_file(target.path, target.content)
print(f"File: {target.path}")
print(f"Found {len(chunks)} total chunks")

for c in chunks[:10]:
    print(f"\n--- [{c.chunk_type}] {c.name} (lines {c.start_line}-{c.end_line}) ---")
    print(c.content[:100])