import json
from pathlib import Path
import numpy as np
from flask import current_app
from sqlalchemy import select
from sentence_transformers import SentenceTransformer
from extensions import db
from models import Chunk

def embedding_model():
    return SentenceTransformer(current_app.config["EMBEDDING_MODEL"])

def rebuild_index():
    rows = db.session.execute(select(Chunk.id, Chunk.content).order_by(Chunk.id)).all()
    folder = Path(current_app.config["VECTOR_FOLDER"])
    folder.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    import faiss
    model = embedding_model()
    vectors = model.encode([r.content for r in rows], normalize_embeddings=True, convert_to_numpy=True)
    vectors = np.asarray(vectors, dtype="float32")
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, str(folder / "chunks.faiss"))
    (folder / "chunk_ids.json").write_text(json.dumps([r.id for r in rows]), encoding="utf-8")
