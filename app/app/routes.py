from flask import Blueprint, render_template, request, jsonify, current_app
from sqlalchemy import desc
from .extensions import db
from .models import Note

bp = Blueprint("main", __name__)

def paginated_query(search: str | None, page: int, limit: int):
    q = Note.query
    if search:
        like = f"%{search}%"
        q = q.filter(Note.content.ilike(like))
    q = q.order_by(desc(Note.created_at))
    total = q.count()
    items = q.offset((page - 1) * limit).limit(limit).all()
    return items, total

@bp.get("/")
def index():
    # Initial page render; dynamic updates via JS
    return render_template("index.html")

@bp.get("/notes")
def list_notes():
    search = request.args.get("search", type=str, default=None)
    page = request.args.get("page", type=int, default=1)
    limit = request.args.get("limit", type=int, default=10)

    items, total = paginated_query(search, page, limit)
    return jsonify({
        "items": [n.as_dict() for n in items],
        "meta": {"page": page, "limit": limit, "total": total}
    })

@bp.post("/notes")
def create_note():
    data = request.get_json(silent=True) or request.form
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "content cannot be empty"}), 400
    n = Note(content=content)
    db.session.add(n)
    db.session.commit()
    current_app.logger.info("Created note id=%s", n.id)
    return jsonify(n.as_dict()), 201

@bp.put("/notes/<int:note_id>")
def update_note(note_id: int):
    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "content cannot be empty"}), 400
    n = Note.query.get_or_404(note_id)
    n.content = content
    db.session.commit()
    current_app.logger.info("Updated note id=%s", n.id)
    return jsonify(n.as_dict()), 200

@bp.delete("/notes/<int:note_id>")
def delete_note(note_id: int):
    n = Note.query.get_or_404(note_id)
    db.session.delete(n)
    db.session.commit()
    current_app.logger.info("Deleted note id=%s", n.id)
    return ("", 204)
