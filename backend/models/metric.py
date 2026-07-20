"""Core data structures for parsed gem5 metrics.

Defines the canonical, low-level types produced by the parser and
extractor layers. These types contain no Pydantic dependencies so they
can be imported freely throughout the service layer without pulling in
the heavier validation machinery.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class MetricCategory(str, Enum):
    """Logical category for a parsed metric.

    Attributes:
        SIMULATION: Simulation-level statistics (simSeconds, simTicks, …).
        CPU: Per-CPU statistics (system.cpu.*).
        OTHER: Any metric that does not match a known category prefix.
    """

    SIMULATION = "simulation"
    CPU = "cpu"
    OTHER = "other"


@dataclass(slots=True)
class Metric:
    """A single metric extracted from a gem5 stats.txt line.

    Attributes:
        name: Exact metric name as it appears in the file
            (e.g. ``system.cpu.numCycles``).
        value: Numeric value; may be NaN or ±Inf for pathological inputs.
        description: Optional description/comment text following ``#``.
        unit: Optional unit string extracted from parentheses in the
            description (e.g. ``"s"``, ``"Hz"``).
        category: Logical grouping inferred from the metric name prefix.
    """

    name: str
    value: float
    description: str = ""
    unit: str = ""
    category: MetricCategory = MetricCategory.OTHER


@dataclass(slots=True)
class ParseWarning:
    """A non-fatal parsing or validation issue.

    Attributes:
        message: Human-readable description of the issue.
        line_number: 1-indexed source line number, or None for file-level
            warnings.
    """

    message: str
    line_number: int | None = None

    def __str__(self) -> str:
        """Return a human-readable string representation.

        Returns:
            A formatted warning string including line number if available.
        """
        if self.line_number is not None:
            return f"[line {self.line_number}] {self.message}"
        return self.message


@dataclass
class ParsedStats:
    """Container holding all metrics and warnings from a single parse run.

    Attributes:
        metrics: Mapping from metric name to :class:`Metric` instance.
            Dictionary lookup is O(1); iteration order matches insertion.
        warnings: Non-fatal issues encountered during parsing.
        line_count: Total number of meaningful (non-blank, non-comment,
            non-separator) lines that were processed.
    """

    metrics: dict[str, Metric] = field(default_factory=dict)
    warnings: list[ParseWarning] = field(default_factory=list)
    line_count: int = 0