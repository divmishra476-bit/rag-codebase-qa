# tests/test_chunker.py
from src.ingestion.chunker import chunk_python_file

SAMPLE_CODE = '''
def top_level_function(x, y):
    return x + y

class MyClass:
    def method_one(self):
        return 1

    def method_two(self, a):
        return a * 2
'''

def test_chunk_python_file_finds_top_level_function():
    chunks = chunk_python_file("sample.py", SAMPLE_CODE)
    function_chunks = [c for c in chunks if c.chunk_type == "function"]
    assert len(function_chunks) == 1
    assert function_chunks[0].name == "top_level_function"

def test_chunk_python_file_finds_class():
    chunks = chunk_python_file("sample.py", SAMPLE_CODE)
    class_chunks = [c for c in chunks if c.chunk_type == "class"]
    assert len(class_chunks) == 1
    assert class_chunks[0].name == "MyClass"

def test_chunk_python_file_finds_methods_with_class_prefix():
    chunks = chunk_python_file("sample.py", SAMPLE_CODE)
    method_chunks = [c for c in chunks if c.chunk_type == "method"]
    method_names = {c.name for c in method_chunks}
    assert method_names == {"MyClass.method_one", "MyClass.method_two"}

def test_chunk_python_file_handles_syntax_errors_gracefully():
    broken_code = "def broken(:\n    pass"
    chunks = chunk_python_file("broken.py", broken_code)
    assert chunks == []