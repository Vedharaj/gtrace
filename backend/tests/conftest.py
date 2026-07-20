"""Shared pytest fixtures for the gem5 backend test suite.

Provides:
  - ``sample_stats_path``: Path to the canonical sample stats.txt used by
    parser/extractor tests.
  - ``app``: Flask application instance configured for testing.
  - ``client``: Flask test client derived from ``app``.
  - ``uploaded_file_id``: A pre-uploaded file_id for metrics endpoint tests.
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from app import create_app
from config import TestConfig


# ---------------------------------------------------------------------------
# Path fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def sample_stats_path() -> Path:
    """Return the path to the canonical sample stats.txt.

    Returns:
        Absolute path to ``backend/uploads/sample_stats.txt``.
    """
    path = Path(__file__).parent.parent / "uploads" / "sample_stats.txt"
    assert path.exists(), f"Sample stats file missing: {path}"
    return path


# ---------------------------------------------------------------------------
# Flask application fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def app():
    """Create a Flask application instance configured for testing.

    Yields:
        A Flask app with ``TESTING=True`` and a temporary upload folder.
    """
    cfg = TestConfig()
    cfg.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    flask_app = create_app(cfg)
    yield flask_app

    # Cleanup temporary uploads created during tests.
    for f in cfg.UPLOAD_FOLDER.glob("*.txt"):
        f.unlink(missing_ok=True)


@pytest.fixture(scope="session")
def client(app):
    """Return a Flask test client for the session.

    Args:
        app: The session-scoped Flask app fixture.

    Returns:
        A :class:`flask.testing.FlaskClient` instance.
    """
    return app.test_client()


@pytest.fixture(scope="session")
def uploaded_file_id(client, sample_stats_path: Path) -> str:
    """Upload the sample stats file once and return the resulting file_id.

    Subsequent tests that need a valid file_id should use this fixture
    rather than re-uploading.

    Args:
        client: The session-scoped Flask test client.
        sample_stats_path: Path to the sample stats.txt.

    Returns:
        The ``file_id`` string from the upload response.
    """
    data = {"file": (io.BytesIO(sample_stats_path.read_bytes()), "stats.txt")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 201, f"Upload setup failed: {response.get_json()}"
    return response.get_json()["file_id"]
