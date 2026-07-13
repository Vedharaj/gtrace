"""
utils.py

Small, dependency-free helper functions shared across the framework.
Kept separate (rather than scattered inline) so every other module can stay
focused on its single responsibility (SRP) and so these helpers are trivially
unit-testable in isolation.
"""
from __future__ import annotations

import hashlib
import os
import platform
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Optional


def sha256_of_file(path: Path, chunk_size: int = 1024 * 1024) -> Optional[str]:
    """Return the SHA-256 hex digest of a file, or None if it doesn't exist."""
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_of_files(paths: list[Path]) -> Optional[str]:
    """Combined SHA-256 across multiple files (order-stable), or None if empty."""
    existing = [p for p in paths if p.exists() and p.is_file()]
    if not existing:
        return None
    digest = hashlib.sha256()
    for p in sorted(existing):
        digest.update(sha256_of_file(p).encode())
    return digest.hexdigest()


def get_hostname() -> str:
    try:
        return socket.gethostname()
    except OSError:
        return "unknown-host"


def get_python_version() -> str:
    return sys.version.split()[0]


def get_os_info() -> str:
    return f"{platform.system()} {platform.release()} ({platform.machine()})"


def get_cpu_info() -> str:
    """Best-effort human-readable CPU description, Linux-first with fallback."""
    cpuinfo_path = Path("/proc/cpuinfo")
    if cpuinfo_path.exists():
        try:
            with cpuinfo_path.open() as f:
                for line in f:
                    if line.lower().startswith("model name"):
                        return line.split(":", 1)[1].strip()
        except OSError:
            pass
    return platform.processor() or "unknown-cpu"


def get_memory_info() -> str:
    """Best-effort total system memory, Linux-first with fallback."""
    meminfo_path = Path("/proc/meminfo")
    if meminfo_path.exists():
        try:
            with meminfo_path.open() as f:
                for line in f:
                    if line.startswith("MemTotal"):
                        kb = int(line.split()[1])
                        return f"{kb / (1024 * 1024):.2f} GB"
        except (OSError, ValueError, IndexError):
            pass
    return "unknown"


def get_git_commit(repo_root: Path) -> str:
    """Return the current git commit hash, or 'unknown' if unavailable."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown"


def get_installed_packages() -> list[str]:
    """Return a list of 'package==version' strings via importlib.metadata."""
    try:
        from importlib import metadata

        return sorted(
            f"{dist.metadata['Name']}=={dist.version}"
            for dist in metadata.distributions()
            if dist.metadata.get("Name")
        )
    except Exception:
        return []


def filtered_env_vars(allowlist_prefixes: list[str]) -> dict[str, str]:
    """Return only environment variables whose key starts with an allowed prefix."""
    result = {}
    for key, value in os.environ.items():
        if any(key.startswith(prefix) for prefix in allowlist_prefixes):
            result[key] = value
    return result


def free_disk_mb(path: Path) -> float:
    """Free disk space in MB for the filesystem containing `path`."""
    usage = shutil.disk_usage(path if path.exists() else path.parent)
    return usage.free / (1024 * 1024)


def human_duration(seconds: float) -> str:
    """Format a duration in seconds as e.g. '1h 03m 12s'."""
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes:02d}m {secs:02d}s"
    if minutes:
        return f"{minutes}m {secs:02d}s"
    return f"{secs}s"


def ensure_dir(path: Path) -> Path:
    """Create a directory (and parents) if missing, returning the Path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_gem5_version(executable: str) -> str:
    """Best-effort `gem5 --version` query; falls back to 'unknown'."""
    try:
        result = subprocess.run(
            [executable, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().splitlines()[0]
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown"