import os
import fitz  # PyMuPDF
from docx import Document

PROCESSED_TEXT_DIR = "app/processed/text"
os.makedirs(PROCESSED_TEXT_DIR, exist_ok=True)


def extract_text(file_path: str):
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        text = _extract_pdf(file_path)
    elif extension == ".docx":
        text = _extract_docx(file_path)
    elif extension == ".txt":
        text = _extract_txt(file_path)
    else:
        raise ValueError("Unsupported file format")

    if not text.strip():
        raise ValueError("No text extracted")

    filename = os.path.basename(file_path)
    print("file_name",filename)
    text_filename = filename.rsplit(".", 1)[0] + ".txt"
    text_path = os.path.join(PROCESSED_TEXT_DIR, text_filename)

    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text)

    return text_path


def _extract_pdf(file_path: str):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def _extract_docx(file_path: str):
    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs)


def _extract_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
