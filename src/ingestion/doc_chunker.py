# src/ingestion/doc_chunker.py
import re
from dataclasses import dataclass

@dataclass
class DocChunk:
    content: str
    file_path: str
    chunk_type: str      # "doc_section"
    heading: str
    start_line: int
    end_line: int

def chunk_markdown_file(file_path: str, content: str) -> list[DocChunk]:
    lines = content.splitlines()
    chunks = []

    heading_pattern = re.compile(r"^(#{1,3})\s+(.*)")
    section_start = 0
    current_heading = "Introduction"

    for i, line in enumerate(lines):
        match = heading_pattern.match(line)
        if match:
            if i > section_start:
                section_text = "\n".join(lines[section_start:i]).strip()
                if section_text:
                    chunks.append(DocChunk(
                        content=section_text,
                        file_path=file_path,
                        chunk_type="doc_section",
                        heading=current_heading,
                        start_line=section_start + 1,
                        end_line=i,
                    ))
            current_heading = match.group(2)
            section_start = i

    if section_start < len(lines):
        section_text = "\n".join(lines[section_start:]).strip()
        if section_text:
            chunks.append(DocChunk(
                content=section_text,
                file_path=file_path,
                chunk_type="doc_section",
                heading=current_heading,
                start_line=section_start + 1,
                end_line=len(lines),
            ))

    return chunks