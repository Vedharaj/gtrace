"""
retry.py

`RetryManager` centralizes retry/backoff policy so that BenchmarkRunner does
not need to know about sleep timing, attempt counting, or which failure
categories are retryable - it just asks "should I retry this?" and "how long
should I wait?".
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, TypeVar

from logger import get_logger

T = TypeVar("T")

logger = get_logger("gtrace.retry")


@dataclass
class RetryPolicy:
    max_attempts: int = 2
    backoff_seconds: float = 5.0
    backoff_multiplier: float = 2.0
    retry_on: tuple[str, ...] = field(
        default_factory=lambda: ("timeout", "nonzero_exit", "missing_output")
    )

    @staticmethod
    def from_dict(data: dict) -> "RetryPolicy":
        return RetryPolicy(
            max_attempts=int(data.get("max_attempts", 2)),
            backoff_seconds=float(data.get("backoff_seconds", 5.0)),
            backoff_multiplier=float(data.get("backoff_multiplier", 2.0)),
            retry_on=tuple(data.get("retry_on", ["timeout", "nonzero_exit", "missing_output"])),
        )


class RetryManager:
    """
    Wraps a single callable execution with the configured retry policy.

    The wrapped callable is expected to return an object with a boolean
    `.success` attribute and a `.failure_reason` attribute (a string, one of
    RetryPolicy.retry_on's vocabulary, or None on success) - this matches
    `ExecutionResult` from gem5_runner.py, keeping RetryManager decoupled
    from Gem5Runner's internals.
    """

    def __init__(self, policy: RetryPolicy) -> None:
        self._policy = policy

    def run(self, attempt_fn: Callable[[int], T], is_success: Callable[[T], bool],
             failure_reason: Callable[[T], str]) -> tuple[T, int]:
        """
        Execute `attempt_fn` up to `max_attempts` additional times on
        retryable failure.

        Returns (last_result, total_attempts_made).
        """
        total_attempts = self._policy.max_attempts + 1
        delay = self._policy.backoff_seconds
        result: T | None = None

        for attempt in range(1, total_attempts + 1):
            result = attempt_fn(attempt)
            if is_success(result):
                if attempt > 1:
                    logger.info("Succeeded on attempt %d/%d", attempt, total_attempts)
                return result, attempt

            reason = failure_reason(result)
            retryable = reason in self._policy.retry_on
            is_last = attempt == total_attempts

            if not retryable:
                logger.warning("Failure reason '%s' is not retryable; stopping.", reason)
                return result, attempt

            if is_last:
                logger.error(
                    "Exhausted %d attempts (last failure: %s)", total_attempts, reason
                )
                return result, attempt

            logger.warning(
                "Attempt %d/%d failed (%s); retrying in %.1fs",
                attempt, total_attempts, reason, delay,
            )
            time.sleep(delay)
            delay *= self._policy.backoff_multiplier

        # Unreachable in practice, but keeps type checkers happy.
        return result, total_attempts