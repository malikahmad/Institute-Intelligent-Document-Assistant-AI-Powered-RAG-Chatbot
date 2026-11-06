from flask import Blueprint, request, jsonify, abort, current_app
from flask_login import login_required, current_user
from sqlalchemy import select
from extensions import db
from models import Conversation, Message
from rag.pipeline import answer_question
bp = Blueprint("chat", __name__, url_prefix="/api")

@bp.route("/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question or len(question) > 5000:
        return jsonify(error="Enter a question of no more than 5000 characters."), 400
    cid = data.get("conversation_id")
    convo = db.session.scalar(select(Conversation).where(Conversation.id == cid, Conversation.user_id == current_user.id)) if cid else None
    if cid and not convo: abort(404)
    if not convo:
        convo = Conversation(user_id=current_user.id, title=question[:80])
        db.session.add(convo); db.session.commit()
    db.session.add(Message(conversation_id=convo.id, role="user", content=question)); db.session.commit()
    try:
        result = answer_question(question, current_user)
        db.session.add(Message(conversation_id=convo.id, role="assistant", content=result["answer"]))
        db.session.commit()
        return jsonify(conversation_id=convo.id, **result)
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Chat request failed")
        return jsonify(error="Assistant request failed. Check the Flask terminal."), 503

@bp.route("/conversations")
@login_required
def conversations():
    rows = db.session.scalars(select(Conversation).where(Conversation.user_id == current_user.id).order_by(Conversation.created_at.desc())).all()
    return jsonify([{"id": x.id, "title": x.title} for x in rows])

@bp.route("/conversations/<int:cid>")
@login_required
def conversation(cid):
    row = db.session.scalar(select(Conversation).where(Conversation.id == cid, Conversation.user_id == current_user.id))
    if not row: abort(404)
    return jsonify(messages=[{"role": m.role, "content": m.content} for m in row.messages])
