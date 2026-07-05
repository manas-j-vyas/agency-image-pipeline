"""
app/core/worker.py
===================
Responsibility: Orchestrates the full pipeline (scan -> detect
duplicates -> optimize -> report) OFF the main GUI thread, so
CustomTkinter's UI never freezes on large folders.

Public API:

    class PipelineWorker(threading.Thread):
        def __init__(
            self,
            config: AppConfig,
            on_progress: Callable[[int, int, str], None],
            on_log: Callable[[str], None],
            on_complete: Callable[[ReportData], None],
        ): ...
        def run(self):
            '''
            1. Scanner.scan(...)          -> emits progress + logs
            2. DuplicateFinder.find_...() -> marks ImageInfo.is_duplicate
            3. Optimizer.optimize_batch() -> emits progress + logs
            4. ReportGenerator.build()    -> on_complete(report_data)
            '''

Design notes:
- This is the ONLY module that imports `threading`/`queue`. GUI code
  never touches core modules directly during processing — it only
  starts a PipelineWorker and listens to its callbacks. This keeps
  core/ fully GUI-framework-agnostic (could later be reused in a CLI
  or web version with zero changes).
- Callbacks are thread-safe: GUI updates happen via
  `self.after(...)` scheduling in main_window.py, not directly from
  this worker thread.
"""

import threading
from typing import Callable

from app.config import AppConfig
from app.core.models import ReportData


class PipelineWorker(threading.Thread):
    def __init__(
        self,
        config: AppConfig,
        on_progress: Callable[[int, int, str], None],
        on_log: Callable[[str], None],
        on_complete: Callable[[ReportData], None],
    ):
        super().__init__(daemon=True)
        self.config = config
        self.on_progress = on_progress
        self.on_log = on_log
        self.on_complete = on_complete

    def run(self):
        raise NotImplementedError
