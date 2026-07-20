"""Compiled regular expressions for gem5 ``stats.txt`` parsing.

All patterns are compiled once at import time so the parser never pays
compilation cost inside its hot loop (single-pass, O(n) parsing).

A gem5 stats line generally looks like one of the following::

    system.cpu.numCycles                              614665
    simSeconds                        0.000307         # Number of seconds simulated
    system.cpu.ipc                    1.234500e+00     # IPC

i.e. ``<metric_name>  <value>  [# <description>]``. The value may be an
integer, a float, or scientific notation. A trailing unit is sometimes
embedded in the description (e.g. "(Hz)"); we extract it opportunistically.
"""

from __future__ import annotations

import re

# Matches a numeric token: integer, float, or scientific notation.
# Also tolerates gem5's special tokens for undefined/NaN values.
_NUMBER_PATTERN = r"[-+]?(?:\d+\.\d+(?:[eE][-+]?\d+)?|\d+(?:[eE][-+]?\d+)?|nan|inf|-inf)"

# Full line pattern:
#   group 1: metric name (dotted identifier, no whitespace)
#   group 2: numeric value (int / float / scientific notation / nan / inf)
#   group 3: optional trailing comment/description (after '#')
METRIC_LINE_PATTERN: re.Pattern[str] = re.compile(
    r"^\s*(?P<name>[A-Za-z0-9_:.\[\]<>]+)\s+"
    rf"(?P<value>{_NUMBER_PATTERN})"
    r"(?:\s+(?:\d+(?:\.\d+)?\s+)?#\s*(?P<description>.*))?\s*$",
    re.IGNORECASE,
)

# A "unit" is often embedded in parentheses within the description, e.g.
# "Simulated seconds (s)" or "Clock rate (Hz)".
UNIT_PATTERN: re.Pattern[str] = re.compile(r"\(([^()]+)\)\s*$")

# A separator line is a run of dashes/equals signs, e.g. "---------- Begin Simulation Statistics ----------"
SEPARATOR_LINE_PATTERN: re.Pattern[str] = re.compile(r"^[\s\-=]*$|^-{2,}.*-{2,}$")

# Lines that mark the begin/end of a stats dump; useful metadata but not metrics.
BEGIN_DUMP_PATTERN: re.Pattern[str] = re.compile(r"Begin Simulation Statistics", re.IGNORECASE)
END_DUMP_PATTERN: re.Pattern[str] = re.compile(r"End Simulation Statistics", re.IGNORECASE)