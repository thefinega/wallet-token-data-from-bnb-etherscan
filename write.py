"""Persist a report to a UTF-8 encoded text file."""

from __future__ import annotations

from pathlib import Path


def write_results(path: str, text: str, *, append: bool = True) -> Path:
    """Write *text* to *path*, ensuring a trailing newline.

    The file handle is always closed via a context manager. When *append* is
    ``True`` (the default) the report is appended, which keeps every run
    separated by its own terminating newline.
    """
    target = Path(path)
    mode = "a" if append else "w"
    with target.open(mode, encoding="utf-8") as handle:
        handle.write(text)
        if not text.endswith("\n"):
            handle.write("\n")
    return target
