from flask import Blueprint, redirect, url_for, render_template
from flask_login import login_required, current_user
from sqlalchemy import select, func
from extensions import db
from models import Document, DocumentGrant, Conversation
bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return redirect(url_for("main.dashboard" if current_user.is_authenticated else "auth.login"))

@bp.route("/dashboard")
@login_required
def dashboard():
    allowed = select(Document.id).join(DocumentGrant).where(DocumentGrant.user_id == current_user.id)
    stmt = select(func.count(Document.id))
    if current_user.role != "admin":
        stmt = stmt.where((Document.visibility == "public") | (Document.id.in_(allowed)))
    docs = db.session.scalar(stmt) or 0
    chats = db.session.scalar(select(func.count(Conversation.id)).where(Conversation.user_id == current_user.id)) or 0
    return render_template("dashboard.html", document_count=docs, conversation_count=chats)
