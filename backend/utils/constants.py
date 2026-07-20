"""Constants and configuration values used across the application.

This module centralizes all "magic" values: required metric names,
category classification rules, and file-handling constraints. New
metrics can be added here without touching parsing logic anywhere else.
"""

from __future__ import annotations

# --- File handling -----------------------------------------------------

ALLOWED_EXTENSIONS: frozenset[str] = frozenset({".txt"})
MAX_FILE_SIZE_BYTES: int = 200 * 1024 * 1024  # 200 MB safety cap
UPLOAD_DIR_NAME: str = "uploads"

# --- Metric categorization ----------------------------------------------
# A metric is classified by matching its name against these prefixes.
# Order matters: first match wins. Extend these tuples to support new
# gem5 output sections without changing any parsing code.

SIMULATION_METRIC_PREFIXES: tuple[str, ...] = (
    "sim",
    "host",
)

CPU_METRIC_PREFIXES: tuple[str, ...] = (
    "system.cpu",
)

# --- Required metrics -----------------------------------------------------
# Used purely for validation / warnings. Absence of one of these does not
# stop parsing; it is reported as a warning in the response metadata.

REQUIRED_SIMULATION_METRICS: frozenset[str] = frozenset(
    {
        "simSeconds",
        "simTicks",
        "finalTick",
        "simFreq",
        "hostSeconds",
        "hostTickRate",
        "hostMemory",
        "simInsts",
        "simOps",
        "hostInstRate",
        "hostOpRate",
    }
)

REQUIRED_CPU_METRICS: frozenset[str] = frozenset(
    {
        "system.cpu.numCycles",
        "system.cpu.cpi",
        "system.cpu.ipc",
        "system.cpu.instsIssued",
        "system.cpu.instsAdded",
    }
)

ALL_REQUIRED_METRICS: frozenset[str] = REQUIRED_SIMULATION_METRICS | REQUIRED_CPU_METRICS

# --- Parsing ---------------------------------------------------------------

COMMENT_PREFIX: str = "#"
SEPARATOR_CHARS: frozenset[str] = frozenset({"-", "="})

# --- Cache ------------------------------------------------------------------

CACHE_TTL_SECONDS: int = 3600