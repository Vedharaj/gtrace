"""GET /metrics/* endpoints: expose parsed and derived metrics.

All four metric endpoints share the same underlying data-loading helper
(:func:`_load_or_404`) and delegate formatting to
:class:`~services.formatter.ResponseFormatter`. The routes themselves
contain *no* business logic — they only resolve file IDs, call the
formatter, and select which sections to include in the response.
"""

from __future__ import annotations

from flask import Blueprint, jsonify

from api.upload import filename_cache, pipeline_cache
from services.formatter import ResponseFormatter
from utils.logger import get_logger

logger = get_logger(__name__)

metrics_bp = Blueprint("metrics", __name__)

_formatter = ResponseFormatter()


def _load_or_404(file_id: str):
    """Fetch a cached PipelineResult for *file_id*, or None if missing.

    Args:
        file_id: The identifier returned by ``POST /upload``.

    Returns:
        A tuple of ``(PipelineResult, original_filename)``, or
        ``(None, None)`` if the file_id is unknown or has expired from
        cache.
    """
    result = pipeline_cache.get(file_id)
    filename = filename_cache.get(file_id)
    if result is None or filename is None:
        return None, None
    return result, filename


@metrics_bp.route("/metrics/<file_id>", methods=["GET"])
def get_all_metrics(file_id: str):
    """Return all extracted and derived metrics for a file.

    Args:
        file_id: The identifier returned by ``POST /upload``.

    Returns:
        JSON body matching the documented ``MetricsResponse`` schema with
        HTTP 200, or a 404 error envelope if *file_id* is unknown.
    """
    result, filename = _load_or_404(file_id)
    if result is None:
        logger.warning("metrics: unknown file_id=%s", file_id)
        return (
            jsonify({"error": "not_found", "message": f"Unknown file_id '{file_id}'"}),
            404,
        )

    response = _formatter.build_metrics_response(
        file_name=filename,
        parsed=result.parsed,
        derived=result.derived,
        warnings=result.warnings,
        parse_time_seconds=result.parse_time_seconds,
    )
    logger.info("metrics/all: file_id=%s", file_id)
    return jsonify(response.model_dump()), 200


@metrics_bp.route("/metrics/cpu/<file_id>", methods=["GET"])
def get_cpu_metrics(file_id: str):
    """Return only CPU-category metrics for a file.

    Args:
        file_id: The identifier returned by ``POST /upload``.

    Returns:
        JSON body containing the ``cpu`` and ``metadata`` sections only,
        with HTTP 200, or a 404 error envelope.
    """
    result, filename = _load_or_404(file_id)
    if result is None:
        return (
            jsonify({"error": "not_found", "message": f"Unknown file_id '{file_id}'"}),
            404,
        )

    response = _formatter.build_metrics_response(
        file_name=filename,
        parsed=result.parsed,
        derived=result.derived,
        warnings=result.warnings,
        parse_time_seconds=result.parse_time_seconds,
    )
    logger.info("metrics/cpu: file_id=%s", file_id)
    return jsonify({"cpu": response.cpu, "metadata": response.metadata.model_dump()}), 200


@metrics_bp.route("/metrics/simulation/<file_id>", methods=["GET"])
def get_simulation_metrics(file_id: str):
    """Return only simulation-category metrics for a file.

    Args:
        file_id: The identifier returned by ``POST /upload``.

    Returns:
        JSON body containing the ``simulation`` and ``metadata`` sections
        only, with HTTP 200, or a 404 error envelope.
    """
    result, filename = _load_or_404(file_id)
    if result is None:
        return (
            jsonify({"error": "not_found", "message": f"Unknown file_id '{file_id}'"}),
            404,
        )

    response = _formatter.build_metrics_response(
        file_name=filename,
        parsed=result.parsed,
        derived=result.derived,
        warnings=result.warnings,
        parse_time_seconds=result.parse_time_seconds,
    )
    logger.info("metrics/simulation: file_id=%s", file_id)
    return (
        jsonify(
            {"simulation": response.simulation, "metadata": response.metadata.model_dump()}
        ),
        200,
    )


@metrics_bp.route("/metrics/derived/<file_id>", methods=["GET"])
def get_derived_metrics(file_id: str):
    """Return only calculated (derived) metrics for a file.

    Args:
        file_id: The identifier returned by ``POST /upload``.

    Returns:
        JSON body containing the ``derived`` and ``metadata`` sections
        only, with HTTP 200, or a 404 error envelope.
    """
    result, filename = _load_or_404(file_id)
    if result is None:
        return (
            jsonify({"error": "not_found", "message": f"Unknown file_id '{file_id}'"}),
            404,
        )

    response = _formatter.build_metrics_response(
        file_name=filename,
        parsed=result.parsed,
        derived=result.derived,
        warnings=result.warnings,
        parse_time_seconds=result.parse_time_seconds,
    )
    logger.info("metrics/derived: file_id=%s", file_id)
    return (
        jsonify({"derived": response.derived, "metadata": response.metadata.model_dump()}),
        200,
    )
