# src/ingestion/chunker.py
import ast
from dataclasses import dataclass

@dataclass
class Chunk:
    content: str
    file_path: str
    chunk_type: str   # "function" | "method" | "class"
    name: str          # e.g. "create_user" or "UserService.create_user"
    start_line: int
    end_line: int

def chunk_python_file(file_path: str, content: str) -> list[Chunk]:
    chunks = []

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return chunks

    lines = content.splitlines()

    def make_chunk(node, chunk_type, name):
        start = node.lineno
        end = node.end_lineno
        chunk_text = "\n".join(lines[start - 1:end])
        return Chunk(
            content=chunk_text,
            file_path=file_path,
            chunk_type=chunk_type,
            name=name,
            start_line=start,
            end_line=end,
        )

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            chunks.append(make_chunk(node, "function", node.name))

        elif isinstance(node, ast.ClassDef):
            # store the whole class as its own chunk
            chunks.append(make_chunk(node, "class", node.name))

            # then also store each method inside it separately
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_name = f"{node.name}.{child.name}"
                    chunks.append(make_chunk(child, "method", method_name))

    return chunks