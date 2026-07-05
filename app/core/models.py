"""
app/core/models.py
===================
Plain data structures shared across the app (scanner -> optimizer ->
report_generator -> GUI). Keeping these separate avoids circular imports
and keeps every module speaking the same "language".

Key classes (to be implemented):

- ImageInfo
    path, filename, extension, size_bytes, width, height,
    file_hash (for duplicate detection), is_large, is_duplicate,
    status ("pending" | "optimized" | "skipped" | "duplicate" | "unsupported")

- OptimizationResult
    source: ImageInfo
    output_path, original_size_bytes, optimized_size_bytes,
    saved_bytes, saved_percent, success: bool, error_message: str | None

- ReportData
    total_images, total_original_size, total_optimized_size,
    total_saved, largest_images (list[ImageInfo]),
    skipped_images (list[ImageInfo]), duplicate_groups (list[list[ImageInfo]]),
    per_format_counts (dict)

Why this module exists:
Without shared dataclasses, the scanner/optimizer/report modules would
pass around loose dicts/tuples, which becomes unmaintainable fast in a
GUI app with threads. These models are the "contract" between modules.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List


@dataclass
class ImageInfo:
    path: Path
    filename: str
    extension: str
    size_bytes: int
    width: int = 0
    height: int = 0
    file_hash: str = ""
    is_large: bool = False
    is_duplicate: bool = False
    status: str = "pending"


@dataclass
class OptimizationResult:
    source: ImageInfo
    output_path: Optional[Path] = None
    original_size_bytes: int = 0
    optimized_size_bytes: int = 0
    saved_bytes: int = 0
    saved_percent: float = 0.0
    success: bool = False
    error_message: Optional[str] = None


@dataclass
class ReportData:
    total_images: int = 0
    total_original_size: int = 0
    total_optimized_size: int = 0
    total_saved: int = 0
    largest_images: List[ImageInfo] = field(default_factory=list)
    skipped_images: List[ImageInfo] = field(default_factory=list)
    duplicate_groups: List[List[ImageInfo]] = field(default_factory=list)
    per_format_counts: dict = field(default_factory=dict)
