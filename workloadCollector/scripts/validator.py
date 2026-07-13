"""
validator.py

`Validator` performs all pre-flight checks for a workload before gem5 is
ever invoked: binary existence/permissions, input file presence, output
directory writability, and available disk space. Separating this from
Gem5Runner keeps "can we run this?" logic independently testable from
"how do we run this?" logic.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from logger import get_logger
from utils import free_disk_mb
from workload import Workload

logger = get_logger("gtrace.validator")


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.ok = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


class Validator:
    """Validates a Workload against the filesystem and environment.yaml policy."""

    def __init__(self, project_root: Path, env_config: dict) -> None:
        self._project_root = project_root
        validation_cfg = env_config.get("validation", {})
        self._check_binary_exists = validation_cfg.get("check_binary_exists", True)
        self._check_binary_executable = validation_cfg.get("check_binary_executable", True)
        self._check_input_files = validation_cfg.get("check_input_files", True)
        self._check_output_dir_writable = validation_cfg.get(
            "check_output_directory_writable", True
        )
        self._check_disk_space = validation_cfg.get("check_disk_space", True)
        self._min_free_disk_mb = (
            env_config.get("_simulator", {}).get("resources", {}).get("min_free_disk_mb", 2048)
        )
        self._outputs_dir = project_root / env_config.get("paths", {}).get(
            "outputs_dir", "outputs"
        )

    def validate(self, workload: Workload) -> ValidationResult:
        result = ValidationResult(ok=True)

        binary_path = workload.binary_path(self._project_root)
        if self._check_binary_exists and not binary_path.exists():
            result.add_error(f"Binary not found: {binary_path}")
        elif self._check_binary_executable and binary_path.exists():
            if not os.access(binary_path, os.X_OK):
                result.add_error(f"Binary is not executable: {binary_path}")

        working_dir = workload.working_directory_path(self._project_root)
        if not working_dir.exists():
            result.add_warning(f"Working directory does not exist yet: {working_dir}")

        if self._check_input_files:
            for input_path in workload.input_file_paths(self._project_root):
                if not input_path.exists():
                    result.add_error(f"Input file not found: {input_path}")

        if self._check_output_dir_writable:
            target = self._outputs_dir / workload.name
            try:
                target.mkdir(parents=True, exist_ok=True)
                probe = target / ".write_test"
                probe.touch()
                probe.unlink()
            except OSError as exc:
                result.add_error(f"Output directory not writable ({target}): {exc}")

        if self._check_disk_space:
            free_mb = free_disk_mb(self._outputs_dir)
            if free_mb < self._min_free_disk_mb:
                result.add_error(
                    f"Insufficient disk space: {free_mb:.0f}MB free, "
                    f"{self._min_free_disk_mb}MB required"
                )

        if result.ok:
            logger.debug("Validation passed for workload '%s'", workload.id)
        else:
            logger.warning(
                "Validation failed for workload '%s': %s", workload.id, "; ".join(result.errors)
            )

        return result