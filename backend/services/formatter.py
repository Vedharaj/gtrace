"""Formats parsed/derived metrics into the final API response shape."""

from __future__ import annotations

import math

from datetime import UTC, datetime

from models.metric import MetricCategory, ParsedStats
from models.response import MetricsResponse, ResponseMetadata
from models.stats import CpuStats, DerivedStats, MetricOut, SimulationStats
from utils.logger import get_logger

logger = get_logger(__name__)


class ResponseFormatter:
    """Builds structured, client-ready response objects.

    Single responsibility: shaping data for output. This class performs
    no parsing, extraction, or calculation — it only assembles already
    computed values into the documented response schema.
    """

    def build_metrics_response(
        self,
        file_name: str,
        parsed: ParsedStats,
        derived: dict[str, float | None],
        warnings: list[str],
        parse_time_seconds: float,
    ) -> MetricsResponse:
        """Assemble the full /metrics/<file_id> response.

        Args:
            file_name: Original uploaded file name.
            parsed: The ParsedStats produced by MetricExtractor.
            derived: The derived metrics computed by MetricCalculator.
            warnings: Human-readable validation/parsing warning messages.
            parse_time_seconds: Wall-clock time spent parsing, in seconds.

        Returns:
            A fully populated MetricsResponse ready for JSON
            serialization.
        """
        simulation = self._filter_by_category(parsed, MetricCategory.SIMULATION)
        cpu = self._filter_by_category(parsed, MetricCategory.CPU)

        sanitized_derived = {
            k: (v if (v is not None and math.isfinite(v)) else None)
            for k, v in derived.items()
        }
        derived_stats = DerivedStats(values=sanitized_derived)

        metadata = ResponseMetadata(
            fileName=file_name,
            parseTime=f"{parse_time_seconds:.6f}s",
            metricCount=len(parsed.metrics),
            warnings=warnings,
        )

        return MetricsResponse(
            simulation=simulation.to_dict(),
            cpu=cpu.to_dict(),
            derived=derived_stats.to_dict(),
            metadata=metadata,
        )

    @staticmethod
    def _filter_by_category(parsed: ParsedStats, category: MetricCategory) -> SimulationStats | CpuStats:
        """Filter parsed metrics down to a single category.

        Args:
            parsed: The full ParsedStats object.
            category: The category to filter for.

        Returns:
            A SimulationStats or CpuStats container holding only metrics
            matching ``category``.
        """
        filtered = {
            name: MetricOut(
                name=m.name,
                value=(m.value if (m.value is not None and math.isfinite(m.value)) else None),
                description=m.description,
                unit=m.unit
            )
            for name, m in parsed.metrics.items()
            if m.category == category
        }
        if category == MetricCategory.CPU:
            return CpuStats(metrics=filtered)
        return SimulationStats(metrics=filtered)

    @staticmethod
    def current_timestamp() -> str:
        """Return the current UTC timestamp in ISO-8601 format.

        Returns:
            An ISO-8601 formatted timestamp string.
        """
        return datetime.now(UTC).isoformat()