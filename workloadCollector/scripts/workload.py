"""
workload.py

Defines the `Workload` dataclass (a typed, immutable-by-convention
representation of a single entry in config/workloads.yaml) plus the
`WorkloadCatalog` loader that parses/filters the full YAML file.

Design decision: workloads are plain dataclasses rather than dicts so that
the rest of the codebase gets static-analysis-friendly attribute access
(`workload.timeout` instead of `workload["timeout"]`) and so defaulting /
validation logic lives in exactly one place.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass(frozen=True)
class CacheConfig:
    """Cache hierarchy sizing for a single workload."""

    l1d_size: str = "32kB"
    l1i_size: str = "32kB"
    l2_size: str = "1MB"

    @staticmethod
    def from_dict(data: Optional[dict[str, Any]]) -> "CacheConfig":
        data = data or {}
        return CacheConfig(
            l1d_size=data.get("l1d_size", "32kB"),
            l1i_size=data.get("l1i_size", "32kB"),
            l2_size=data.get("l2_size", "1MB"),
        )


@dataclass(frozen=True)
class Workload:
    """
    A single benchmark workload as declared in config/workloads.yaml.

    Frozen (immutable) because a Workload should never be mutated after
    load - any per-run derived data (paths, results) belongs in
    ExecutionResult instead, keeping the two concerns separate.
    """

    id: str
    name: str
    suite: str
    category: str
    binary: str
    working_directory: str
    arguments: tuple[str, ...] = field(default_factory=tuple)
    input_files: tuple[str, ...] = field(default_factory=tuple)
    output_files: tuple[str, ...] = field(default_factory=tuple)
    timeout: int = 1800
    cpu_type: str = "DerivO3CPU"
    cpu_clock: str = "2GHz"
    memory: str = "2GB"
    cache: CacheConfig = field(default_factory=CacheConfig)
    isa: str = "riscv"
    priority: str = "normal"
    repetitions: int = 1
    enabled: bool = True

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Workload":
        required = ["id", "name", "suite", "category", "binary", "working_directory"]
        missing = [k for k in required if k not in data or data[k] in (None, "")]
        if missing:
            raise ValueError(
                f"Workload entry missing required field(s) {missing}: {data!r}"
            )
        return Workload(
            id=str(data["id"]),
            name=str(data["name"]),
            suite=str(data["suite"]),
            category=str(data["category"]),
            binary=str(data["binary"]),
            working_directory=str(data["working_directory"]),
            arguments=tuple(data.get("arguments") or []),
            input_files=tuple(data.get("input_files") or []),
            output_files=tuple(data.get("output_files") or []),
            timeout=int(data.get("timeout", 1800)),
            cpu_type=str(data.get("cpu_type", "DerivO3CPU")),
            cpu_clock=str(data.get("cpu_clock", "2GHz")),
            memory=str(data.get("memory", "2GB")),
            cache=CacheConfig.from_dict(data.get("cache")),
            isa=str(data.get("isa", "riscv")),
            priority=str(data.get("priority", "normal")),
            repetitions=int(data.get("repetitions", 1)),
            enabled=bool(data.get("enabled", True)),
        )

    def binary_path(self, project_root: Path) -> Path:
        return (project_root / self.binary).resolve()

    def working_directory_path(self, project_root: Path) -> Path:
        return (project_root / self.working_directory).resolve()

    def input_file_paths(self, project_root: Path) -> list[Path]:
        return [self.working_directory_path(project_root) / f for f in self.input_files]


class WorkloadCatalog:
    """Loads and filters the full set of workloads declared in workloads.yaml."""

    def __init__(self, workloads: list[Workload]) -> None:
        self._workloads = workloads

    @classmethod
    def load(cls, path: Path) -> "WorkloadCatalog":
        with path.open() as f:
            doc = yaml.safe_load(f) or {}
        raw_workloads = doc.get("workloads", [])
        workloads = [Workload.from_dict(w) for w in raw_workloads]
        return cls(workloads)

    def all(self) -> list[Workload]:
        return list(self._workloads)

    def enabled(self) -> list[Workload]:
        return [w for w in self._workloads if w.enabled]

    def by_suite(self, suite: str) -> list[Workload]:
        return [w for w in self._workloads if w.suite == suite and w.enabled]

    def by_name(self, name: str) -> list[Workload]:
        return [w for w in self._workloads if w.name == name and w.enabled]

    def by_id(self, workload_id: str) -> Optional[Workload]:
        for w in self._workloads:
            if w.id == workload_id:
                return w
        return None

    def filter(
        self,
        suite: Optional[str] = None,
        name: Optional[str] = None,
        category: Optional[str] = None,
    ) -> list[Workload]:
        result = self.enabled()
        if suite:
            result = [w for w in result if w.suite == suite]
        if name:
            result = [w for w in result if w.name == name]
        if category:
            result = [w for w in result if w.category == category]
        return result

    def __len__(self) -> int:
        return len(self._workloads)