"""Integration tests for all REST API endpoints.

Tests use the session-scoped ``client`` and ``uploaded_file_id`` fixtures
from ``conftest.py``. Every test validates both HTTP status codes and the
structure / content of the JSON response body.
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


def test_health_check_returns_ok(client) -> None:
    """GET /health returns 200 with status=ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"


# ---------------------------------------------------------------------------
# Upload — happy path
# ---------------------------------------------------------------------------


def test_upload_returns_201_and_file_id(client, sample_stats_path: Path) -> None:
    """POST /upload with a valid stats.txt returns 201 and a file_id."""
    data = {"file": (io.BytesIO(sample_stats_path.read_bytes()), "stats.txt")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 201
    body = response.get_json()
    assert "file_id" in body
    assert body["status"] == "success"
    assert len(body["file_id"]) == 32  # UUID4 hex


# ---------------------------------------------------------------------------
# Upload — error cases
# ---------------------------------------------------------------------------


def test_upload_no_file_part_returns_400(client) -> None:
    """POST /upload without a file part returns 400 bad_request."""
    response = client.post("/upload", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    assert response.get_json()["error"] == "bad_request"


def test_upload_empty_filename_returns_400(client) -> None:
    """POST /upload with an empty filename returns 400 bad_request."""
    data = {"file": (io.BytesIO(b"content"), "")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert response.get_json()["error"] == "bad_request"


def test_upload_wrong_extension_returns_400(client) -> None:
    """POST /upload with a .csv file returns 400 invalid_extension."""
    data = {"file": (io.BytesIO(b"a,b,c"), "data.csv")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert response.get_json()["error"] == "invalid_extension"


def test_upload_empty_file_returns_400(client) -> None:
    """POST /upload with a zero-byte file returns 400 empty_file."""
    data = {"file": (io.BytesIO(b""), "stats.txt")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert response.get_json()["error"] == "empty_file"


def test_upload_no_metrics_returns_422(client) -> None:
    """POST /upload with a file containing only comments returns 422."""
    content = b"# only a comment line\n# another comment\n"
    data = {"file": (io.BytesIO(content), "stats.txt")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 422
    assert response.get_json()["error"] == "no_metrics_found"


# ---------------------------------------------------------------------------
# GET /metrics/<file_id>
# ---------------------------------------------------------------------------


def test_get_all_metrics_returns_200(client, uploaded_file_id: str) -> None:
    """GET /metrics/<file_id> returns 200 with expected top-level keys."""
    response = client.get(f"/metrics/{uploaded_file_id}")
    assert response.status_code == 200
    body = response.get_json()
    assert "simulation" in body
    assert "cpu" in body
    assert "derived" in body
    assert "metadata" in body


def test_get_all_metrics_metadata_structure(client, uploaded_file_id: str) -> None:
    """Metadata section has the expected fields."""
    response = client.get(f"/metrics/{uploaded_file_id}")
    metadata = response.get_json()["metadata"]
    assert "fileName" in metadata
    assert "parseTime" in metadata
    assert "metricCount" in metadata
    assert "warnings" in metadata


def test_get_all_metrics_simulation_contains_simSeconds(client, uploaded_file_id: str) -> None:
    """Simulation section contains simSeconds."""
    response = client.get(f"/metrics/{uploaded_file_id}")
    simulation = response.get_json()["simulation"]
    assert "simSeconds" in simulation


def test_get_all_metrics_cpu_contains_numCycles(client, uploaded_file_id: str) -> None:
    """CPU section contains system.cpu.numCycles."""
    response = client.get(f"/metrics/{uploaded_file_id}")
    cpu = response.get_json()["cpu"]
    assert "system.cpu.numCycles" in cpu


def test_get_all_metrics_unknown_file_id_returns_404(client) -> None:
    """GET /metrics/<bad_id> returns 404 not_found."""
    response = client.get("/metrics/deadbeef00000000000000000000dead")
    assert response.status_code == 404
    assert response.get_json()["error"] == "not_found"


# ---------------------------------------------------------------------------
# GET /metrics/cpu/<file_id>
# ---------------------------------------------------------------------------


def test_get_cpu_metrics_returns_200(client, uploaded_file_id: str) -> None:
    """GET /metrics/cpu/<file_id> returns 200 with cpu and metadata keys."""
    response = client.get(f"/metrics/cpu/{uploaded_file_id}")
    assert response.status_code == 200
    body = response.get_json()
    assert "cpu" in body
    assert "metadata" in body
    assert "simulation" not in body


def test_get_cpu_metrics_unknown_id_returns_404(client) -> None:
    """GET /metrics/cpu/<bad_id> returns 404."""
    response = client.get("/metrics/cpu/deadbeef00000000000000000000dead")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /metrics/simulation/<file_id>
# ---------------------------------------------------------------------------


def test_get_simulation_metrics_returns_200(client, uploaded_file_id: str) -> None:
    """GET /metrics/simulation/<file_id> returns 200 with simulation key."""
    response = client.get(f"/metrics/simulation/{uploaded_file_id}")
    assert response.status_code == 200
    body = response.get_json()
    assert "simulation" in body
    assert "metadata" in body
    assert "cpu" not in body


def test_get_simulation_metrics_unknown_id_returns_404(client) -> None:
    """GET /metrics/simulation/<bad_id> returns 404."""
    response = client.get("/metrics/simulation/deadbeef00000000000000000000dead")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /metrics/derived/<file_id>
# ---------------------------------------------------------------------------


def test_get_derived_metrics_returns_200(client, uploaded_file_id: str) -> None:
    """GET /metrics/derived/<file_id> returns 200 with derived key."""
    response = client.get(f"/metrics/derived/{uploaded_file_id}")
    assert response.status_code == 200
    body = response.get_json()
    assert "derived" in body
    assert "metadata" in body
    assert "cpu" not in body


def test_get_derived_metrics_contains_expected_keys(client, uploaded_file_id: str) -> None:
    """Derived section contains all expected derived metric names."""
    expected = {
        "ipc",
        "cpi",
        "executionTimeSeconds",
        "busyCycles",
        "idlePercentage",
        "instructionEfficiency",
        "hostSpeedInstsPerSec",
        "cpuUtilizationPercentage",
    }
    response = client.get(f"/metrics/derived/{uploaded_file_id}")
    derived = response.get_json()["derived"]
    assert expected.issubset(set(derived.keys()))


def test_get_derived_metrics_unknown_id_returns_404(client) -> None:
    """GET /metrics/derived/<bad_id> returns 404."""
    response = client.get("/metrics/derived/deadbeef00000000000000000000dead")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# 404 / 405
# ---------------------------------------------------------------------------


def test_unknown_route_returns_404(client) -> None:
    """Requests to unknown routes return 404."""
    response = client.get("/nonexistent/route")
    assert response.status_code == 404


def test_wrong_method_on_upload_returns_405(client) -> None:
    """GET /upload returns 405 method_not_allowed."""
    response = client.get("/upload")
    assert response.status_code == 405
