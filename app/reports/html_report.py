"""
app/reports/html_report.py
============================
Renders a ReportData object into a standalone, shareable HTML report
(useful for QA or attaching to client/internal handoffs).
"""

from pathlib import Path
from app.core.models import ReportData
from app.utils.file_utils import human_readable_size

_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Agency Image Pipeline - Report</title>
<style>
  body {{ font-family: Segoe UI, Arial, sans-serif; background: #1a1a1a; color: #f5f5f5; padding: 30px; }}
  h1 {{ font-size: 22px; }}
  .cards {{ display: flex; gap: 16px; flex-wrap: wrap; margin: 20px 0; }}
  .card {{ background: #232323; border-radius: 10px; padding: 16px 20px; min-width: 160px; }}
  .card .label {{ font-size: 12px; color: #a3a3a3; }}
  .card .value {{ font-size: 22px; font-weight: bold; margin-top: 6px; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
  th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid #3a3a3a; font-size: 13px; }}
  th {{ color: #a3a3a3; font-weight: normal; }}
  h2 {{ font-size: 16px; margin-top: 34px; }}
</style>
</head>
<body>
  <h1>Agency Image Pipeline &mdash; Processing Report</h1>
  <div class="cards">
    <div class="card"><div class="label">Total Images</div><div class="value">{total_images}</div></div>
    <div class="card"><div class="label">Original Size</div><div class="value">{original_size}</div></div>
    <div class="card"><div class="label">Optimized Size</div><div class="value">{optimized_size}</div></div>
    <div class="card"><div class="label">Space Saved</div><div class="value">{saved_size}</div></div>
    <div class="card"><div class="label">Duplicate Groups</div><div class="value">{dup_count}</div></div>
    <div class="card"><div class="label">Skipped / Unsupported</div><div class="value">{skipped_count}</div></div>
  </div>

  <h2>Largest Images</h2>
  <table>
    <tr><th>Filename</th><th>Size</th></tr>
    {largest_rows}
  </table>

  <h2>Duplicate Groups</h2>
  <table>
    <tr><th>Group</th><th>Files</th></tr>
    {duplicate_rows}
  </table>

  <h2>Skipped / Unsupported Files</h2>
  <table>
    <tr><th>Filename</th></tr>
    {skipped_rows}
  </table>
</body>
</html>
"""


def export_html(report: ReportData, output_path: Path) -> Path:
    largest_rows = "".join(
        f"<tr><td>{img.filename}</td><td>{human_readable_size(img.size_bytes)}</td></tr>"
        for img in report.largest_images
    ) or "<tr><td colspan='2'>None</td></tr>"

    duplicate_rows = "".join(
        f"<tr><td>Group {i+1}</td><td>{', '.join(img.filename for img in group)}</td></tr>"
        for i, group in enumerate(report.duplicate_groups)
    ) or "<tr><td colspan='2'>No duplicates found</td></tr>"

    skipped_rows = "".join(
        f"<tr><td>{img.filename}</td></tr>" for img in report.skipped_images
    ) or "<tr><td>None</td></tr>"

    html = _TEMPLATE.format(
        total_images=report.total_images,
        original_size=human_readable_size(report.total_original_size),
        optimized_size=human_readable_size(report.total_optimized_size),
        saved_size=human_readable_size(report.total_saved),
        dup_count=len(report.duplicate_groups),
        skipped_count=len(report.skipped_images),
        largest_rows=largest_rows,
        duplicate_rows=duplicate_rows,
        skipped_rows=skipped_rows,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path
