"""Streaming, single-pass parser for gem5 ``stats.txt`` files."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from models.metric import ParseWarning
from utils.constants import COMMENT_PREFIX
from utils.logger import get_logger
from utils.regex import SEPARATOR_LINE_PATTERN

logger = get_logger(__name__)


class StatsParser:
    """Streams a gem5 stats.txt file and yields raw, cleaned lines.

    This class has a single responsibility: efficient, O(n), line-by-line
    file iteration with structural noise (blank lines, comments,
    separators) filtered out. It knows nothing about metric semantics —
    that is the job of :class:`services.extractor.MetricExtractor`.
    """

    def __init__(self, file_path: Path) -> None:
        """Initialize the parser for a given file path.

        Args:
            file_path: Path to the stats.txt file on disk.
        """
        self._file_path = file_path

    def iter_lines(self) -> Iterator[tuple[int, str]]:
        """Lazily yield (line_number, line_text) for meaningful lines.

        Blank lines, comment-only lines (starting with '#'), and
        separator lines (e.g. dashed rules) are skipped. The file is
        streamed, never fully loaded into memory.

        Yields:
            Tuples of (1-indexed line number, stripped line text).

        Raises:
            FileNotFoundError: If the underlying file does not exist.
            OSError: If the file cannot be read.
        """
        if not self._file_path.exists():
            raise FileNotFoundError(f"File not found: {self._file_path}")

        with self._file_path.open("r", encoding="utf-8", errors="replace") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                stripped = raw_line.strip()

                if not stripped:
                    continue
                if stripped.startswith(COMMENT_PREFIX):
                    continue
                if SEPARATOR_LINE_PATTERN.match(stripped):
                    continue

                yield line_number, stripped

    def validate_not_empty(self) -> ParseWarning | None:
        """Check whether the file has zero bytes.

        Returns:
            A ParseWarning describing the issue, or None if the file has
            content.
        """
        if self._file_path.stat().st_size == 0:
            return ParseWarning(message="File is empty")
        return None