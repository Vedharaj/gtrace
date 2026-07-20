"""Generic, regex-driven extraction of metrics from parsed stats lines.

The extractor never hardcodes metric names. Any line matching the
generic ``METRIC_LINE_PATTERN`` becomes a :class:`~models.metric.Metric`
automatically, which means new gem5 metrics appear in API responses
without any code changes here.
"""

from __future__ import annotations

from models.metric import Metric, MetricCategory, ParsedStats, ParseWarning
from services.parser import StatsParser
from utils.constants import CPU_METRIC_PREFIXES, SIMULATION_METRIC_PREFIXES
from utils.helpers import is_finite_number, safe_float
from utils.logger import get_logger
from utils.regex import METRIC_LINE_PATTERN, UNIT_PATTERN

logger = get_logger(__name__)


class MetricExtractor:
    """Extracts and categorizes :class:`Metric` objects from a stats file.

    Single responsibility: turn cleaned text lines into typed, categorized
    Metric objects. Delegates raw line iteration to :class:`StatsParser`.
    """

    def __init__(self, parser: StatsParser) -> None:
        """Initialize the extractor with a parser to source lines from.

        Args:
            parser: A StatsParser bound to the target file.
        """
        self._parser = parser

    def extract(self) -> ParsedStats:
        """Run extraction over the whole file in a single pass.

        Returns:
            A ParsedStats object containing all extracted metrics and any
            non-fatal warnings encountered (e.g. malformed lines,
            duplicate metric names).
        """
        result = ParsedStats()

        empty_warning = self._parser.validate_not_empty()
        if empty_warning is not None:
            result.warnings.append(empty_warning)
            return result

        for line_number, line in self._parser.iter_lines():
            result.line_count += 1
            metric = self._parse_line(line, line_number, result.warnings)
            if metric is None:
                continue

            if metric.name in result.metrics:
                result.warnings.append(
                    ParseWarning(
                        message=f"Duplicate metric '{metric.name}' overwritten with later value",
                        line_number=line_number,
                    )
                )
            result.metrics[metric.name] = metric

        logger.info(
            "Extraction complete: %d lines read, %d metrics found, %d warnings",
            result.line_count,
            len(result.metrics),
            len(result.warnings),
        )
        return result

    def _parse_line(
        self, line: str, line_number: int, warnings: list[ParseWarning]
    ) -> Metric | None:
        """Parse a single line into a Metric, recording warnings on failure.

        Args:
            line: The cleaned line text.
            line_number: 1-indexed source line number, for diagnostics.
            warnings: List to append any ParseWarning to.

        Returns:
            A Metric instance, or None if the line could not be parsed
            or the value was invalid (NaN/Infinity).
        """
        match = METRIC_LINE_PATTERN.match(line)
        if match is None:
            warnings.append(
                ParseWarning(message=f"Malformed metric line: '{line}'", line_number=line_number)
            )
            return None

        name = match.group("name")
        raw_value = match.group("value")
        description = (match.group("description") or "").strip()

        try:
            value = safe_float(raw_value)
        except ValueError:
            warnings.append(
                ParseWarning(
                    message=f"Unparseable numeric value for '{name}': '{raw_value}'",
                    line_number=line_number,
                )
            )
            return None

        if not is_finite_number(value):
            warnings.append(
                ParseWarning(
                    message=f"Non-finite value for '{name}' (NaN/Infinity) — kept but flagged",
                    line_number=line_number,
                )
            )

        unit_match = UNIT_PATTERN.search(description)
        unit = unit_match.group(1) if unit_match else ""

        return Metric(
            name=name,
            value=value,
            description=description,
            unit=unit,
            category=self._categorize(name),
        )

    @staticmethod
    def _categorize(name: str) -> MetricCategory:
        """Classify a metric name into a category using prefix rules.

        Args:
            name: The exact metric name.

        Returns:
            The matching MetricCategory. CPU prefixes are checked before
            simulation prefixes since "system.cpu.*" is more specific
            than the broad "sim"/"host" prefixes.
        """
        if any(name.startswith(prefix) for prefix in CPU_METRIC_PREFIXES):
            return MetricCategory.CPU
        if any(name.startswith(prefix) for prefix in SIMULATION_METRIC_PREFIXES):
            return MetricCategory.SIMULATION
        return MetricCategory.OTHER