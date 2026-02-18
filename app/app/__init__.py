from flask import Flask
from .extensions import db, migrate
from .routes import bp as main_bp
from .metrics import metrics_bp
import os
import logging

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Config
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+mysqlconnector://{os.getenv('DB_USER','notesuser')}:"
        f"{os.getenv('DB_PASSWORD','')}"
        f"@{os.getenv('DB_HOST','db')}:{os.getenv('DB_PORT','3306')}/"
        f"{os.getenv('DB_NAME','notesdb')}?charset=utf8mb4"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Logging to stdout
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(metrics_bp)

    @app.get("/health")
    def health():
        try:
            with app.app_context():
                db.session.execute(db.text("SELECT 1"))  # DB reachable
                # Check notes table exists
                db.session.execute(db.text("SELECT 1 FROM notes LIMIT 1"))
            return {"status": "ok"}, 200
        except Exception as e:
            app.logger.error("Health check failed: %s", e)
            return {"status": "error", "detail": str(e)}, 503

    return app
