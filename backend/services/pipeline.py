"""Analysis pipeline: orchestrates parsing, extraction, validation, and derivation.

Encapsulates the full workflow so API routes remain thin and never contain
business logic. The pipeline is stateless — construct one per request (or
reuse across requests if you prefer a singleton).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

from models.metric import ParsedStats
from services.calculator import MetricCalculator
from services.extractor import MetricExtractor
from services.parser import StatsParser
from services.validator import MetricValidator
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PipelineResult:
    """Holds the complete output of a single :class:`AnalysisPipeline` run.

    Attributes:
        parsed: The raw metrics extracted by the extractor.
        derived: Calculated/derived metric values (may contain ``None``
            for metrics whose calculation was not possible).
        warnings: Human-readable messages from parsing and validation.
        parse_time_seconds: Wall-clock seconds spent inside
            :meth:`AnalysisPipeline.run`.
    """

    parsed: ParsedStats
    derived: dict[str, float | None] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    parse_time_seconds: float = 0.0


class AnalysisPipeline:
    """Coordinates the full gem5 stats analysis workflow.

    Responsibilities (single-responsibility per collaborator):
      - :class:`~services.parser.StatsParser`: stream and filter raw lines.
      - :class:`~services.extractor.MetricExtractor`: produce typed Metrics.
      - :class:`~services.validator.MetricValidator`: surface data-quality
        issues.
      - :class:`~services.calculator.MetricCalculator`: compute derived
        metrics.

    Each collaborator is injected (or created internally) so the pipeline
    can be tested with mocks.
    """

    def __init__(
        self,
        validator: MetricValidator | None = None,
    ) -> None:
        """Initialize the pipeline with optional collaborator overrides.

        Args:
            validator: Optional :class:`MetricValidator` instance. A new
                instance is created when not provided.
        """
        self._validator = validator or MetricValidator()

    def run(self, file_path: Path) -> PipelineResult:
        """Execute the full analysis pipeline for *file_path*.

        Steps:
          1. Parse and extract metrics (single pass, O(n)).
          2. Validate data quality and collect warnings.
          3. Calculate derived metrics.

        Args:
            file_path: Absolute path to a gem5 stats.txt file on disk.

        Returns:
            A :class:`PipelineResult` populated with metrics, derived
            values, warnings, and timing information.

        Raises:
            FileNotFoundError: If *file_path* does not exist.
            OSError: If the file cannot be read.
        """
        logger.info("Pipeline started: %s", file_path)
        start = time.perf_counter()

        parser = StatsParser(file_path)
        extractor = MetricExtractor(parser)
        parsed = extractor.extract()

        validation_warnings = self._validator.validate(parsed)

        calculator = MetricCalculator(parsed.metrics)
        derived = calculator.calculate_all()

        elapsed = time.perf_counter() - start
        logger.info(
            "Pipeline finished: %.4fs, %d metrics, %d warnings",
            elapsed,
            len(parsed.metrics),
            len(validation_warnings),
        )

        return PipelineResult(
            parsed=parsed,
            derived=derived,
            warnings=validation_warnings,
            parse_time_seconds=elapsed,
        )
