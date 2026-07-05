# Agency Image Pipeline

Internal agency tool for scanning, auditing, and optimizing project image
folders (not a generic "image compressor" — it's a full audit + optimize
pipeline with reporting).

## Project Structure

```
agency_image_pipeline/
├── main.py                     # Entry point only — no logic
├── requirements.txt
├── app/
│   ├── config.py                # AppConfig: all tunable settings
│   ├── gui/
│   │   ├── main_window.py       # Main CTk window / controller
│   │   ├── widgets.py           # StatCard, LogConsole, SettingsPanel, FolderPicker
│   │   └── theme.py             # Dark theme + color/font constants
│   ├── core/
│   │   ├── models.py            # ImageInfo, OptimizationResult, ReportData
│   │   ├── scanner.py           # Recursive scan + format/size detection
│   │   ├── duplicate_finder.py  # Exact (and future near-) duplicate detection
│   │   ├── optimizer.py         # Resize / compress / WebP conversion
│   │   ├── report_generator.py  # Aggregates scan + optimize results
│   │   └── worker.py            # Threaded pipeline orchestration
│   ├── utils/
│   │   ├── file_utils.py        # Path/size helpers
│   │   ├── hash_utils.py        # SHA-256 (+ future perceptual hash)
│   │   └── logger.py            # Shared logger -> file + GUI console
│   └── reports/
│       ├── html_report.py       # Export ReportData -> HTML
│       └── json_report.py       # Export ReportData -> JSON
├── assets/                      # Icons/logo for the GUI
└── tests/                       # Unit tests per core module
```

## Data Flow

```
User selects folder
        │
        ▼
   Scanner.scan()  ──────────────► list[ImageInfo]
        │
        ▼
DuplicateFinder.find_exact_duplicates()  ──► marks duplicates
        │
        ▼
   Optimizer.optimize_batch()  ────────────► list[OptimizationResult]
        │
        ▼
ReportGenerator.build()  ────────────────► ReportData
        │
        ▼
GUI displays summary + (optional) html_report/json_report export
```

All of the above is driven by `PipelineWorker` (a background thread) so
the CustomTkinter GUI stays responsive, communicating back to
`main_window.py` via progress/log/complete callbacks.

## Why this structure

- **GUI never touches core logic directly** — only through `worker.py`.
  This means `app/core` could be reused later as a CLI tool or batch
  script with zero changes.
- **Each pipeline stage is a separate, independently testable module**
  (scan → dedupe → optimize → report), matching your 5-step workflow
  exactly.
- **`models.py` is the shared contract** between stages, so no module
  passes around loose dicts/tuples.
- **`utils/` and `reports/`** hold cross-cutting or output-only concerns,
  kept out of core business logic.

## Status

This is the architecture scaffold only. Every module currently contains
docstrings + method signatures (`raise NotImplementedError`) describing
exactly what it will do. Next step: implement modules one at a time,
starting with `models.py` → `scanner.py` → `duplicate_finder.py` →
`optimizer.py` → `report_generator.py` → `worker.py` → GUI.
