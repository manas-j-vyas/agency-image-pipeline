"""
app/core/duplicate_finder.py
=============================
Detects exact (byte-identical) duplicate images among a list of
ImageInfo produced by scanner.py.

Strategy: group by file size first (cheap pre-filter), then only
compare SHA-256 hashes within same-size groups. This avoids hashing
every single file pair in large agency folders.
"""

from collections import defaultdict
from typing import List

from app.core.models import ImageInfo


class DuplicateFinder:
    def find_exact_duplicates(self, images: List[ImageInfo]) -> List[List[ImageInfo]]:
        by_size = defaultdict(list)
        for img in images:
            if img.status == "unsupported":
                continue
            by_size[img.size_bytes].append(img)

        duplicate_groups: List[List[ImageInfo]] = []
        for size_group in by_size.values():
            if len(size_group) < 2:
                continue
            by_hash = defaultdict(list)
            for img in size_group:
                if img.file_hash:
                    by_hash[img.file_hash].append(img)
            for hash_group in by_hash.values():
                if len(hash_group) > 1:
                    # Keep original order stable; first item = "keeper".
                    for img in hash_group[1:]:
                        img.is_duplicate = True
                    duplicate_groups.append(hash_group)

        return duplicate_groups

    def find_near_duplicates(self, images: List[ImageInfo]) -> List[List[ImageInfo]]:
        """Reserved for future perceptual-hash based near-duplicate
        detection (e.g. same photo re-exported at a different size).
        Not required for v1."""
        return []
