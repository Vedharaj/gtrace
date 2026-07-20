"""Pydantic output schemas for categorized metric data.

These models represent the *per-category* sections of the API response.
They are intentionally separate from the raw :class:`~models.metric.Metric`
dataclass so that formatting concerns (serialization, field aliases, etc.)
stay out of the parsing layer.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class MetricOut(BaseModel):
    """Serializable representation of a single extracted metric.

    Attributes:
        name: Exact metric name (e.g. ``system.cpu.numCycles``).
        value: Numeric value. ``None`` is used when a metric is present
            but its value could not be meaningfully represented.
        description: Optional description/comment from the source file.
        unit: Optional unit string (e.g. ``"s"``, ``"Hz"``).
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    value: float | None
    description: str = ""
    unit: str = ""


class SimulationStats(BaseModel):
    """Simulation-category metrics section of the API response.

    Attributes:
        metrics: Ordered mapping of metric name -> :class:`MetricOut`.
    """

    metrics: dict[str, MetricOut] = {}

    def to_dict(self) -> dict[str, dict]:
        """Serialize each metric to a plain dict, keyed by metric name.

        Returns:
            A JSON-serializable dictionary of metric name -> metric fields.
        """
        return {name: m.model_dump() for name, m in self.metrics.items()}


class CpuStats(BaseModel):
    """CPU-category metrics section of the API response.

    Attributes:
        metrics: Ordered mapping of metric name -> :class:`MetricOut`.
    """

    metrics: dict[str, MetricOut] = {}

    def to_dict(self) -> dict[str, dict]:
        """Serialize each metric to a plain dict, keyed by metric name.

        Returns:
            A JSON-serializable dictionary of metric name -> metric fields.
        """
        return {name: m.model_dump() for name, m in self.metrics.items()}


class DerivedStats(BaseModel):
    """Derived (calculated) metrics section of the API response.

    Attributes:
        values: Mapping of derived metric name -> computed float value
            (``None`` if the calculation could not be performed).
    """

    values: dict[str, float | None] = {}

    def to_dict(self) -> dict[str, float | None]:
        """Return the values dict directly for JSON serialization.

        Returns:
            The derived metric name -> value mapping.
        """
        return dict(self.values)
