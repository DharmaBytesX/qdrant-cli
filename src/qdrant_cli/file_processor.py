from pathlib import Path

from markitdown import MarkItDown


def process_file(file_path: str) -> str:
    path = Path(file_path)
    ext = path.suffix.lower()
    supported = {".docx", ".pdf", ".xlsx"}
    if ext not in supported:
        raise ValueError(f"Unsupported file type: {ext}. Supported: {', '.join(supported)}")
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    md = MarkItDown()
    result = md.convert(str(path))
    return result.text_content


def process_file_chunked(
    file_path: str, chunk_size: int = 512
) -> list[tuple[str, int]]:
    text = process_file(file_path)

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks: list[tuple[str, int]] = []
    current_chunk: list[str] = []
    current_word_count = 0
    idx = 0

    for para in paragraphs:
        para_words = len(para.split())
        if current_word_count + para_words > chunk_size and current_chunk:
            chunks.append((" ".join(current_chunk), idx))
            idx += 1
            current_chunk = []
            current_word_count = 0

        if para_words > chunk_size:
            if current_chunk:
                chunks.append((" ".join(current_chunk), idx))
                idx += 1
                current_chunk = []
                current_word_count = 0
            words = para.split()
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i : i + chunk_size])
                chunks.append((chunk, idx))
                idx += 1
        else:
            current_chunk.append(para)
            current_word_count += para_words

    if current_chunk:
        chunks.append((" ".join(current_chunk), idx))

    return chunks
