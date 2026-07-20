"""POST /upload endpoint: accept and process a gem5 stats.txt file.

Handles multipart file upload, extension validation, pipeline execution,
and caching of the result. All heavy lifting is delegated to
:class:`~services.pipeline.AnalysisPipeline`; the route itself only
manages HTTP concerns (status codes, error envelopes, headers).
"""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from services.cache import ResultCache
from services.pipeline import AnalysisPipeline, PipelineResult
from utils.constants import ALLOWED_EXTENSIONS
from utils.helpers import generate_file_id, has_allowed_extension
from utils.logger import get_logger

logger = get_logger(__name__)

upload_bp = Blueprint("upload", __name__)

# Module-level cache instances shared across requests within this process.
# Keyed by file_id -> PipelineResult, and file_id -> original filename.
pipeline_cache: ResultCache[PipelineResult] = ResultCache()
filename_cache: ResultCache[str] = ResultCache()


@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    """Handle upload of a gem5 stats.txt file.

    Expects a ``multipart/form-data`` request with a single file field
    named ``file``.

    Returns:
        JSON body ``{"file_id": ..., "status": "success"}`` with HTTP
        201 on success, or an error envelope with the appropriate 4xx / 5xx
        status code on failure:

        - 400 ``bad_request`` — missing file part or empty filename.
        - 400 ``invalid_extension`` — file suffix not in
          :data:`~utils.constants.ALLOWED_EXTENSIONS`.
        - 400 ``empty_file`` — uploaded file has zero bytes.
        - 422 ``no_metrics_found`` — file parsed but contained no valid
          gem5 metrics.
        - 422 ``corrupted_file`` — file could not be parsed.
        - 500 ``upload_failed`` — OS-level save failure.
    """
    if "file" not in request.files:
        return jsonify({"error": "bad_request", "message": "No file part in request"}), 400

    uploaded = request.files["file"]

    if not uploaded.filename:
        return jsonify({"error": "bad_request", "message": "No file selected"}), 400

    if not has_allowed_extension(uploaded.filename, ALLOWED_EXTENSIONS):
        return (
            jsonify(
                {
                    "error": "invalid_extension",
                    "message": f"Only {sorted(ALLOWED_EXTENSIONS)} files are accepted",
                }
            ),
            400,
        )

    file_id = generate_file_id()
    safe_name = secure_filename(uploaded.filename) or "stats.txt"
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    upload_dir.mkdir(parents=True, exist_ok=True)
    destination = upload_dir / f"{file_id}_{safe_name}"

    try:
        uploaded.save(destination)
        logger.info("File saved: %s (%d bytes)", destination.name, destination.stat().st_size)
    except OSError as exc:
        logger.error("Failed to save upload: %s", exc)
        return jsonify({"error": "upload_failed", "message": "Could not save file"}), 500

    if destination.stat().st_size == 0:
        destination.unlink(missing_ok=True)
        return jsonify({"error": "empty_file", "message": "Uploaded file is empty"}), 400

    try:
        result = AnalysisPipeline().run(destination)
    except FileNotFoundError:
        return jsonify({"error": "upload_failed", "message": "File went missing after save"}), 500
    except (OSError, ValueError) as exc:
        logger.error("Failed to parse uploaded file: %s", exc)
        return jsonify({"error": "corrupted_file", "message": "Could not parse file contents"}), 422

    if not result.parsed.metrics:
        return (
            jsonify(
                {
                    "error": "no_metrics_found",
                    "message": "No valid gem5 metrics were found in the file",
                }
            ),
            422,
        )

    pipeline_cache.set(file_id, result)
    filename_cache.set(file_id, uploaded.filename)

    logger.info(
        "Upload successful: file_id=%s metrics=%d parse_time=%.4fs",
        file_id,
        len(result.parsed.metrics),
        result.parse_time_seconds,
    )
    return jsonify({"file_id": file_id, "status": "success"}), 201