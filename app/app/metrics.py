from flask import Blueprint, Response, current_app
from time import time
from .extensions import db
from .models import Note

metrics_bp = Blueprint("metrics", __name__)

START_TIME = time()
REQUEST_COUNT = 0

@metrics_bp.before_app_request
def count_request():
    global REQUEST_COUNT
    REQUEST_COUNT += 1

@metrics_bp.get("/metrics")
def metrics():
    try:
        note_count = db.session.query(Note).count()
    except Exception as e:
        current_app.logger.error("Metrics query failed: %s", e)
        note_count = -1

    uptime = int(time() - START_TIME)
    payload = [
        "# HELP app_uptime_seconds Uptime in seconds",
        "# TYPE app_uptime_seconds counter",
        f"app_uptime_seconds {uptime}",
        "# HELP app_requests_total Total HTTP requests served",
        "# TYPE app_requests_total counter",
        f"app_requests_total {REQUEST_COUNT}",
        "# HELP app_notes_count Number of notes",
        "# TYPE app_notes_count gauge",
        f"app_notes_count {note_count}",
        "",
    ]
    return Response("\n".join(payload), mimetype="text/plain")
