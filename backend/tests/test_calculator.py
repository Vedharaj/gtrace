"""Unit tests for MetricCalculator."""

from __future__ import annotations

import math

import pytest

from models.metric import Metric, MetricCategory
from services.calculator import MetricCalculator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_metric(name: str, value: float) -> Metric:
    """Create a minimal Metric for test use."""
    return Metric(name=name, value=value, category=MetricCategory.CPU)


def _calc(overrides: dict[str, float] | None = None) -> MetricCalculator:
    """Build a MetricCalculator pre-loaded with a standard set of metrics.

    Args:
        overrides: Additional or replacement metrics to add/override.

    Returns:
        A MetricCalculator instance.
    """
    base: dict[str, float] = {
        "system.cpu.numCycles": 1000.0,
        "system.cpu.instsIssued": 800.0,
        "system.cpu.instsAdded": 760.0,
        "simSeconds": 0.001,
        "hostInstRate": 500000.0,
    }
    if overrides:
        base.update(overrides)
    metrics = {name: _make_metric(name, v) for name, v in base.items()}
    return MetricCalculator(metrics)


# ---------------------------------------------------------------------------
# IPC
# ---------------------------------------------------------------------------


def test_calculate_ipc_uses_reported_value() -> None:
    """Prefers ``system.cpu.ipc`` when it is present."""
    calc = _calc({"system.cpu.ipc": 2.5})
    assert calc.calculate_ipc() == pytest.approx(2.5)


def test_calculate_ipc_derived_from_insts_and_cycles() -> None:
    """Falls back to instsIssued / numCycles when reported IPC is absent."""
    calc = _calc()  # no ipc key
    # 800 / 1000 = 0.8
    assert calc.calculate_ipc() == pytest.approx(0.8)


def test_calculate_ipc_returns_none_when_missing_inputs() -> None:
    """Returns None when neither ipc nor the required inputs are present."""
    calc = MetricCalculator({})
    assert calc.calculate_ipc() is None


def test_calculate_ipc_returns_none_on_zero_cycles() -> None:
    """Returns None when numCycles is zero (avoid divide-by-zero)."""
    calc = _calc({"system.cpu.numCycles": 0.0})
    assert calc.calculate_ipc() is None


# ---------------------------------------------------------------------------
# CPI
# ---------------------------------------------------------------------------


def test_calculate_cpi_uses_reported_value() -> None:
    """Prefers ``system.cpu.cpi`` when it is present."""
    calc = _calc({"system.cpu.cpi": 1.25})
    assert calc.calculate_cpi() == pytest.approx(1.25)


def test_calculate_cpi_derived_from_cycles_and_insts() -> None:
    """Falls back to numCycles / instsIssued when reported CPI is absent."""
    calc = _calc()
    # 1000 / 800 = 1.25
    assert calc.calculate_cpi() == pytest.approx(1.25)


def test_calculate_cpi_returns_none_on_zero_insts() -> None:
    """Returns None when instsIssued is zero (avoid divide-by-zero)."""
    calc = _calc({"system.cpu.instsIssued": 0.0})
    assert calc.calculate_cpi() is None


# ---------------------------------------------------------------------------
# Execution time
# ---------------------------------------------------------------------------


def test_calculate_execution_time_returns_simSeconds() -> None:
    """Returns simSeconds directly."""
    calc = _calc({"simSeconds": 0.005})
    assert calc.calculate_execution_time() == pytest.approx(0.005)


def test_calculate_execution_time_returns_none_when_absent() -> None:
    """Returns None when simSeconds is not present."""
    calc = MetricCalculator({})
    assert calc.calculate_execution_time() is None


# ---------------------------------------------------------------------------
# Busy cycles
# ---------------------------------------------------------------------------


def test_calculate_busy_cycles() -> None:
    """busy_cycles = instsAdded * cpi = 760 * (1000/800) = 950."""
    calc = _calc()
    expected = 760.0 * (1000.0 / 800.0)
    assert calc.calculate_busy_cycles() == pytest.approx(expected)


def test_calculate_busy_cycles_returns_none_when_missing() -> None:
    """Returns None when required metrics are absent."""
    calc = MetricCalculator({})
    assert calc.calculate_busy_cycles() is None


# ---------------------------------------------------------------------------
# Idle percentage
# ---------------------------------------------------------------------------


def test_calculate_idle_percentage_bounded() -> None:
    """Idle percentage must be in [0, 100]."""
    calc = _calc()
    idle = calc.calculate_idle_percentage()
    assert idle is not None
    assert 0.0 <= idle <= 100.0


def test_calculate_idle_percentage_returns_none_when_missing() -> None:
    """Returns None when numCycles or busy_cycles cannot be computed."""
    calc = MetricCalculator({})
    assert calc.calculate_idle_percentage() is None


def test_calculate_idle_percentage_zero_when_fully_busy() -> None:
    """Idle percentage is 0% when instsAdded == instsIssued and CPI == 1."""
    calc = _calc(
        {
            "system.cpu.numCycles": 1000.0,
            "system.cpu.instsIssued": 1000.0,
            "system.cpu.instsAdded": 1000.0,
        }
    )
    idle = calc.calculate_idle_percentage()
    assert idle is not None
    assert idle == pytest.approx(0.0, abs=1e-6)


# ---------------------------------------------------------------------------
# Instruction efficiency
# ---------------------------------------------------------------------------


def test_calculate_instruction_efficiency_ratio() -> None:
    """efficiency = instsAdded / instsIssued = 760 / 800 = 0.95."""
    calc = _calc()
    assert calc.calculate_instruction_efficiency() == pytest.approx(0.95)


def test_calculate_instruction_efficiency_returns_none_on_zero_issued() -> None:
    """Returns None when instsIssued is zero."""
    calc = _calc({"system.cpu.instsIssued": 0.0})
    assert calc.calculate_instruction_efficiency() is None


# ---------------------------------------------------------------------------
# Host speed
# ---------------------------------------------------------------------------


def test_calculate_host_speed_returns_hostInstRate() -> None:
    """Returns hostInstRate directly."""
    calc = _calc()
    assert calc.calculate_host_speed() == pytest.approx(500000.0)


def test_calculate_host_speed_returns_none_when_absent() -> None:
    """Returns None when hostInstRate is not present."""
    calc = MetricCalculator({})
    assert calc.calculate_host_speed() is None


# ---------------------------------------------------------------------------
# CPU utilization
# ---------------------------------------------------------------------------


def test_calculate_cpu_utilization_is_complement_of_idle() -> None:
    """cpu_utilization == 100 - idle_percentage."""
    calc = _calc()
    idle = calc.calculate_idle_percentage()
    util = calc.calculate_cpu_utilization()
    assert idle is not None and util is not None
    assert util == pytest.approx(100.0 - idle)


def test_calculate_cpu_utilization_clamped_to_100() -> None:
    """CPU utilization is clamped to [0, 100]."""
    calc = _calc()
    util = calc.calculate_cpu_utilization()
    assert util is not None
    assert 0.0 <= util <= 100.0


# ---------------------------------------------------------------------------
# calculate_all
# ---------------------------------------------------------------------------


def test_calculate_all_returns_all_keys() -> None:
    """calculate_all returns a dict with every expected derived key."""
    expected_keys = {
        "ipc",
        "cpi",
        "executionTimeSeconds",
        "busyCycles",
        "idlePercentage",
        "instructionEfficiency",
        "hostSpeedInstsPerSec",
        "cpuUtilizationPercentage",
    }
    calc = _calc()
    results = calc.calculate_all()
    assert expected_keys == set(results.keys())


def test_calculate_all_handles_empty_metrics_gracefully() -> None:
    """calculate_all returns None values (not exceptions) for missing metrics."""
    calc = MetricCalculator({})
    results = calc.calculate_all()
    assert all(v is None for v in results.values())


def test_calculate_all_no_nan_for_finite_inputs() -> None:
    """Derived values must not be NaN when inputs are valid finite numbers."""
    calc = _calc()
    results = calc.calculate_all()
    for name, val in results.items():
        if val is not None:
            assert math.isfinite(val), f"Non-finite value for derived metric '{name}': {val}"
