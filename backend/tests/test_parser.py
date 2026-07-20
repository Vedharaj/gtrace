"""Tests for StatsParser and MetricExtractor."""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from models.metric import MetricCategory
from services.extractor import MetricExtractor
from services.parser import StatsParser


def test_parser_streams_meaningful_lines(sample_stats_path: Path) -> None:
    parser = StatsParser(sample_stats_path)
    lines = list(parser.iter_lines())
    assert len(lines) > 0
    # Comment-only and separator lines must be excluded.
    assert all(not text.startswith("#") for _, text in lines)


def test_parser_missing_file_raises(tmp_path: Path) -> None:
    parser = StatsParser(tmp_path / "does_not_exist.txt")
    with pytest.raises(FileNotFoundError):
        list(parser.iter_lines())


def test_parser_empty_file_warning(tmp_path: Path) -> None:
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("")
    parser = StatsParser(empty_file)
    warning = parser.validate_not_empty()
    assert warning is not None
    assert "empty" in warning.message.lower()


def test_extractor_finds_required_metrics(sample_stats_path: Path) -> None:
    extractor = MetricExtractor(StatsParser(sample_stats_path))
    parsed = extractor.extract()
    assert "simSeconds" in parsed.metrics
    assert "system.cpu.numCycles" in parsed.metrics
    assert parsed.metrics["system.cpu.numCycles"].value == 614665


def test_extractor_categorizes_metrics(sample_stats_path: Path) -> None:
    extractor = MetricExtractor(StatsParser(sample_stats_path))
    parsed = extractor.extract()
    assert parsed.metrics["simSeconds"].category == MetricCategory.SIMULATION
    assert parsed.metrics["system.cpu.numCycles"].category == MetricCategory.CPU


def test_extractor_flags_malformed_lines(sample_stats_path: Path) -> None:
    extractor = MetricExtractor(StatsParser(sample_stats_path))
    parsed = extractor.extract()
    assert any("Malformed" in w.message for w in parsed.warnings)


def test_extractor_new_metric_auto_discovered(sample_stats_path: Path) -> None:
    """A metric never explicitly required (dcache hits) is still extracted."""
    extractor = MetricExtractor(StatsParser(sample_stats_path))
    parsed = extractor.extract()
    assert "system.cpu.dcache.overallHits::total" in parsed.metrics


def test_extractor_handles_scientific_notation(tmp_path: Path) -> None:
    stats_file = tmp_path / "sci.txt"
    stats_file.write_text("system.cpu.ipc    1.234500e+00    # IPC\n")
    extractor = MetricExtractor(StatsParser(stats_file))
    parsed = extractor.extract()
    assert math.isclose(parsed.metrics["system.cpu.ipc"].value, 1.2345)


def test_extractor_duplicate_metric_warns(tmp_path: Path) -> None:
    stats_file = tmp_path / "dup.txt"
    stats_file.write_text("simInsts 100\nsimInsts 200\n")
    extractor = MetricExtractor(StatsParser(stats_file))
    parsed = extractor.extract()
    assert parsed.metrics["simInsts"].value == 200
    assert any("Duplicate" in w.message for w in parsed.warnings)


def test_extractor_empty_file(tmp_path: Path) -> None:
    stats_file = tmp_path / "empty.txt"
    stats_file.write_text("")
    extractor = MetricExtractor(StatsParser(stats_file))
    parsed = extractor.extract()
    assert parsed.metrics == {}
    assert len(parsed.warnings) == 1