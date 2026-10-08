# tests/test_loader.py
from src.ingestion.loader import load_repo_files
from pathlib import Path

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
        parts = Path(f.path).parts
        assert not any(p.startswith(".") for p in parts)
        assert "test" not in parts
        assert "tests" not in parts

def test_load_repo_files_returns_empty_list_for_invalid_path():
    files = load_repo_files("this-folder-does-not-exist")
    assert files == []

def test_load_repo_files_works_when_parent_folder_is_hidden(tmp_path):
    repo = tmp_path / ".cache" / "repo"
    repo.mkdir(parents=True)
    (repo / "a.py").write_text("x = 1")
    files = load_repo_files(str(repo))
    assert len(files) == 1