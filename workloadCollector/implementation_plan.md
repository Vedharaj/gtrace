# Implementation Plan - gem5 Trace.log RISC-V Benchmark Automation Framework

This plan details the architecture and implementation steps to develop a production-quality benchmark execution and collection framework for gem5. It is designed to manage and run ~100 RISC-V benchmark workloads, capture debug traces, extract execution metrics, handle process failures/retries, and persist system metadata for research reproducibility.

## System Architecture (Mermaid)

The following Mermaid diagram shows the layout of our framework's software components and their relations:

```mermaid
graph TD
    runner["CLI Runner (runner.py)"] --> scheduler["Scheduler (scheduler.py)"]
    runner --> catalog["Workload Catalog (workload.py)"]
    scheduler --> val["Validator (validator.py)"]
    scheduler --> gem5["Gem5 Runner (gem5_runner.py)"]
    scheduler --> retry["Retry Manager (retry.py)"]
    scheduler --> meta["Metadata Writer (metadata.py)"]
    scheduler --> rep["Report Generator (runner.py)"]
    
    gem5 --> parser["Stats Parser (parser.py)"]
    meta --> parser
    meta --> utils["System Utils (utils.py)"]
```

## Class Diagram (Mermaid)

```mermaid
classDiagram
    class Workload {
        +id: str
        +name: str
        +suite: str
        +category: str
        +binary: str
        +working_directory: str
        +arguments: tuple[str]
        +input_files: tuple[str]
        +output_files: tuple[str]
        +timeout: int
        +cpu_type: str
        +cpu_clock: str
        +memory: str
        +cache: CacheConfig
        +isa: str
        +priority: str
        +repetitions: int
        +enabled: bool
        +binary_path(project_root: Path) Path
        +working_directory_path(project_root: Path) Path
    }

    class CacheConfig {
        +l1d_size: str
        +l1i_size: str
        +l2_size: str
    }

    class ExecutionResult {
        +workload_id: str
        +run_dir: Path
        +attempt_number: int
        +return_code: Optional[int]
        +success: bool
        +failure_reason: Optional[str]
        +execution_time_seconds: float
        +stdout_path: Path
        +stderr_path: Path
        +trace_path: Path
        +stats_path: Path
        +started_at: str
        +finished_at: str
        +error_message: Optional[str]
    }

    class Gem5Runner {
        -project_root: Path
        -sim_cfg: dict
        +build_command(workload: Workload, run_dir: Path) list[str]
        +run(workload: Workload, run_dir: Path, attempt_number: int) ExecutionResult
    }

    class Validator {
        -project_root: Path
        -env_config: dict
        +validate(workload: Workload) ValidationResult
    }

    class RetryManager {
        -policy: RetryPolicy
        +run(attempt_fn, is_success, failure_reason) tuple[T, int]
    }

    class MetadataWriter {
        -project_root: Path
        -env_config: dict
        +generate(workload: Workload, result: ExecutionResult, gem5_executable: str) dict
        +write(workload: Workload, result: ExecutionResult, gem5_executable: str) Path
    }

    class StatisticsCollector {
        +parse_stats_file(stats_path: Path) dict[str, float]
        +summarize(stats_path: Path) dict
    }

    class Scheduler {
        -project_root: Path
        -env_config: dict
        -sim_config: dict
        -parallel_mode: str
        -worker_count: int
        -resume: bool
        -dry_run: bool
        +run_all(workloads: list[Workload]) SchedulerSummary
    }

    Workload *-- CacheConfig
    Gem5Runner ..> ExecutionResult
    Scheduler --> Gem5Runner
    Scheduler --> Validator
    Scheduler --> RetryManager
    Scheduler --> MetadataWriter
    MetadataWriter ..> StatisticsCollector
```

## Batch Execution Sequence (Mermaid)

```mermaid
sequenceDiagram
    autonumber
    actor CLI as runner.py
    participant S as Scheduler
    participant V as Validator
    participant RM as RetryManager
    participant G as Gem5Runner
    participant M as MetadataWriter
    participant P as StatsParser

    CLI->>S: run_all(workloads)
    loop For each Workload
        alt Resume is True and Run has Completed
            S->>S: Skip run
        else Run needed
            S->>V: validate(workload)
            alt Validation Failed
                V-->>S: ValidationResult(ok=False)
                S->>S: Skip & mark failed
            else Validation Passed
                V-->>S: ValidationResult(ok=True)
                S->>RM: run(attempt_fn)
                loop Attempt 1..max_attempts
                    RM->>G: run(workload)
                    G-->>RM: ExecutionResult
                    note over RM: Check if retry needed
                end
                RM-->>S: (FinalResult, attempts)
                S->>M: write(workload, FinalResult)
                M->>P: summarize(stats.txt)
                P-->>M: stats summary
                M->>M: Gather system environment details
                M-->>S: Write metadata.json
            end
        end
    end
    S-->>CLI: SchedulerSummary
    CLI->>CLI: Write Report files (CSV, JSON, MD)
```

## User Review Required

> [!IMPORTANT]
> - **Project Root**: All file creation will occur inside `/run/media/vedha/E/gtrace/workloadCollector/` to match the directory where existing scripts like [logger.py](file:///run/media/vedha/E/gtrace/workloadCollector/scripts/logger.py) are placed.
> - **Dry-Run Capabilities**: Since actual gem5 runs can require minutes to hours per benchmark and need target RISC-V binaries, the framework will support a robust `--dry-run` mode which skips binary checks and launches mock executions. This allows immediate testing of the entire scheduler, progress reporting, and output creation infrastructure.

## Proposed Changes

### Configuration Layer

Create YAML files under the `config` directory to customize execution options without modifying Python code.

#### [NEW] [workloads.yaml](file:///run/media/vedha/E/gtrace/workloadCollector/config/workloads.yaml)
Stores approximately 100 workloads mapping across CoreMark, Embench, Polybench, MiBench, GAPBS, NPB, and PARSEC suites.
*Because 100 workloads would result in a massive file (~2000 lines), we will construct a Python generator script to initialize it programmatically with rich parameters, ensuring completeness without placeholder entries.*

#### [NEW] [simulator.yaml](file:///run/media/vedha/E/gtrace/workloadCollector/config/simulator.yaml)
Defines target simulator paths (gem5 executable, CPU type, memory config, caches, limit parameters, debug flags, and retry parameters).

#### [NEW] [environment.yaml](file:///run/media/vedha/E/gtrace/workloadCollector/config/environment.yaml)
Contains system execution options, resource limitations (e.g., minimum disk space limits), and path structures.

#### [NEW] [logging.yaml](file:///run/media/vedha/E/gtrace/workloadCollector/config/logging.yaml)
Specifies parameters for console log formats, file paths, log levels, and backup rotations.

#### [NEW] [metadata_schema.json](file:///run/media/vedha/E/gtrace/workloadCollector/config/metadata_schema.json)
Specifies JSON Schema representation for `metadata.json` ensuring standard verification of output metrics.

---

### Scripts Layer

Create the missing Python logic to run the scheduler, handle metadata composition, and process CLI input.

#### [NEW] [metadata.py](file:///run/media/vedha/E/gtrace/workloadCollector/scripts/metadata.py)
Collects host system details (OS, CPU, memory), imports parsed simulation metrics (ticks, committed instructions, etc.), captures hashes of inputs/binaries, and writes `metadata.json`.

#### [NEW] [scheduler.py](file:///run/media/vedha/E/gtrace/workloadCollector/scripts/scheduler.py)
Orchestrates batch runs sequentially or in parallel using `ProcessPoolExecutor` or `ThreadPoolExecutor`. Updates progress reports, filters runs to support resume, and aggregates simulation results.

#### [NEW] [runner.py](file:///run/media/vedha/E/gtrace/workloadCollector/scripts/runner.py)
Initializes configurations, loads catalog entries, parses command line options, triggers scheduling, and compiles performance reports (CSV, JSON, MD) inside a `reports/` folder.

---

### Project Metadata Layer

#### [NEW] [requirements.txt](file:///run/media/vedha/E/gtrace/workloadCollector/requirements.txt)
Specifies necessary dependencies like `PyYAML` and `jsonschema`.

#### [NEW] [README.md](file:///run/media/vedha/E/gtrace/workloadCollector/README.md)
Comprehensive installation and execution instructions.

---

## Verification Plan

### Automated Verification
Run the runner using dry-run modes to verify the control flow:
- `python3 scripts/runner.py --dry-run` (Sequential dry run)
- `python3 scripts/runner.py --dry-run --parallel 4` (Parallel dry run with 4 workers)
- `python3 scripts/runner.py --dry-run --suite polybench` (Filtering by suite)
- `python3 scripts/runner.py --dry-run --repeat 2` (Testing repetition counting)

### Manual Verification
Inspect the outputs:
- Check that report files are written successfully under `reports/`.
- Verify the schema validation of generated `metadata.json` files.
- Inspect the log messages and progress console displays.
