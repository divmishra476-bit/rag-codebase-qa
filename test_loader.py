import logging
logging.basicConfig(level=logging.INFO)

from src.ingestion.loader import load_repo_files

files = load_repo_files("test-repo")
print(f"Loaded {len(files)} files")
print(f"First file: {files[0].path} ({files[0].file_type})")


for f in files[:5]:
    print(f"\n--- {f.path} ({f.file_type}) ---")
    print(f.content[:200])   # first 200 characters only