from .extensions import db
from datetime import datetime, timezone

class Note(db.Model):
    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def as_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "created_at": self.created_at.isoformat().replace("+00:00", "Z"),
        }
