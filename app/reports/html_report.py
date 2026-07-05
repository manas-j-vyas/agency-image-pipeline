"""
app/reports/html_report.py
============================
Responsibility: Render a ReportData object into a standalone,
shareable HTML report (useful for the agency to attach to client
handoffs or internal QA).

Public API:

    def export_html(report: ReportData, output_path: Path) -> Path:
        '''Renders a simple, styled HTML summary (tables + basic CSS)
        and writes it to output_path. Returns the path written.'''

Design notes:
- Kept separate from report_generator.py: that module BUILDS the data,
  this module PRESENTS it. Adding a PDF or CSV export later just means
  adding pdf_report.py / csv_report.py alongside this one — no changes
  to core logic.
"""

from pathlib import Path
from app.core.models import ReportData


def export_html(report: ReportData, output_path: Path) -> Path:
    raise NotImplementedError
