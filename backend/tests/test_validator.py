"""Unit tests for MetricValidator."""

from __future__ import annotations

import math

import pytest

from models.metric import Metric, MetricCategory, ParsedStats, ParseWarning
from services.validator import MetricValidator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_metric(name: str, value: float, category: MetricCategory = MetricCategory.OTHER) -> Metric:
    """Create a Metric with the given name and value."""
    return Metric(name=name, value=value, category=category)


def _full_stats() -> ParsedStats:
    """Return a ParsedStats with all required metrics populated."""
    required_sim = {
        "simSeconds": 0.000307,
        "simTicks": 307332500.0,
        "finalTick": 307332500.0,
        "simFreq": 1e12,
        "hostSeconds": 1.23,
        "hostTickRate": 249863008.0,
        "hostMemory": 1572864.0,
        "simInsts": 614665.0,
        "simOps": 614665.0,
        "hostInstRate": 499728.0,
        "hostOpRate": 499728.0,
    }
    required_cpu = {
        "system.cpu.numCycles": 614665.0,
        "system.cpu.cpi": 1.0,
        "system.cpu.ipc": 1.0,
        "system.cpu.instsIssued": 614665.0,
        "system.cpu.instsAdded": 614665.0,
    }
    all_values = {**required_sim, **required_cpu}
    return ParsedStats(
        metrics={name: _make_metric(name, v) for name, v in all_values.items()}
    )


# ---------------------------------------------------------------------------
# Missing required metrics
# ---------------------------------------------------------------------------


def test_no_warnings_when_all_required_present() -> None:
    """A fully populated ParsedStats produces zero validation warnings."""
    validator = MetricValidator()
    warnings = validator.validate(_full_stats())
    # Filter only missing-metric messages to be precise.
    missing = [w for w in warnings if w.startswith("Missing required metric")]
    assert missing == []


def test_missing_single_required_metric_warns() -> None:
    """A single absent required metric generates exactly one warning."""
    stats = _full_stats()
    del stats.metrics["simSeconds"]
    validator = MetricValidator()
    warnings = validator.validate(stats)
    missing = [w for w in warnings if "simSeconds" in w]
    assert len(missing) == 1


def test_missing_multiple_required_metrics_warns_each() -> None:
    """Each missing required metric produces its own warning."""
    stats = _full_stats()
    del stats.metrics["simSeconds"]
    del stats.metrics["system.cpu.numCycles"]
    validator = MetricValidator()
    warnings = validator.validate(stats)
    assert any("simSeconds" in w for w in warnings)
    assert any("system.cpu.numCycles" in w for w in warnings)


def test_missing_all_required_metrics() -> None:
    """An empty ParsedStats produces a warning for every required metric."""
    from utils.constants import ALL_REQUIRED_METRICS

    validator = MetricValidator()
    warnings = validator.validate(ParsedStats())
    missing_msgs = [w for w in warnings if w.startswith("Missing required metric")]
    assert len(missing_msgs) == len(ALL_REQUIRED_METRICS)


# ---------------------------------------------------------------------------
# Invalid values (NaN / Infinity)
# ---------------------------------------------------------------------------


def test_nan_value_generates_warning() -> None:
    """A metric with a NaN value generates an invalid-value warning."""
    stats = _full_stats()
    stats.metrics["simSeconds"] = _make_metric("simSeconds", math.nan)
    validator = MetricValidator()
    warnings = validator.validate(stats)
    invalid = [w for w in warnings if "simSeconds" in w and "invalid value" in w]
    assert len(invalid) >= 1


def test_inf_value_generates_warning() -> None:
    """A metric with an Infinity value generates an invalid-value warning."""
    stats = _full_stats()
    stats.metrics["simSeconds"] = _make_metric("simSeconds", math.inf)
    validator = MetricValidator()
    warnings = validator.validate(stats)
    assert any("simSeconds" in w for w in warnings)


def test_neg_inf_value_generates_warning() -> None:
    """A metric with a -Infinity value generates an invalid-value warning."""
    stats = _full_stats()
    stats.metrics["simSeconds"] = _make_metric("simSeconds", -math.inf)
    validator = MetricValidator()
    warnings = validator.validate(stats)
    assert any("simSeconds" in w for w in warnings)


# ---------------------------------------------------------------------------
# Negative cycles
# ---------------------------------------------------------------------------


def test_negative_cycles_generates_warning() -> None:
    """A negative numCycles value generates a negative-value warning."""
    stats = _full_stats()
    stats.metrics["system.cpu.numCycles"] = _make_metric("system.cpu.numCycles", -100.0)
    validator = MetricValidator()
    warnings = validator.validate(stats)
    negative_msgs = [w for w in warnings if "negative" in w.lower() and "numCycles" in w]
    assert len(negative_msgs) == 1


def test_negative_simInsts_generates_warning() -> None:
    """A negative simInsts value generates a negative-value warning."""
    stats = _full_stats()
    stats.metrics["simInsts"] = _make_metric("simInsts", -1.0)
    validator = MetricValidator()
    warnings = validator.validate(stats)
    assert any("simInsts" in w for w in warnings)


def test_zero_cycles_does_not_generate_negative_warning() -> None:
    """Zero is valid (not negative); no negative-cycles warning expected."""
    stats = _full_stats()
    stats.metrics["system.cpu.numCycles"] = _make_metric("system.cpu.numCycles", 0.0)
    validator = MetricValidator()
    warnings = validator.validate(stats)
    negative_msgs = [w for w in warnings if "negative" in w.lower() and "numCycles" in w]
    assert negative_msgs == []


# ---------------------------------------------------------------------------
# Divide-by-zero risk
# ---------------------------------------------------------------------------


def test_divide_by_zero_risk_detected() -> None:
    """check_divide_by_zero_risk returns a message when the metric is 0."""
    stats = _full_stats()
    stats.metrics["system.cpu.numCycles"] = _make_metric("system.cpu.numCycles", 0.0)
    msg = MetricValidator.check_divide_by_zero_risk("system.cpu.numCycles", stats.metrics)
    assert msg is not None
    assert "divide-by-zero" in msg.lower()


def test_divide_by_zero_risk_clear_when_nonzero() -> None:
    """check_divide_by_zero_risk returns None when the metric is non-zero."""
    stats = _full_stats()
    msg = MetricValidator.check_divide_by_zero_risk("system.cpu.numCycles", stats.metrics)
    assert msg is None


def test_divide_by_zero_risk_clear_when_absent() -> None:
    """check_divide_by_zero_risk returns None when the metric is absent."""
    msg = MetricValidator.check_divide_by_zero_risk("nonexistent_metric", {})
    assert msg is None


# ---------------------------------------------------------------------------
# Parse warnings propagation
# ---------------------------------------------------------------------------


def test_parse_warnings_propagated_into_validate() -> None:
    """Existing ParseWarnings on the ParsedStats are included in the output."""
    stats = _full_stats()
    stats.warnings.append(ParseWarning(message="Malformed line detected"))
    validator = MetricValidator()
    warnings = validator.validate(stats)
    assert any("Malformed" in w for w in warnings)


def test_to_parse_warnings_converts_strings() -> None:
    """to_parse_warnings wraps plain strings into ParseWarning objects."""
    messages = ["Warning A", "Warning B"]
    result = MetricValidator.to_parse_warnings(messages)
    assert len(result) == 2
    assert all(isinstance(w, ParseWarning) for w in result)
    assert result[0].message == "Warning A"
    assert result[1].message == "Warning B"
