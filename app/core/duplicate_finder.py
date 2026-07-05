"""
app/core/duplicate_finder.py
=============================
Responsibility: Detect duplicate images among the ImageInfo list
produced by scanner.py.

Strategy (to be implemented):
- Fast pass: group by file size first (cheap pre-filter).
- Exact-duplicate pass: compute a content hash (e.g. SHA-256 via
  utils/hash_utils.py) only within same-size groups — avoids hashing
  every file in large folders.
- Optional future extension: perceptual hash (pHash/dHash) for
  near-duplicate detection (resized/re-exported versions of the same
  image). Kept as a separate method so it can be toggled on/off without
  touching exact-duplicate logic.

Public API:

    class DuplicateFinder:
        def find_exact_duplicates(self, images: list[ImageInfo]) -> list[list[ImageInfo]]:
            '''Returns groups of ImageInfo that are byte-identical.'''

        def find_near_duplicates(self, images: list[ImageInfo]) -> list[list[ImageInfo]]:
            '''(Optional/future) perceptual-hash based grouping.'''

Why separate from scanner.py:
Duplicate detection is a distinct concern (comparison across many files)
vs scanning (per-file classification). Keeping them apart means you can
swap the duplicate-detection algorithm later without touching the scanner.
"""

from typing import List
from app.core.models import ImageInfo


class DuplicateFinder:
    def find_exact_duplicates(self, images: List[ImageInfo]) -> List[List[ImageInfo]]:
        raise NotImplementedError

    def find_near_duplicates(self, images: List[ImageInfo]) -> List[List[ImageInfo]]:
        raise NotImplementedError
