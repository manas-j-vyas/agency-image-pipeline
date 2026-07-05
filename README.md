# Agency Image Pipeline

A production desktop application for auditing and optimizing project
image folders — built for internal agency use. Not a generic "image
compressor": it scans, detects duplicates/large files/unsupported
formats, optimizes with configurable settings, and produces a report.

Distributed as a **single standalone Windows .exe**. The people who use
it never install Python, never open a terminal, and never see any code
— they just double-click `AgencyImagePipeline.exe`.

---

## For the developer: building the .exe

You only need to do this once per release. Requires Python 3.10+ installed
on your Windows machine (only for building — not for running the final app).

**Easiest way:** double-click `build.bat` in this folder. It will:
1. Create a local virtual environment
2. Install dependencies (customtkinter, Pillow, PyInstaller)
3. Run PyInstaller using `build.spec`
4. Open the `dist` folder containing `AgencyImagePipeline.exe`

That `.exe` in `dist/` is the entire deliverable — copy it anywhere
(a shared drive, a USB stick, another PC) and it runs standalone with
no installation.

If you'd rather run the build manually instead of double-clicking `build.bat`:
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pyinstaller build.spec --noconfirm
```

### Rebuilding after code changes
Just re-run `build.bat` (or the manual commands above) — it overwrites
`dist\AgencyImagePipeline.exe` with the updated build.

### Customizing the icon/branding
Replace `assets/icons/app_icon.ico` with the agency's real logo (must
be a valid multi-size `.ico` file) before building, and it will appear
as the exe's icon and taskbar icon.

---

## For the end user: running the app

1. Double-click `AgencyImagePipeline.exe`
2. Click **Browse…** and select the project image folder
3. (Optional) choose a different output folder — defaults to
   `optimized_output` inside the source folder
4. Click **Start Processing**
5. Watch the live log and progress bar
6. When finished, view the report summary, click **Open Output Folder**
   to grab the optimized images, or **Export Report** for an HTML report

Settings (max width, quality, WebP conversion, etc.) are available via
the **⚙ Settings** button or **File > Settings** menu, and persist
automatically between launches.

Logs are saved automatically to:
`%APPDATA%\AgencyImagePipeline\logs\pipeline.log`
(accessible via **File > Open Logs Folder** in the app — useful for
troubleshooting without needing a developer involved).

---

## Project Structure

```
agency_image_pipeline/
├── main.py                     # Entry point + global crash-dialog handler
├── build.spec                   # PyInstaller build configuration
├── build.bat                    # One-click build script (developer use)
├── requirements.txt
├── app/
│   ├── config.py                # AppConfig + JSON persistence (%APPDATA%)
│   ├── gui/
│   │   ├── main_window.py       # Main window / controller
│   │   ├── dialogs.py           # Error dialog, Settings dialog, About dialog
│   │   ├── widgets.py           # StatCard, LogConsole, FolderPicker
│   │   └── theme.py             # Dark theme + color/font constants
│   ├── core/
│   │   ├── models.py            # ImageInfo, OptimizationResult, ReportData
│   │   ├── scanner.py           # Recursive scan + format/size detection
│   │   ├── duplicate_finder.py  # Exact duplicate detection (SHA-256)
│   │   ├── optimizer.py         # Resize / compress / WebP conversion
│   │   ├── report_generator.py  # Aggregates scan + optimize results
│   │   └── worker.py            # Background thread orchestration
│   ├── utils/
│   │   ├── file_utils.py, hash_utils.py, logger.py
│   └── reports/
│       ├── html_report.py, json_report.py
├── assets/icons/                # App icon (.ico/.png)
└── tests/                       # Unit tests per core module
```

## Why it's built this way

- **GUI never touches core logic directly** — only through
  `app/core/worker.PipelineWorker`, which runs on a background thread
  via Python's `threading` module. This keeps the UI responsive on
  large folders and is what makes the progress bar/live log possible.
- **Every uncaught error shows a dialog**, never a silent crash —
  critical for a windowed .exe where there's no visible console to
  print a traceback to. Errors are also written to a log file so you
  can debug issues the end user reports.
- **Settings persist to `%APPDATA%`**, not next to the .exe, since a
  double-click-installed program on a shared/locked-down machine may
  not have write access to its own folder.
- **Each pipeline stage is independently testable** (`scanner.py` →
  `duplicate_finder.py` → `optimizer.py` → `report_generator.py`),
  matching the 5-step workflow exactly.
