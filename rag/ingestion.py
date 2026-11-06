import re, io
from pathlib import Path
import fitz
from flask import current_app
from PIL import Image
from extensions import db
from models import Chunk
from rag.indexing import rebuild_index

def split_text(text, size, overlap):
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text: return []
    overlap = min(max(overlap, 0), size - 1)
    result, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if text[start:end].strip(): result.append(text[start:end].strip())
        if end == len(text): break
        start = end - overlap
    return result

def extract_pages(path):
    pages = []
    with fitz.open(path) as pdf:
        for number, page in enumerate(pdf, 1):
            text = page.get_text("text") or ""
            if len(text.strip()) < 30 and current_app.config["OCR_ENABLED"]:
                try:
                    import pytesseract
                    if current_app.config["TESSERACT_CMD"]:
                        pytesseract.pytesseract.tesseract_cmd = current_app.config["TESSERACT_CMD"]
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    text = pytesseract.image_to_string(Image.open(io.BytesIO(pix.tobytes("png"))))
                except Exception: current_app.logger.exception("OCR error on page %s", number)
            if text.strip(): pages.append((number, text))
    return pages

def ingest(document):
    path = Path(current_app.config["UPLOAD_FOLDER"]) / document.stored_name
    pending = []
    for page, text in extract_pages(path):
        for idx, chunk in enumerate(split_text(text, current_app.config["CHUNK_SIZE"], current_app.config["CHUNK_OVERLAP"])):
            pending.append(Chunk(document_id=document.id, chunk_index=idx, page_number=page, content=chunk))
    if not pending: raise ValueError("No readable text found in this PDF.")
    db.session.add_all(pending)
    db.session.commit()
    rebuild_index()
    return len(pending)
