"""Simple in-memory cache for parsed file results, keyed by file_id.

Avoids re-parsing the same stats.txt file on every metrics request.
Thread-safe for the simple get/set access pattern used by Flask's
default (threaded) dev server. For multi-process production deployment,
swap this for a shared store (Redis, etc.) behind the same interface.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Generic, TypeVar

from utils.constants import CACHE_TTL_SECONDS
from utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


@dataclass(slots=True)
class _CacheEntry(Generic[T]):
    """Internal wrapper pairing a cached value with its insertion time."""

    value: T
    inserted_at: float


class ResultCache(Generic[T]):
    """A minimal thread-safe, TTL-based in-memory cache.

    Attributes:
        ttl_seconds: How long an entry remains valid before expiring.
    """

    def __init__(self, ttl_seconds: int = CACHE_TTL_SECONDS) -> None:
        """Initialize an empty cache.

        Args:
            ttl_seconds: Time-to-live for cache entries, in seconds.
        """
        self.ttl_seconds = ttl_seconds
        self._store: dict[str, _CacheEntry[T]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> T | None:
        """Retrieve a cached value if present and not expired.

        Args:
            key: The cache key (typically a file_id).

        Returns:
            The cached value, or None if missing/expired.
        """
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if time.monotonic() - entry.inserted_at > self.ttl_seconds:
                del self._store[key]
                return None
            return entry.value

    def set(self, key: str, value: T) -> None:
        """Store a value in the cache under the given key.

        Args:
            key: The cache key (typically a file_id).
            value: The value to cache.
        """
        with self._lock:
            self._store[key] = _CacheEntry(value=value, inserted_at=time.monotonic())

    def delete(self, key: str) -> None:
        """Remove a key from the cache if present.

        Args:
            key: The cache key to remove.
        """
        with self._lock:
            self._store.pop(key, None)

    def exists(self, key: str) -> bool:
        """Check whether a non-expired entry exists for a key.

        Args:
            key: The cache key to check.

        Returns:
            True if a valid cached entry exists.
        """
        return self.get(key) is not None