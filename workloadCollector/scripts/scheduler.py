"""
scheduler.py

Manages batch execution of workloads across single/multiple threads/processes.
Uses a main-thread tracker to update console progress safely without passing
locks to child processes.
"""
from __future__ import annotations

import concurrent.futures
import json
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

from gem5_runner import ExecutionResult, Gem5Runner
from logger import attach_per_run_file_handler, get_logger
from metadata import MetadataWriter
from retry import RetryManager, RetryPolicy
from utils import ensure_dir, human_duration
from validator import Validator
from workload import Workload

logger = get_logger("gtrace.scheduler")


@dataclass
class SchedulerSummary:
    total_workloads: int
    executed_count: int
    success_count: int
    failure_count: int
    skipped_count: int
    retry_count: int
    total_time_seconds: float
    average_runtime_seconds: float
    results: list[ExecutionResult] = field(default_factory=list)


class ProgressTracker:
    """Thread-safe tracker to print running stats to stdout."""

    def __init__(self, total_runs: int) -> None:
        self.total = total_runs
        self.completed = 0
        self.success_count = 0
        self.failure_count = 0
        self.skipped_count = 0
        self.retry_count = 0
        self.start_time = 0.0
        self._lock = threading.Lock()
        self._active_benchmarks: dict[str, str] = {}
        self._bench_counter = 0

    def start(self) -> None:
        self.start_time = time.monotonic()

    def register_start(self, run_key: str, name: str) -> None:
        with self._lock:
            self._active_benchmarks[run_key] = name
            self._display()

    def register_completion(self, run_key: str, success: bool, retries: int) -> None:
        with self._lock:
            self._active_benchmarks.pop(run_key, None)
            self.completed += 1
            if success:
                self.success_count += 1
            else:
                self.failure_count += 1
            self.retry_count += retries
            self._display()

    def register_skipped(self) -> None:
        with self._lock:
            self.completed += 1
            self.skipped_count += 1
            self._display()

    def _display(self) -> None:
        elapsed = time.monotonic() - self.start_time
        avg_time = elapsed / self.completed if self.completed > 0 else 0.0
        remaining = self.total - self.completed
        eta = avg_time * remaining if self.completed > 0 else 0.0

        current_active = ", ".join(self._active_benchmarks.values()) or "None"

        status_line = (
            f"\n=== Progress: Running benchmark {min(self.completed + len(self._active_benchmarks), self.total)}/{self.total} ===\n"
            f"Current benchmark(s): {current_active}\n"
            f"Elapsed time: {human_duration(elapsed)} | ETA: {human_duration(eta)}\n"
            f"Success: {self.success_count} | Failed: {self.failure_count} | Skipped: {self.skipped_count} | Retries: {self.retry_count}\n"
            f"========================================\n"
        )
        print(status_line, flush=True)


def _execute_run_worker(
    workload: Workload,
    run_dir: Path,
    sim_config: dict,
    env_config: dict,
    project_root: Path,
    dry_run: bool,
) -> ExecutionResult:
    """Independent worker execution logic. Runs validation, gem5, and metadata generation."""
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Validation
    if not dry_run:
        validator = Validator(project_root, env_config)
        val_res = validator.validate(workload)
        if not val_res.ok:
            return ExecutionResult(
                workload_id=workload.id,
                run_dir=run_dir,
                attempt_number=1,
                return_code=None,
                success=False,
                failure_reason="validation_failed",
                execution_time_seconds=0.0,
                stdout_path=run_dir / "stdout.txt",
                stderr_path=run_dir / "stderr.txt",
                trace_path=run_dir / "trace.log",
                stats_path=run_dir / "stats.txt",
                started_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
                finished_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
                error_message="; ".join(val_res.errors),
            )

    # 2. Attach per-run logging
    run_log = run_dir / "execution.log"
    log_handler = None
    if not dry_run:
        # Get standard logger and attach file handler for this runner thread/process
        run_logger = get_logger("gtrace.scheduler")
        log_handler = attach_per_run_file_handler(run_logger, run_log)

    try:
        # Build components
        runner = Gem5Runner(project_root, sim_config)
        retry_cfg = sim_config.get("retry", {})
        retry_policy = RetryPolicy.from_dict(retry_cfg)
        retry_manager = RetryManager(retry_policy)

        # Attempt runner wrapper
        def attempt_fn(attempt: int) -> ExecutionResult:
            if dry_run:
                # Mock execution
                time.sleep(0.1)
                return ExecutionResult(
                    workload_id=workload.id,
                    run_dir=run_dir,
                    attempt_number=attempt,
                    return_code=0,
                    success=True,
                    failure_reason=None,
                    execution_time_seconds=0.1,
                    stdout_path=run_dir / "stdout.txt",
                    stderr_path=run_dir / "stderr.txt",
                    trace_path=run_dir / "trace.log",
                    stats_path=run_dir / "stats.txt",
                    started_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
                    finished_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
                )
            return runner.run(workload, run_dir, attempt)

        is_success = lambda res: res.success
        failure_reason = lambda res: res.failure_reason or "unknown"

        result, attempts_made = retry_manager.run(attempt_fn, is_success, failure_reason)

        # Write metadata
        if not dry_run:
            metadata_writer = MetadataWriter(project_root, env_config)
            metadata_writer.write(workload, result, sim_config["gem5"]["executable"])

        return result

    finally:
        if log_handler:
            get_logger("gtrace.scheduler").removeHandler(log_handler)
            log_handler.close()


class Scheduler:
    """Orchestrates runs across workers, verifying and tracking progress."""

    def __init__(
        self,
        project_root: Path,
        env_config: dict,
        sim_config: dict,
        parallel_mode: str = "sequential",
        worker_count: int = 1,
        resume: bool = False,
        dry_run: bool = False,
    ) -> None:
        self.project_root = project_root
        self.env_config = env_config
        self.sim_config = sim_config
        self.parallel_mode = parallel_mode.lower()
        self.worker_count = worker_count
        self.resume = resume
        self.dry_run = dry_run

        self.outputs_dir = project_root / env_config.get("paths", {}).get("outputs_dir", "outputs")
        ensure_dir(self.outputs_dir)

    def _get_run_directory(self, workload: Workload, run_idx: int) -> Path:
        return self.outputs_dir / workload.name / f"run_{run_idx:03d}"

    def _is_run_completed(self, run_dir: Path) -> bool:
        if not self.resume:
            return False
        metadata_file = run_dir / "metadata.json"
        if not metadata_file.exists():
            return False
        try:
            with metadata_file.open() as f:
                data = json.load(f)
                return data.get("execution_status") == "success"
        except Exception:
            return False

    def run_all(self, workloads: list[Workload]) -> SchedulerSummary:
        start_time = time.monotonic()

        # Flatten workloads into distinct run parameters
        all_runs: list[tuple[Workload, Path, int]] = []
        for wl in workloads:
            for rep in range(1, wl.repetitions + 1):
                run_dir = self._get_run_directory(wl, rep)
                all_runs.append((wl, run_dir, rep))

        total_runs = len(all_runs)
        tracker = ProgressTracker(total_runs)
        tracker.start()

        results: list[ExecutionResult] = []
        runs_to_submit: list[tuple[Workload, Path, str]] = []

        # Filter out skipped runs first
        for wl, run_dir, rep in all_runs:
            if self._is_run_completed(run_dir):
                logger.info("Resuming: Skip completed run %s", run_dir)
                tracker.register_skipped()
            else:
                run_key = f"{wl.id}_rep{rep}"
                runs_to_submit.append((wl, run_dir, run_key))

        to_execute = len(runs_to_submit)
        logger.info(
            "Starting execution of %d runs using mode '%s' (workers=%d)",
            to_execute,
            self.parallel_mode,
            self.worker_count,
        )

        if self.parallel_mode == "sequential" or self.worker_count <= 1:
            for wl, run_dir, run_key in runs_to_submit:
                tracker.register_start(run_key, wl.name)
                try:
                    res = _execute_run_worker(
                        wl,
                        run_dir,
                        self.sim_config,
                        self.env_config,
                        self.project_root,
                        self.dry_run,
                    )
                    results.append(res)
                    tracker.register_completion(
                        run_key, success=res.success, retries=res.attempt_number - 1
                    )
                except Exception as exc:
                    logger.error("Error executing %s: %s", wl.id, exc, exc_info=True)
                    tracker.register_completion(run_key, success=False, retries=0)
        else:
            # Parallel Executors
            if self.parallel_mode == "processes":
                executor_cls = concurrent.futures.ProcessPoolExecutor
            else:
                executor_cls = concurrent.futures.ThreadPoolExecutor

            with executor_cls(max_workers=self.worker_count) as executor:
                futures = {}
                for wl, run_dir, run_key in runs_to_submit:
                    tracker.register_start(run_key, wl.name)
                    fut = executor.submit(
                        _execute_run_worker,
                        wl,
                        run_dir,
                        self.sim_config,
                        self.env_config,
                        self.project_root,
                        self.dry_run,
                    )
                    futures[fut] = (wl, run_dir, run_key)

                for fut in concurrent.futures.as_completed(futures):
                    wl, run_dir, run_key = futures[fut]
                    try:
                        res = fut.result()
                        results.append(res)
                        tracker.register_completion(
                            run_key, success=res.success, retries=res.attempt_number - 1
                        )
                    except Exception as exc:
                        logger.error(
                            "Unhandled pool exception running %s: %s", wl.id, exc, exc_info=True
                        )
                        tracker.register_completion(run_key, success=False, retries=0)
                        # Create generic failed result
                        results.append(
                            ExecutionResult(
                                workload_id=wl.id,
                                run_dir=run_dir,
                                attempt_number=1,
                                return_code=None,
                                success=False,
                                failure_reason="crashed",
                                execution_time_seconds=0.0,
                                stdout_path=run_dir / "stdout.txt",
                                stderr_path=run_dir / "stderr.txt",
                                trace_path=run_dir / "trace.log",
                                stats_path=run_dir / "stats.txt",
                                started_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
                                finished_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
                                error_message=f"Pool scheduler exception: {exc}",
                            )
                        )

        total_time = time.monotonic() - start_time
        successes = [r for r in results if r.success]
        failures = [r for r in results if not r.success]
        executed_count = len(results)

        avg_runtime = (
            sum(r.execution_time_seconds for r in results) / executed_count
            if executed_count > 0
            else 0.0
        )
        total_retries = sum(r.attempt_number - 1 for r in results)

        summary = SchedulerSummary(
            total_workloads=total_runs,
            executed_count=executed_count,
            success_count=len(successes),
            failure_count=len(failures),
            skipped_count=total_runs - executed_count,
            retry_count=total_retries,
            total_time_seconds=total_time,
            average_runtime_seconds=avg_runtime,
            results=results,
        )

        logger.info(
            "Scheduler batch processing finished. Success: %d/%d, Failed: %d, Skipped: %d, Time: %s",
            summary.success_count,
            summary.total_workloads,
            summary.failure_count,
            summary.skipped_count,
            human_duration(total_time),
        )

        return summary
