# tests/test_loader.py
from src.ingestion.loader import load_repo_files

def test_load_repo_files_returns_files():
    files = load_repo_files("test-repo")
    assert len(files) > 0

def test_load_repo_files_tags_code_and_doc_types():
    files = load_repo_files("test-repo")
    file_types = {f.file_type for f in files}
    assert "code" in file_types
    assert "doc" in file_types

def test_load_repo_files_skips_hidden_and_test_folders():
    files = load_repo_files("test-repo")
    for f in files:
        assert ".git" not in f.path
        assert "test" not in f.path.lower() or "tests" not in f.path.lower()

def test_load_repo_files_returns_empty_list_for_invalid_path():
    files = load_repo_files("this-folder-does-not-exist")
    assert files == []