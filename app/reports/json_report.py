"""
app/reports/json_report.py
=============================
Serializes a ReportData object to JSON.
"""

import json
from pathlib import Path
from app.core.models import ReportData
from app.utils.file_utils import human_readable_size


def export_json(report: ReportData, output_path: Path) -> Path:
    data = {
        "total_images": report.total_images,
        "total_original_size_bytes": report.total_original_size,
        "total_optimized_size_bytes": report.total_optimized_size,
        "total_saved_bytes": report.total_saved,
        "per_format_counts": report.per_format_counts,
        "largest_images": [
            {"filename": img.filename, "path": str(img.path), "size_bytes": img.size_bytes}
            for img in report.largest_images
        ],
        "skipped_images": [
            {"filename": img.filename, "path": str(img.path)} for img in report.skipped_images
        ],
        "duplicate_groups": [
            [str(img.path) for img in group] for group in report.duplicate_groups
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return output_path
