"""
app/reports/json_report.py
=============================
Responsibility: Serialize a ReportData object to JSON.

Public API:

    def export_json(report: ReportData, output_path: Path) -> Path:
        '''Writes report as machine-readable JSON — useful if the
        agency later wants to feed results into another internal tool
        or dashboard.'''
"""

from pathlib import Path
from app.core.models import ReportData


def export_json(report: ReportData, output_path: Path) -> Path:
    raise NotImplementedError
