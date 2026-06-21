from app.services.text_cleaner import clean_text
from app.services.text_chunking import chunk_text

def process_extracted_text(text_path: str):
    # Load extracted text
    with open(text_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Clean text
    cleaned_text = clean_text(raw_text)

    # Chunk text
    chunks = chunk_text(cleaned_text)

    return chunks
