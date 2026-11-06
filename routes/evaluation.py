from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from sqlalchemy import select, func
from extensions import db
from models import Document, Chunk
from rag.retriever import retrieve
bp = Blueprint("evaluation", __name__, url_prefix="/api/admin")

@bp.route("/evaluation")
@login_required
def evaluation():
    if current_user.role != "admin": return jsonify(error="Forbidden"), 403
    docs = db.session.scalar(select(func.count(Document.id))) or 0
    chunks = db.session.scalar(select(func.count(Chunk.id))) or 0
    samples = ["What are the admission requirements?", "What are the examination rules?", "How are fees paid?"]
    checks = []
    for question in samples:
        try:
            hits = retrieve(question, current_user)
            checks.append({"question": question, "hits": len(hits),
                           "top_document": hits[0]["chunk"].document.filename if hits else None})
        except Exception:
            checks.append({"question": question, "hits": 0, "error": "Retrieval failed"})
    return jsonify(documents=docs, chunks=chunks, checks=checks,
                   note="Diagnostic only; not a validated accuracy or faithfulness benchmark.")
