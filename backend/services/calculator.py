"""Reusable derived-metric calculations.

All arithmetic that combines raw parsed metrics into higher-level,
derived statistics lives here — never inside API routes. Each function
is pure: it takes primitive inputs and returns a single float (or None
when the calculation is not possible, e.g. divide-by-zero or missing
inputs).
"""

from __future__ import annotations

from models.metric import Metric
from utils.helpers import safe_divide
from utils.logger import get_logger

logger = get_logger(__name__)


class MetricCalculator:
    """Computes derived metrics from a dictionary of parsed Metrics.

    Single responsibility: derived-metric arithmetic. This class reads
    from the raw metrics mapping and produces named, calculated values;
    it never mutates its inputs.
    """

    def __init__(self, metrics: dict[str, Metric]) -> None:
        """Initialize the calculator with the full set of parsed metrics.

        Args:
            metrics: Mapping of metric name -> Metric, as produced by
                MetricExtractor.
        """
        self._metrics = metrics

    def _value(self, name: str) -> float | None:
        """Look up a metric's numeric value by exact name.

        Args:
            name: The exact metric name to look up.

        Returns:
            The metric's value, or None if the metric is not present.
        """
        metric = self._metrics.get(name)
        return metric.value if metric is not None else None

    def calculate_ipc(self) -> float | None:
        """Instructions per cycle = instsIssued / numCycles (or use parsed ipc).

        Returns:
            The IPC value, preferring the directly-reported metric if
            present, otherwise deriving it from instructions and cycles.
        """
        reported = self._value("system.cpu.ipc")
        if reported is not None:
            return reported
        insts = self._value("system.cpu.instsIssued")
        cycles = self._value("system.cpu.numCycles")
        if insts is None or cycles is None:
            return None
        return safe_divide(insts, cycles)

    def calculate_cpi(self) -> float | None:
        """Cycles per instruction = numCycles / instsIssued (or use parsed cpi).

        Returns:
            The CPI value, preferring the directly-reported metric,
            otherwise derived from cycles and instructions.
        """
        reported = self._value("system.cpu.cpi")
        if reported is not None:
            return reported
        cycles = self._value("system.cpu.numCycles")
        insts = self._value("system.cpu.instsIssued")
        if cycles is None or insts is None:
            return None
        return safe_divide(cycles, insts)

    def calculate_execution_time(self) -> float | None:
        """Wall-clock simulated execution time, in seconds.

        Returns:
            The value of simSeconds, or None if not present.
        """
        return self._value("simSeconds")

    def calculate_busy_cycles(self) -> float | None:
        """Estimated busy (non-idle) cycles = instsAdded * cpi.

        Returns:
            An estimate of cycles spent doing useful work, or None if
            required inputs are missing.
        """
        insts_added = self._value("system.cpu.instsAdded")
        cpi = self.calculate_cpi()
        if insts_added is None or cpi is None:
            return None
        return insts_added * cpi

    def calculate_idle_percentage(self) -> float | None:
        """Percentage of total cycles considered idle.

        Idle cycles are estimated as (numCycles - busy_cycles), expressed
        as a percentage of numCycles.

        Returns:
            A percentage in [0, 100], or None if required inputs are
            missing or numCycles is zero.
        """
        total_cycles = self._value("system.cpu.numCycles")
        busy_cycles = self.calculate_busy_cycles()
        if total_cycles is None or busy_cycles is None:
            return None
        idle_fraction = safe_divide(max(total_cycles - busy_cycles, 0.0), total_cycles)
        if idle_fraction is None:
            return None
        return idle_fraction * 100.0

    def calculate_instruction_efficiency(self) -> float | None:
        """Ratio of issued instructions that were actually added/committed.

        Returns:
            instsAdded / instsIssued as a fraction in [0, 1], or None if
            inputs are missing or instsIssued is zero.
        """
        added = self._value("system.cpu.instsAdded")
        issued = self._value("system.cpu.instsIssued")
        if added is None or issued is None:
            return None
        return safe_divide(added, issued)

    def calculate_host_speed(self) -> float | None:
        """Host simulation speed in simulated-instructions-per-second.

        Returns:
            The value of hostInstRate, or None if not present.
        """
        return self._value("hostInstRate")

    def calculate_cpu_utilization(self) -> float | None:
        """CPU utilization percentage = 100 - idle_percentage.

        Returns:
            A percentage in [0, 100], or None if idle percentage cannot
            be computed.
        """
        idle_pct = self.calculate_idle_percentage()
        if idle_pct is None:
            return None
        return max(0.0, min(100.0, 100.0 - idle_pct))

    def calculate_all(self) -> dict[str, float | None]:
        """Run all derived-metric calculations.

        Returns:
            A mapping of derived-metric name -> computed value (or None
            if the calculation could not be performed).
        """
        calculations = {
            "ipc": self.calculate_ipc,
            "cpi": self.calculate_cpi,
            "executionTimeSeconds": self.calculate_execution_time,
            "busyCycles": self.calculate_busy_cycles,
            "idlePercentage": self.calculate_idle_percentage,
            "instructionEfficiency": self.calculate_instruction_efficiency,
            "hostSpeedInstsPerSec": self.calculate_host_speed,
            "cpuUtilizationPercentage": self.calculate_cpu_utilization,
        }
        results: dict[str, float | None] = {}
        for name, func in calculations.items():
            try:
                results[name] = func()
            except (ZeroDivisionError, ValueError, TypeError) as exc:
                logger.warning("Derived metric '%s' failed: %s", name, exc)
                results[name] = None
        return results