"""
gem5_runner.py

`Gem5Runner` is responsible for exactly one thing: constructing and
executing a single gem5 subprocess invocation for a single (Workload,
attempt, run_dir) triple, and reporting back a structured `ExecutionResult`.

It deliberately knows nothing about retries (see retry.py), scheduling
across many workloads (see scheduler.py), or metadata persistence (see
metadata.py) - each of those is a separate class per the single
responsibility principle requested in the design.
"""
from __future__ import annotations

import shlex
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from logger import get_logger
from workload import Workload

logger = get_logger("gtrace.gem5")


@dataclass
class ExecutionResult:
    """
    Structured outcome of one gem5 invocation attempt. This is the object
    passed to RetryManager (via duck-typed `.success`/`.failure_reason`),
    MetadataWriter, and the final report generators - it is the single
    source of truth about "what happened" for a run.
    """

    workload_id: str
    run_dir: Path
    attempt_number: int
    return_code: Optional[int]
    success: bool
    failure_reason: Optional[str]      # one of: timeout, nonzero_exit, missing_output,
                                        # crashed, interrupted, oom, None (success)
    execution_time_seconds: float
    stdout_path: Path
    stderr_path: Path
    trace_path: Path
    stats_path: Path
    started_at: str
    finished_at: str
    error_message: Optional[str] = None
    expected_outputs_present: dict[str, bool] = field(default_factory=dict)


class Gem5Runner:
    """
    Builds a gem5 command line from simulator.yaml + a Workload, executes it
    as a subprocess with a hard timeout, and validates that the expected
    output artifacts were produced.
    """

    def __init__(self, project_root: Path, simulator_config: dict) -> None:
        self._project_root = project_root
        self._sim_cfg = simulator_config
        self._gem5_executable = simulator_config["gem5"]["executable"]
        
        config_script = simulator_config["gem5"]["config_script"]
        config_script_path = Path(config_script)
        if not config_script_path.is_absolute():
            config_script_path = (project_root / config_script_path).resolve()
        self._config_script = str(config_script_path)

    def build_command(self, workload: Workload, run_dir: Path) -> list[str]:
        """
        Construct the full gem5 command line for a single run.

        gem5's own CLI convention is:
            gem5.opt [gem5 options] <config_script> [script options]
        so global/debug/output options must precede the config script, and
        per-benchmark options (binary + args) come after it.
        """
        gem5_cfg = self._sim_cfg["gem5"]
        trace_cfg = self._sim_cfg.get("trace", {})
        limits_cfg = self._sim_cfg.get("limits", {})

        cmd: list[str] = [self._gem5_executable]

        cmd += ["--outdir", str(run_dir)]

        if trace_cfg.get("enabled", True):
            cmd += ["--debug-flags", trace_cfg.get("debug_flags", "Exec,ExecAll")]
            cmd += ["--debug-file", trace_cfg.get("debug_file", "trace.log")]
            if trace_cfg.get("use_debug_start", False):
                cmd += ["--debug-start", str(trace_cfg.get("debug_start_tick", 0))]

        for flag in self._sim_cfg.get("debug", {}).get("extra_flags", []):
            cmd.append(flag)

        cmd.append(self._config_script)

        cmd += ["--cmd", str(workload.binary_path(self._project_root))]
        if workload.arguments:
            cmd += ["--options", shlex.join(workload.arguments)]

        cmd += ["--cpu-type", workload.cpu_type]
        cmd += ["--cpu-clock", workload.cpu_clock]
        cmd += ["--mem-size", workload.memory]
        cmd += ["--caches"]
        cmd += ["--l1d_size", workload.cache.l1d_size]
        cmd += ["--l1i_size", workload.cache.l1i_size]
        cmd += ["--l2cache", "--l2_size", workload.cache.l2_size]

        max_insts = limits_cfg.get("max_instructions", 0)
        if max_insts:
            cmd += ["--maxinsts", str(max_insts)]
        max_ticks = limits_cfg.get("max_ticks", 0)
        if max_ticks:
            cmd += ["--abs-max-tick", str(max_ticks)]

        return cmd

    def run(self, workload: Workload, run_dir: Path, attempt_number: int) -> ExecutionResult:
        """Execute one gem5 attempt for `workload`, writing artifacts into run_dir."""
        run_dir.mkdir(parents=True, exist_ok=True)
        stdout_path = run_dir / "stdout.txt"
        stderr_path = run_dir / "stderr.txt"
        trace_path = run_dir / self._sim_cfg.get("trace", {}).get("debug_file", "trace.log")
        stats_path = run_dir / "stats.txt"

        cmd = self.build_command(workload, run_dir)
        cwd = workload.working_directory_path(self._project_root)
        timeout = workload.timeout or self._sim_cfg.get("limits", {}).get(
            "default_timeout_seconds", 1800
        )

        started = time.strftime("%Y-%m-%dT%H:%M:%S")
        start_ts = time.monotonic()
        logger.info(
            "Launching gem5 for '%s' (attempt %d, timeout=%ds)",
            workload.id, attempt_number, timeout,
        )
        logger.debug("Command: %s", shlex.join(cmd))

        return_code: Optional[int] = None
        failure_reason: Optional[str] = None
        error_message: Optional[str] = None

        try:
            with stdout_path.open("w") as out, stderr_path.open("w") as err:
                proc = subprocess.run(
                    cmd,
                    cwd=cwd if cwd.exists() else self._project_root,
                    stdout=out,
                    stderr=err,
                    timeout=timeout,
                    check=False,
                )
            return_code = proc.returncode
            if return_code == -11 or return_code == 139:
                failure_reason = "crashed"
                error_message = "Segmentation fault (signal 11)"
            elif return_code == -9 or return_code == 137:
                failure_reason = "oom"
                error_message = "Process killed (possible OOM, signal 9)"
            elif return_code != 0:
                failure_reason = "nonzero_exit"
                error_message = f"gem5 exited with return code {return_code}"
        except subprocess.TimeoutExpired:
            failure_reason = "timeout"
            error_message = f"Execution exceeded timeout of {timeout}s"
            logger.error("Timeout after %ds for workload '%s'", timeout, workload.id)
        except KeyboardInterrupt:
            failure_reason = "interrupted"
            error_message = "Execution interrupted by user (KeyboardInterrupt)"
            logger.warning("Run interrupted by user for workload '%s'", workload.id)
            raise
        except OSError as exc:
            failure_reason = "crashed"
            error_message = f"OS error launching gem5: {exc}"
            logger.error("OS error launching gem5 for '%s': %s", workload.id, exc)

        elapsed = time.monotonic() - start_ts
        finished = time.strftime("%Y-%m-%dT%H:%M:%S")

        expected_present = {
            "trace.log": trace_path.exists(),
            "stats.txt": stats_path.exists(),
        }
        if failure_reason is None and not all(expected_present.values()):
            failure_reason = "missing_output"
            missing = [k for k, v in expected_present.items() if not v]
            error_message = f"Missing expected output file(s): {missing}"

        success = failure_reason is None and return_code == 0

        result = ExecutionResult(
            workload_id=workload.id,
            run_dir=run_dir,
            attempt_number=attempt_number,
            return_code=return_code,
            success=success,
            failure_reason=failure_reason,
            execution_time_seconds=elapsed,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            trace_path=trace_path,
            stats_path=stats_path,
            started_at=started,
            finished_at=finished,
            error_message=error_message,
            expected_outputs_present=expected_present,
        )

        level = logger.info if success else logger.warning
        level(
            "gem5 finished for '%s' in %.1fs (success=%s, reason=%s)",
            workload.id, elapsed, success, failure_reason,
        )
        return result