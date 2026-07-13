"""
logger.py

Centralized logging setup for the gtrace-benchmark framework.

Design decision: we build a single `GTraceLogger` factory rather than calling
`logging.basicConfig()` ad hoc in every module. This lets us load the console
format, rotation policy, and per-logger levels from config/logging.yaml in
one place, and guarantees every module gets a consistently configured
`logging.Logger` via `get_logger(name)`.
"""
from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any, Optional

import yaml

# ANSI color codes for console output. Kept minimal and terminal-portable.
_COLORS = {
    "DEBUG": "\033[36m",     # cyan
    "INFO": "\033[32m",      # green
    "WARNING": "\033[33m",   # yellow
    "ERROR": "\033[31m",     # red
    "CRITICAL": "\033[41m",  # red background
}
_RESET = "\033[0m"


class ColoredFormatter(logging.Formatter):
    """Formatter that wraps the levelname in an ANSI color for TTY output."""

    def __init__(self, fmt: str, datefmt: str, use_color: bool = True) -> None:
        super().__init__(fmt=fmt, datefmt=datefmt)
        self._use_color = use_color and sys.stdout.isatty()

    def format(self, record: logging.LogRecord) -> str:
        if self._use_color:
            color = _COLORS.get(record.levelname, "")
            original_levelname = record.levelname
            record.levelname = f"{color}{record.levelname}{_RESET}"
            formatted = super().format(record)
            record.levelname = original_levelname
            return formatted
        return super().format(record)


class LoggingConfigurator:
    """
    Loads config/logging.yaml once and configures the root 'gtrace' logger
    hierarchy. Subsequent calls to get_logger() are cheap lookups.
    """

    _configured = False

    @classmethod
    def configure(cls, config_path: Path, project_root: Optional[Path] = None) -> None:
        if cls._configured:
            return

        cfg: dict[str, Any] = {}
        if config_path.exists():
            with config_path.open() as f:
                cfg = yaml.safe_load(f) or {}

        project_root = project_root or config_path.parent.parent
        root_logger = logging.getLogger("gtrace")
        root_logger.setLevel(cfg.get("root_level", "INFO"))
        root_logger.handlers.clear()
        root_logger.propagate = False

        console_cfg = cfg.get("console", {})
        if console_cfg.get("enabled", True):
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(console_cfg.get("level", "INFO"))
            handler.setFormatter(
                ColoredFormatter(
                    fmt=console_cfg.get(
                        "format", "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
                    ),
                    datefmt=console_cfg.get("datefmt", "%H:%M:%S"),
                    use_color=console_cfg.get("colored", True),
                )
            )
            root_logger.addHandler(handler)

        file_cfg = cfg.get("file", {})
        if file_cfg.get("enabled", True):
            log_path = project_root / file_cfg.get("path", "logs/gtrace.log")
            log_path.parent.mkdir(parents=True, exist_ok=True)
            rotation = file_cfg.get("rotation", {})
            if rotation.get("enabled", True):
                file_handler: logging.Handler = logging.handlers.RotatingFileHandler(
                    log_path,
                    maxBytes=rotation.get("max_bytes", 10 * 1024 * 1024),
                    backupCount=rotation.get("backup_count", 5),
                )
            else:
                file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(file_cfg.get("level", "DEBUG"))
            file_handler.setFormatter(
                logging.Formatter(
                    fmt=file_cfg.get(
                        "format", "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
                    ),
                    datefmt=file_cfg.get("datefmt", "%Y-%m-%d %H:%M:%S"),
                )
            )
            root_logger.addHandler(file_handler)

        for logger_name, level in cfg.get("loggers", {}).items():
            logging.getLogger(logger_name).setLevel(level)

        cls._configured = True

    @classmethod
    def reset(cls) -> None:
        """Testing hook: allow re-configuration within the same process."""
        cls._configured = False
        logging.getLogger("gtrace").handlers.clear()


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger under the 'gtrace' hierarchy. If LoggingConfigurator has
    not been explicitly configured yet, falls back to sane defaults so
    imports never fail even in ad hoc scripts or unit tests.
    """
    if not LoggingConfigurator._configured:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
    return logging.getLogger(name)


def attach_per_run_file_handler(
    logger: logging.Logger, log_file: Path, level: str = "DEBUG"
) -> logging.Handler:
    """
    Attach a dedicated FileHandler for a single benchmark run's execution.log.
    Caller is responsible for removing the handler when the run completes
    (see BenchmarkRunner) to avoid leaking handlers across runs.
    """
    log_file.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_file)
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(handler)
    return handler