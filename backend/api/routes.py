"""Top-level route registration, including the health check endpoint."""

from __future__ import annotations

from flask import Blueprint, Flask, jsonify

from api.metrics import metrics_bp
from api.upload import upload_bp

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Simple liveness/health check endpoint.

    Returns:
        JSON body ``{"status": "ok"}`` with HTTP 200.
    """
    return jsonify({"status": "ok"}), 200


def register_routes(app: Flask) -> None:
    """Register all blueprints on the given Flask app.

    Args:
        app: The Flask application instance.
    """
    app.register_blueprint(health_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(metrics_bp)