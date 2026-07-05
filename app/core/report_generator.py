"""
app/core/report_generator.py
=============================
Responsibility: STEP 5 — aggregate everything into a ReportData object,
and optionally export it (handled by app/reports/*.py).

Input:
- list[ImageInfo] from scanner (includes skipped/unsupported/duplicates)
- list[OptimizationResult] from optimizer

Output:
- A single ReportData instance containing:
    total_images, total_original_size, total_optimized_size,
    total_saved (bytes + percent), largest_images (top N by size),
    skipped_images, duplicate_groups, per_format_counts

Public API:

    class ReportGenerator:
        def build(
            self,
            scanned: list[ImageInfo],
            duplicates: list[list[ImageInfo]],
            results: list[OptimizationResult],
        ) -> ReportData: ...

Why separate from optimizer.py:
The optimizer's job ends once a file is processed. Aggregating stats
and presenting them (sorting "largest images", computing totals) is a
reporting concern — keeping it separate means report format/logic can
change (e.g. add CSV export) without touching optimization code.
"""

from typing import List
from app.core.models import ImageInfo, OptimizationResult, ReportData


class ReportGenerator:
    def build(
        self,
        scanned: List[ImageInfo],
        duplicates: List[List[ImageInfo]],
        results: List[OptimizationResult],
    ) -> ReportData:
        raise NotImplementedError
