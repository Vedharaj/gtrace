"""Flask application factory for the gem5 stats analysis backend."""

from __future__ import annotations

from flask import Flask, jsonify

from api.routes import register_routes
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


def create_app(config: Config | None = None) -> Flask:
    """Construct and configure the Flask application.

    Args:
        config: Optional Config instance to use instead of the default
            environment-derived configuration. Primarily used by tests
            to inject a TestConfig.

    Returns:
        A fully configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config or Config.from_env())
    app.config["UPLOAD_FOLDER"].mkdir(parents=True, exist_ok=True)

    register_routes(app)
    _register_error_handlers(app)

    logger.info("Application created (debug=%s)", app.config.get("DEBUG"))
    return app


def _register_error_handlers(app: Flask) -> None:
    """Attach JSON error handlers for common HTTP failure modes.

    Args:
        app: The Flask application instance to attach handlers to.
    """

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "not_found", "message": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return jsonify({"error": "method_not_allowed", "message": "HTTP method not allowed"}), 405

    @app.errorhandler(413)
    def payload_too_large(_error):
        return jsonify({"error": "payload_too_large", "message": "Uploaded file is too large"}), 413

    @app.errorhandler(500)
    def internal_error(_error):
        logger.exception("Unhandled server error")
        return jsonify({"error": "internal_error", "message": "An unexpected error occurred"}), 500


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000)