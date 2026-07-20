"""Pydantic schemas for all REST API responses.

Keeps request/response contracts decoupled from internal service types.
Every endpoint serializes through these models, which guarantees a
consistent, versioned JSON shape regardless of internal refactoring.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ResponseMetadata(BaseModel):
    """Metadata section appended to every metrics response.

    Attributes:
        fileName: Original file name supplied during upload.
        parseTime: Human-readable parse duration (e.g. ``"0.003210s"``).
        metricCount: Total number of metrics extracted from the file.
        warnings: List of non-fatal warning messages encountered during
            parsing or validation.
    """

    model_config = ConfigDict(populate_by_name=True)

    fileName: str
    parseTime: str
    metricCount: int
    warnings: list[str] = Field(default_factory=list)


class MetricsResponse(BaseModel):
    """Full structured response for ``GET /metrics/<file_id>`` and subsets.

    Attributes:
        simulation: Simulation-category metrics keyed by metric name.
        cpu: CPU-category metrics keyed by metric name.
        derived: Calculated/derived metric values keyed by derived name.
        metadata: Parse metadata and any warnings.
    """

    model_config = ConfigDict(populate_by_name=True)

    simulation: dict[str, dict] = Field(default_factory=dict)
    cpu: dict[str, dict] = Field(default_factory=dict)
    derived: dict[str, float | None] = Field(default_factory=dict)
    metadata: ResponseMetadata


class UploadResponse(BaseModel):
    """Response returned after a successful ``POST /upload``.

    Attributes:
        file_id: UUID hex string identifying the uploaded file's analysis
            results for subsequent ``GET /metrics/*`` requests.
        status: Always ``"success"`` on a 201 response.
    """

    file_id: str
    status: str = "success"


class ErrorResponse(BaseModel):
    """Standardized error envelope for 4xx / 5xx responses.

    Attributes:
        error: Machine-readable error code (snake_case).
        message: Human-readable description of the error.
    """

    error: str
    message: str
