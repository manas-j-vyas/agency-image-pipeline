"""
app/utils/file_utils.py
========================
Responsibility: Small, reusable filesystem helpers used across core
modules — kept here so no module duplicates path/size logic.

Functions (to be implemented):
- iter_files_recursive(folder: Path) -> Iterator[Path]
- get_file_size(path: Path) -> int
- human_readable_size(num_bytes: int) -> str      # e.g. "3.2 MB"
- ensure_output_subfolder(source_root, output_root, file_path) -> Path
      (mirrors original relative folder structure into output folder)
- is_supported_extension(path: Path, supported: tuple[str, ...]) -> bool
"""

from pathlib import Path
from typing import Iterator, Tuple


def iter_files_recursive(folder: Path) -> Iterator[Path]:
    raise NotImplementedError


def get_file_size(path: Path) -> int:
    raise NotImplementedError


def human_readable_size(num_bytes: int) -> str:
    raise NotImplementedError


def ensure_output_subfolder(source_root: Path, output_root: Path, file_path: Path) -> Path:
    raise NotImplementedError


def is_supported_extension(path: Path, supported: Tuple[str, ...]) -> bool:
    raise NotImplementedError
