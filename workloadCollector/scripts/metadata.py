"""
metadata.py

`MetadataWriter` aggregates simulation outputs (duration, stats) with host system details
(CPU, OS, git commit, installed libraries) to build the structured `metadata.json`
required for replication of simulation experiments.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from logger import get_logger
from workload import Workload
from gem5_runner import ExecutionResult
from parser import StatisticsCollector
from utils import (
    get_hostname,
    get_python_version,
    get_os_info,
    get_cpu_info,
    get_memory_info,
    get_git_commit,
    get_installed_packages,
    filtered_env_vars,
    sha256_of_file,
    sha256_of_files,
    get_gem5_version,
)

logger = get_logger("gtrace.metadata")


class MetadataWriter:
    """Gathers and saves experiment reproducibility metadata to run directories."""

    def __init__(self, project_root: Path, env_config: dict) -> None:
        self.project_root = project_root
        self.env_config = env_config
        self.allowlist_prefixes = env_config.get(
            "env_vars_allowlist", ["PATH", "GEM5", "LD_LIBRARY_PATH"]
        )

    def generate(
        self, workload: Workload, result: ExecutionResult, gem5_executable: str
    ) -> dict[str, Any]:
        """Aggregate all metrics, hashes, and system info into a dictionary."""
        stats_path = result.stats_path
        trace_path = result.trace_path

        # 1. Parse gem5 simulation statistics from stats.txt
        stats_summary = StatisticsCollector.summarize(stats_path)

        # 2. Measure sizes of the generated artifacts
        trace_size = trace_path.stat().st_size if trace_path.exists() else 0
        stats_size = stats_path.stat().st_size if stats_path.exists() else 0

        # 3. Hash binary and input files for data-integrity tracking
        binary_hash = sha256_of_file(workload.binary_path(self.project_root)) or "unknown"
        input_hash = sha256_of_files(workload.input_file_paths(self.project_root)) or "none"

        # 4. Gather system execution properties
        git_commit = get_git_commit(self.project_root)
        gem5_ver = get_gem5_version(gem5_executable)

        metadata = {
            "benchmark_name": workload.name,
            "suite": workload.suite,
            "category": workload.category,
            "execution_time_seconds": result.execution_time_seconds,
            "simulation_ticks": stats_summary.get("sim_ticks"),
            "simulation_seconds": stats_summary.get("sim_seconds"),
            "committed_instructions": stats_summary.get("sim_insts"),
            "host_name": get_hostname(),
            "cpu_model": workload.cpu_type,
            "isa": workload.isa,
            "memory": workload.memory,
            "cache": {
                "l1d_size": workload.cache.l1d_size,
                "l1i_size": workload.cache.l1i_size,
                "l2_size": workload.cache.l2_size,
            },
            "gem5_version": gem5_ver,
            "git_commit": git_commit,
            "date": result.finished_at,
            "binary_hash": binary_hash,
            "input_hash": input_hash,
            "return_code": result.return_code,
            "trace_size_bytes": trace_size,
            "stats_size_bytes": stats_size,
            "execution_status": "success" if result.success else (result.failure_reason or "failed"),
            "attempt": result.attempt_number,
            "error_message": result.error_message,
            "reproducibility": {
                "python_version": get_python_version(),
                "operating_system": get_os_info(),
                "host_cpu": get_cpu_info(),
                "host_memory": get_memory_info(),
                "environment_variables": filtered_env_vars(self.allowlist_prefixes),
                "installed_packages": get_installed_packages(),
            },
        }
        return metadata

    def write(self, workload: Workload, result: ExecutionResult, gem5_executable: str) -> Path:
        """Write the aggregated metadata dictionary to metadata.json."""
        metadata = self.generate(workload, result, gem5_executable)
        out_path = result.run_dir / "metadata.json"
        
        try:
            with out_path.open("w") as f:
                json.dump(metadata, f, indent=2)
            logger.debug("Wrote metadata.json to %s", out_path)
            
            # Optional Schema Validation
            self._validate_schema(metadata)
            
        except OSError as exc:
            logger.error("Failed to write metadata.json to %s: %s", out_path, exc)
            
        return out_path

    def _validate_schema(self, metadata: dict[str, Any]) -> None:
        """Validate metadata against schema if jsonschema is installed."""
        try:
            import jsonschema
            schema_path = self.project_root / "config/metadata_schema.json"
            if schema_path.exists():
                with schema_path.open() as sf:
                    schema = json.load(sf)
                jsonschema.validate(instance=metadata, schema=schema)
                logger.debug("Successfully validated metadata against schema.")
        except ImportError:
            pass  # jsonschema not installed, skip validation
        except Exception as exc:
            logger.warning("Metadata schema validation warning: %s", exc)

