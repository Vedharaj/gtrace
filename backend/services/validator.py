"""Validation layer for parsed metric data.

Checks for missing required metrics, duplicates (already flagged by the
extractor but re-surfaced here), invalid numeric values (NaN/Infinity),
divide-by-zero risk, and semantically impossible values such as negative
cycle counts. Produces human-readable warning/error messages rather than
raising, so a single bad metric doesn't block the whole response.
"""

from __future__ import annotations

from models.metric import Metric, ParsedStats, ParseWarning
from utils.constants import ALL_REQUIRED_METRICS
from utils.helpers import is_finite_number
from utils.logger import get_logger

logger = get_logger(__name__)

# Metrics that represent counts and must never be negative.
_NON_NEGATIVE_METRICS: frozenset[str] = frozenset(
    {
        "system.cpu.numCycles",
        "system.cpu.instsIssued",
        "system.cpu.instsAdded",
        "simTicks",
        "simInsts",
        "simOps",
    }
)


class MetricValidator:
    """Validates a ParsedStats object and reports issues as warnings.

    Single responsibility: data-quality checks. This class does not
    mutate the input; it returns a list of human-readable messages that
    the caller (API layer) can surface to the client.
    """

    def validate(self, parsed: ParsedStats) -> list[str]:
        """Run all validation checks against parsed stats.

        Args:
            parsed: The result of MetricExtractor.extract().

        Returns:
            A list of human-readable warning/error message strings.
            An empty list means no issues were found.
        """
        messages: list[str] = []
        messages.extend(self._check_missing_required(parsed.metrics))
        messages.extend(self._check_invalid_values(parsed.metrics))
        messages.extend(self._check_negative_cycles(parsed.metrics))
        messages.extend(w.message for w in parsed.warnings)
        return messages

    @staticmethod
    def _check_missing_required(metrics: dict[str, Metric]) -> list[str]:
        """Detect required metrics that are absent from the parsed set.

        Args:
            metrics: The extracted metrics mapping.

        Returns:
            Warning messages, one per missing required metric.
        """
        missing = ALL_REQUIRED_METRICS - metrics.keys()
        return [f"Missing required metric: '{name}'" for name in sorted(missing)]

    @staticmethod
    def _check_invalid_values(metrics: dict[str, Metric]) -> list[str]:
        """Detect NaN/Infinity values among parsed metrics.

        Args:
            metrics: The extracted metrics mapping.

        Returns:
            Warning messages for any metric with a non-finite value.
        """
        messages: list[str] = []
        for metric in metrics.values():
            if not is_finite_number(metric.value):
                messages.append(f"Metric '{metric.name}' has an invalid value: {metric.value}")
        return messages

    @staticmethod
    def _check_negative_cycles(metrics: dict[str, Metric]) -> list[str]:
        """Detect negative values for metrics that must be non-negative.

        Args:
            metrics: The extracted metrics mapping.

        Returns:
            Warning messages for any count-like metric with a negative
            value.
        """
        messages: list[str] = []
        for name in _NON_NEGATIVE_METRICS:
            metric = metrics.get(name)
            if metric is not None and is_finite_number(metric.value) and metric.value < 0:
                messages.append(f"Metric '{name}' has an impossible negative value: {metric.value}")
        return messages

    @staticmethod
    def check_divide_by_zero_risk(denominator_name: str, metrics: dict[str, Metric]) -> str | None:
        """Check whether a metric intended as a divisor is zero.

        Args:
            denominator_name: Name of the metric used as a divisor.
            metrics: The extracted metrics mapping.

        Returns:
            A warning message if the denominator is zero, else None.
        """
        metric = metrics.get(denominator_name)
        if metric is not None and metric.value == 0:
            return f"Potential divide-by-zero: '{denominator_name}' is 0"
        return None

    @staticmethod
    def to_parse_warnings(messages: list[str]) -> list[ParseWarning]:
        """Convert plain message strings into ParseWarning objects.

        Args:
            messages: List of human-readable warning strings.

        Returns:
            Corresponding ParseWarning objects (without line numbers).
        """
        return [ParseWarning(message=m) for m in messages]