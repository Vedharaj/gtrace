"""
parser.py

`StatisticsCollector` parses gem5's stats.txt output (a simple
"key   value   # description" text format) into a dictionary, and extracts
the handful of fields (sim_ticks, sim_seconds, instructions) that are
promoted into metadata.json. Kept separate from Gem5Runner because parsing
output is a different concern from producing it, and this module is the
natural place to extend for future visualization/analysis tooling.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from logger import get_logger

logger = get_logger("gtrace.parser")

# gem5 stats.txt lines look like:
#   system.cpu.numCycles                      1234567     # Number of cpu cycles simulated
_STAT_LINE_RE = re.compile(r"^(?P<key>\S+)\s+(?P<value>[-+0-9.eE]+)\b")


class StatisticsCollector:
    """Parses gem5 stats.txt files into a flat dict[str, float]."""

    @staticmethod
    def parse_stats_file(stats_path: Path) -> dict[str, float]:
        stats: dict[str, float] = {}
        if not stats_path.exists():
            logger.debug("stats.txt not found at %s", stats_path)
            return stats

        try:
            with stats_path.open(errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("---"):
                        continue
                    match = _STAT_LINE_RE.match(line)
                    if not match:
                        continue
                    try:
                        stats[match.group("key")] = float(match.group("value"))
                    except ValueError:
                        continue
        except OSError as exc:
            logger.warning("Failed to read stats.txt (%s): %s", stats_path, exc)

        return stats

    @staticmethod
    def extract_sim_ticks(stats: dict[str, float]) -> Optional[int]:
        for key in ("sim_ticks", "simTicks", "system.sim_ticks"):
            if key in stats:
                return int(stats[key])
        return None

    @staticmethod
    def extract_sim_seconds(stats: dict[str, float]) -> Optional[float]:
        for key in ("sim_seconds", "system.sim_seconds"):
            if key in stats:
                return stats[key]
        return None

    @staticmethod
    def extract_instructions(stats: dict[str, float]) -> Optional[int]:
        for key in ("sim_insts", "system.cpu.committedInsts", "simInsts"):
            if key in stats:
                return int(stats[key])
        return None

    @classmethod
    def summarize(cls, stats_path: Path) -> dict[str, Optional[float]]:
        """Convenience wrapper returning just the fields metadata.json needs."""
        stats = cls.parse_stats_file(stats_path)
        return {
            "sim_ticks": cls.extract_sim_ticks(stats),
            "sim_seconds": cls.extract_sim_seconds(stats),
            "sim_insts": cls.extract_instructions(stats),
            "raw_stat_count": len(stats),
        }