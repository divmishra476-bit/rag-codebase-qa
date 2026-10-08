# src/ingestion/loader.py
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)
SKIP_DIRS = {"test", "tests", "venv", "env", "node_modules", "site-packages", "build", "dist"}

@dataclass
class LoadedFile:
    path: str
    content: str
    file_type: str  # "code" | "doc"

def load_repo_files(repo_path: str) -> list[LoadedFile]:
    repo = Path(repo_path)
    files = []

    code_extensions = {".py"}
    doc_extensions = {".md", ".rst"}

    if not repo.exists():
        logger.error(f"Repo path '{repo_path}' does not exist")
        return []

    for path in repo.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(repo)
        if any(part.startswith(".") for part in rel.parts):
            continue
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        

        suffix = path.suffix.lower()
        if suffix in code_extensions:
            file_type = "code"
        elif suffix in doc_extensions:
            file_type = "doc"
        else:
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError, OSError) as e:
            logger.warning(f"Skipping {path}: {e}")
            continue

        files.append(LoadedFile(
            path=str(path.relative_to(repo)),
            content=content,
            file_type=file_type,
        ))

    logger.info(f"Loaded {len(files)} files from {repo_path}")
    return files
