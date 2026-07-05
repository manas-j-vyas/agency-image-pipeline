"""
app/core/report_generator.py
=============================
STEP 5: aggregates scan + optimize results into a single ReportData
object used by the GUI summary panel and (optionally) exported reports.
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
        report = ReportData()

        report.total_images = len(scanned)
        report.skipped_images = [img for img in scanned if img.status == "unsupported"]
        report.duplicate_groups = duplicates

        successful_results = [r for r in results if r.success]
        report.total_original_size = sum(r.original_size_bytes for r in successful_results)
        report.total_optimized_size = sum(r.optimized_size_bytes for r in successful_results)
        report.total_saved = report.total_original_size - report.total_optimized_size

        report.largest_images = sorted(
            [img for img in scanned if img.status != "unsupported"],
            key=lambda i: i.size_bytes,
            reverse=True,
        )[:10]

        per_format = {}
        for img in scanned:
            key = img.extension.lstrip(".").upper() or "UNKNOWN"
            per_format[key] = per_format.get(key, 0) + 1
        report.per_format_counts = per_format

        return report
