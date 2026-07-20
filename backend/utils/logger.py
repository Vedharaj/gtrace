"""Centralized logging configuration.

Provides a single :func:`get_logger` factory so every module logs through
a consistently configured handler/formatter instead of each module
configuring logging ad hoc.
"""

from __future__ import annotations

import logging
import sys
from logging import Logger

_CONFIGURED: bool = False
_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def _configure_root() -> None:
    """Configure the root logger exactly once for the process."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT))

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)

    _CONFIGURED = True


def get_logger(name: str) -> Logger:
    """Return a configured logger for the given module name.

    Args:
        name: Typically ``__name__`` of the calling module.

    Returns:
        A :class:`logging.Logger` instance ready for use.
    """
    _configure_root()
    return logging.getLogger(name)