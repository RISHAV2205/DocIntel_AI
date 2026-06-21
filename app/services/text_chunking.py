def chunk_text(
    text: str,
    chunk_size: int = 400,
    overlap: int = 50):
    """
    Split cleaned text into overlapping word-based chunks.
    Uses only Python standard library.
    """

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    words = text.split()
    total_words = len(words)

    chunks = []
    start = 0

    while start < total_words:
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk = " ".join(chunk_words)
        chunks.append(chunk)

        # move forward with overlap
        start += chunk_size - overlap

    return chunks
