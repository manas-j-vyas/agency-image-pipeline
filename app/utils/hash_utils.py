"""
app/utils/hash_utils.py
========================
Hashing helpers used by duplicate_finder.py.
"""

import hashlib
from pathlib import Path


def file_sha256(path: Path, chunk_size: int = 65536) -> str:
    """Streamed SHA-256 hash — never loads the whole file into memory."""
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError:
        return ""
