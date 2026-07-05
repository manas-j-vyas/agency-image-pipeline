"""
app/utils/hash_utils.py
========================
Responsibility: Hashing helpers used by duplicate_finder.py.

Functions (to be implemented):
- file_sha256(path: Path, chunk_size: int = 65536) -> str
      Streamed hashing so large files don't get fully loaded into memory.

- image_phash(path: Path) -> str   (optional, future near-duplicate support)
      Perceptual hash for "visually similar" detection, separate from
      exact byte-level duplicate hashing.
"""

from pathlib import Path


def file_sha256(path: Path, chunk_size: int = 65536) -> str:
    raise NotImplementedError


def image_phash(path: Path) -> str:
    raise NotImplementedError
