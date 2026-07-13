"""
runner.py

Main command line interface (CLI) entry point for the gtrace-benchmark execution framework.
Parses CLI parameters, loads/filters YAML configurations, runs validation and batch scheduling,
and produces detailed reports in CSV, JSON, and Markdown.
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional

import yaml

from logger import LoggingConfigurator, get_logger
from scheduler import Scheduler, SchedulerSummary
from utils import ensure_dir, human_duration
from workload import Workload, WorkloadCatalog

logger = get_logger("gtrace.runner")


def load_yaml_config(path: Path) -> dict:
    """Safely load a YAML config file; return an empty dict on failure."""
    if not path.exists():
        return {}
    try:
        with path.open() as f:
            return yaml.safe_load(f) or {}
    except Exception as exc:
        print(f"Error reading YAML configuration {path}: {exc}", file=sys.stderr)
        return {}


class BenchmarkRunner:
    """Coordinates startup, filtering, scheduler execution, and reporting."""

    def __init__(self, project_root: Path, args: argparse.Namespace) -> None:
        self.project_root = project_root
        self.args = args

        # Load configs
        self.env_config = load_yaml_config(project_root / "config/environment.yaml")
        self.sim_config = load_yaml_config(project_root / "config/simulator.yaml")
        self.logging_config_path = project_root / "config/logging.yaml"

        # Apply verbose override to logging config dictionary before initializing
        if args.verbose:
            self.env_config["logging_level"] = "DEBUG"

        # Initialize logging hierarchy
        LoggingConfigurator.configure(self.logging_config_path, self.project_root)
        if args.verbose:
            logging.getLogger("gtrace").setLevel(logging.DEBUG)
            logger.setLevel(logging.DEBUG)

    def run(self) -> int:
        """Run the core pipeline workflow."""
        logger.info("Initializing gtrace-benchmark execution framework...")

        # 1. Load workload configurations
        workloads_yaml_path = self.project_root / "config/workloads.yaml"
        if not workloads_yaml_path.exists():
            logger.critical("Workload configuration not found at %s. Please generate it.", workloads_yaml_path)
            return 1

        try:
            catalog = WorkloadCatalog.load(workloads_yaml_path)
        except Exception as exc:
            logger.critical("Failed to load workload catalog: %s", exc, exc_info=True)
            return 1

        # 2. Filter workloads based on CLI requirements
        filtered_workloads = catalog.filter(
            suite=self.args.suite,
            name=self.args.benchmark,
            category=self.args.category,
        )

        if not filtered_workloads:
            logger.warning(
                "No active workloads found matching: suite=%s, benchmark=%s, category=%s",
                self.args.suite,
                self.args.benchmark,
                self.args.category,
            )
            return 0

        # Apply repetitions override if requested
        if self.args.repeat is not None:
            updated_workloads = []
            for wl in filtered_workloads:
                # Use dataclasses.replace to respect frozen workload dataclass
                import dataclasses
                updated_workloads.append(dataclasses.replace(wl, repetitions=self.args.repeat))
            filtered_workloads = updated_workloads

        logger.info("Selected %d workload(s) for execution", len(filtered_workloads))

        # 3. Instantiate Scheduler and start execution
        parallel_mode = "sequential"
        worker_count = 1
        if self.args.parallel and self.args.parallel > 1:
            parallel_mode = self.args.parallel_mode or "threads"
            worker_count = self.args.parallel

        scheduler = Scheduler(
            project_root=self.project_root,
            env_config=self.env_config,
            sim_config=self.sim_config,
            parallel_mode=parallel_mode,
            worker_count=worker_count,
            resume=self.args.resume,
            dry_run=self.args.dry_run,
        )

        summary = scheduler.run_all(filtered_workloads)

        # 4. Generate report summaries
        self.generate_reports(summary)

        # 5. Print final console summary
        self.print_console_summary(summary)

        return 0 if summary.failure_count == 0 else 2

    def generate_reports(self, summary: SchedulerSummary) -> None:
        """Create CSV, JSON, and Markdown summaries under the reports directory."""
        reports_dir = self.project_root / self.env_config.get("paths", {}).get("reports_dir", "reports")
        ensure_dir(reports_dir)

        # A. Write CSV Report
        csv_path = reports_dir / "summary.csv"
        try:
            with csv_path.open("w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "workload_id", "run_directory", "attempt", "status", "return_code",
                    "runtime_seconds", "failure_reason", "error_message"
                ])
                for res in summary.results:
                    writer.writerow([
                        res.workload_id,
                        str(res.run_dir.relative_to(self.project_root)),
                        res.attempt_number,
                        "success" if res.success else "failed",
                        res.return_code,
                        f"{res.execution_time_seconds:.3f}",
                        res.failure_reason or "",
                        res.error_message or ""
                    ])
            logger.info("Wrote CSV report to %s", csv_path)
        except OSError as exc:
            logger.error("Failed to write CSV summary: %s", exc)

        # B. Write JSON Report
        json_path = reports_dir / "summary.json"
        try:
            report_data = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "total_workloads": summary.total_workloads,
                "executed": summary.executed_count,
                "success": summary.success_count,
                "failed": summary.failure_count,
                "skipped": summary.skipped_count,
                "retry_count": summary.retry_count,
                "total_time_seconds": summary.total_time_seconds,
                "average_runtime_seconds": summary.average_runtime_seconds,
                "results": [
                    {
                        "workload_id": res.workload_id,
                        "run_dir": str(res.run_dir.relative_to(self.project_root)),
                        "attempt": res.attempt_number,
                        "success": res.success,
                        "return_code": res.return_code,
                        "runtime": res.execution_time_seconds,
                        "failure_reason": res.failure_reason,
                    }
                    for res in summary.results
                ]
            }
            with json_path.open("w") as f:
                json.dump(report_data, f, indent=2)
            logger.info("Wrote JSON report to %s", json_path)
        except OSError as exc:
            logger.error("Failed to write JSON summary: %s", exc)

        # C. Write Markdown Summary
        md_path = reports_dir / "summary.md"
        try:
            with md_path.open("w") as f:
                f.write("# gem5 Batch Simulation Run Report\n\n")
                f.write(f"- **Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"- **Total Target Runs**: {summary.total_workloads}\n")
                f.write(f"- **Executed**: {summary.executed_count}\n")
                f.write(f"- **Success Count**: {summary.success_count}\n")
                f.write(f"- **Failure Count**: {summary.failure_count}\n")
                f.write(f"- **Skipped (Resume)**: {summary.skipped_count}\n")
                f.write(f"- **Total Retries Made**: {summary.retry_count}\n")
                f.write(f"- **Total Elapsed Time**: {human_duration(summary.total_time_seconds)}\n")
                f.write(f"- **Average Benchmark Execution Time**: {summary.average_runtime_seconds:.2f}s\n\n")

                f.write("## Individual Run Summary\n\n")
                f.write("| Workload ID | Attempt | Status | Runtime (s) | Failure Reason | Run Directory |\n")
                f.write("|---|---|---|---|---|---|\n")
                for res in summary.results:
                    status_emoji = "✅ Success" if res.success else "❌ Failed"
                    f.write(
                        f"| {res.workload_id} | {res.attempt_number} | {status_emoji} | "
                        f"{res.execution_time_seconds:.1f}s | {res.failure_reason or 'None'} | "
                        f"`{res.run_dir.relative_to(self.project_root)}` |\n"
                    )
            logger.info("Wrote Markdown report to %s", md_path)
        except OSError as exc:
            logger.error("Failed to write Markdown summary: %s", exc)

    def print_console_summary(self, summary: SchedulerSummary) -> None:
        """Output clear final counts to stdout."""
        summary_msg = (
            f"\n"
            f"==================================================\n"
            f"               Execution Summary                  \n"
            f"==================================================\n"
            f"Total Target Runs : {summary.total_workloads}\n"
            f"Executed Runs      : {summary.executed_count}\n"
            f"Success Runs       : {summary.success_count}\n"
            f"Failed Runs        : {summary.failure_count}\n"
            f"Skipped Runs       : {summary.skipped_count}\n"
            f"Total Retries      : {summary.retry_count}\n"
            f"Total Elapsed Time : {human_duration(summary.total_time_seconds)}\n"
            f"Avg Runtime        : {summary.average_runtime_seconds:.2f}s\n"
            f"==================================================\n"
        )
        print(summary_msg, flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="gtrace-benchmark: gem5 RISC-V trace generation automation engine."
    )
    
    # Filtering options
    parser.add_argument("--suite", type=str, help="Filter workloads by suite (e.g. polybench, embench)")
    parser.add_argument("--benchmark", type=str, help="Filter workloads by benchmark name (e.g. gemm)")
    parser.add_argument("--category", type=str, help="Filter workloads by category (e.g. graph)")
    
    # Override options
    parser.add_argument("--repeat", type=int, help="Override number of execution repetitions for workloads")
    
    # Parallel execution options
    parser.add_argument("--parallel", type=int, help="Number of parallel worker execution threads/processes")
    parser.add_argument(
        "--parallel-mode",
        choices=["threads", "processes"],
        default="threads",
        help="Use ThreadPoolExecutor ('threads') or ProcessPoolExecutor ('processes') for execution"
    )
    
    # Flow controls
    parser.add_argument("--resume", action="store_true", help="Skip runs that have successfully completed previously")
    parser.add_argument("--dry-run", action="store_true", help="Perform validation and output tracking without launching gem5")
    parser.add_argument("--verbose", action="store_true", help="Log debug messages to the console")

    args = parser.parse_args()

    # Scripts folder is in workloadCollector/scripts. Project root is parent of scripts.
    scripts_dir = Path(__file__).resolve().parent
    project_root = scripts_dir.parent

    runner = BenchmarkRunner(project_root, args)
    sys.exit(runner.run())


if __name__ == "__main__":
    main()

