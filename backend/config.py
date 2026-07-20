"""Application configuration.

Centralizes environment-driven settings so no module reads environment
variables directly. Extend this class (or subclass it) for
dev/test/prod variants.
"""

from __future__ import annotations

import os
from pathlib import Path

from utils.constants import MAX_FILE_SIZE_BYTES, UPLOAD_DIR_NAME


class Config:
    """Base Flask configuration.

    Attributes:
        BASE_DIR: Absolute path to the backend project root.
        UPLOAD_FOLDER: Absolute path to the directory where uploaded
            files are stored.
        MAX_CONTENT_LENGTH: Maximum accepted request body size, in bytes.
        JSON_SORT_KEYS: Whether Flask should sort JSON response keys.
    """

    BASE_DIR: Path = Path(__file__).resolve().parent
    UPLOAD_FOLDER: Path = BASE_DIR / UPLOAD_DIR_NAME
    MAX_CONTENT_LENGTH: int = MAX_FILE_SIZE_BYTES
    JSON_SORT_KEYS: bool = False
    TESTING: bool = False
    DEBUG: bool = False

    @classmethod
    def from_env(cls) -> "Config":
        """Build a Config instance, allowing environment overrides.

        Returns:
            A Config instance with DEBUG toggled based on the
            FLASK_DEBUG environment variable.
        """
        config = cls()
        config.DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
        return config


class TestConfig(Config):
    """Configuration used by the pytest suite."""

    TESTING: bool = True
    UPLOAD_FOLDER: Path = Config.BASE_DIR / "tests" / "_tmp_uploads"