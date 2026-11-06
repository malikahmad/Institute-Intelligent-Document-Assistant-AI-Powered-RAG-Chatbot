import uuid
from pathlib import Path
from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import select, func
from werkzeug.utils import secure_filename
from extensions import db
from models import User, Document, DocumentGrant, Chunk
from rag.ingestion import ingest
bp = Blueprint("admin", __name__, url_prefix="/admin")

def require_admin():
    if current_user.role != "admin": abort(403)

@bp.route("/")
@login_required
def dashboard():
    require_admin()
    users = db.session.scalars(select(User).order_by(User.created_at.desc())).all()
    docs = db.session.scalars(select(Document).order_by(Document.created_at.desc())).all()
    stats = {key: db.session.scalar(select(func.count(model.id))) or 0 for key, model in
             (("users", User), ("documents", Document), ("chunks", Chunk))}
    return render_template("admin_dashboard.html", users=users, documents=docs, stats=stats)

@bp.route("/documents/upload", methods=["POST"])
@login_required
def upload():
    require_admin()
    file = request.files.get("file")
    if not file or not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        flash("Select a valid PDF file.", "danger")
        return redirect(url_for("admin.dashboard"))
    stored = uuid.uuid4().hex + ".pdf"
    safe = secure_filename(file.filename) or "document.pdf"
    target = Path(current_app.config["UPLOAD_FOLDER"]) / stored
    file.save(target)
    doc = Document(filename=safe, stored_name=stored,
                   visibility="public" if request.form.get("visibility") == "public" else "private",
                   uploaded_by=current_user.id)
    db.session.add(doc)
    db.session.commit()
    try:
        count = ingest(doc)
        flash(f"Indexed {safe}: {count} chunks.", "success")
    except Exception as exc:
        db.session.delete(doc); db.session.commit(); target.unlink(missing_ok=True)
        current_app.logger.exception("PDF ingestion failed")
        flash(f"PDF indexing failed: {exc}", "danger")
    return redirect(url_for("admin.dashboard"))

@bp.route("/documents/<int:doc_id>/grant", methods=["POST"])
@login_required
def grant(doc_id):
    require_admin()
    doc, user = db.session.get(Document, doc_id), db.session.get(User, request.form.get("user_id", type=int))
    if not doc or not user: abort(404)
    exists = db.session.scalar(select(DocumentGrant).where(DocumentGrant.document_id == doc.id, DocumentGrant.user_id == user.id))
    if not exists:
        db.session.add(DocumentGrant(document_id=doc.id, user_id=user.id)); db.session.commit()
    flash("Document access granted.", "success")
    return redirect(url_for("admin.dashboard"))

@bp.route("/documents/<int:doc_id>/delete", methods=["POST"])
@login_required
def delete(doc_id):
    require_admin()
    doc = db.session.get(Document, doc_id)
    if not doc: abort(404)
    path = Path(current_app.config["UPLOAD_FOLDER"]) / doc.stored_name
    db.session.delete(doc); db.session.commit(); path.unlink(missing_ok=True)
    flash("Document deleted.", "success")
    return redirect(url_for("admin.dashboard"))
