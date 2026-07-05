"""
app/core/worker.py
===================
Runs the full pipeline (scan -> detect duplicates -> optimize ->
report) on a background thread so the GUI never freezes, and reports
progress/logs/completion/errors back via callbacks.

This is the ONLY module that imports `threading`. GUI code never
touches scanner/optimizer/report_generator directly.
"""

import threading
import traceback
from pathlib import Path
from typing import Callable, Optional

from app.config import AppConfig
from app.core.models import ReportData
from app.core.scanner import Scanner
from app.core.duplicate_finder import DuplicateFinder
from app.core.optimizer import Optimizer
from app.core.report_generator import ReportGenerator


class PipelineWorker(threading.Thread):
    def __init__(
        self,
        config: AppConfig,
        source_folder: Path,
        output_folder: Path,
        logger,
        on_progress: Callable[[str, int, int], None],
        on_complete: Callable[[ReportData], None],
        on_error: Callable[[str, str], None],
    ):
        super().__init__(daemon=True)
        self.config = config
        self.source_folder = source_folder
        self.output_folder = output_folder
        self.logger = logger
        self.on_progress = on_progress
        self.on_complete = on_complete
        self.on_error = on_error
        self._cancel_event = threading.Event()

    def cancel(self):
        self._cancel_event.set()

    def run(self):
        try:
            scanner = Scanner(self.config, self.logger)
            dup_finder = DuplicateFinder()
            optimizer = Optimizer(self.config, self.logger)
            reporter = ReportGenerator()

            self.logger.info(f"Starting scan: {self.source_folder}")
            scanned = scanner.scan(
                self.source_folder,
                progress_callback=lambda cur, tot: self.on_progress("Scanning", cur, tot),
            )

            if self._cancel_event.is_set():
                self.logger.warning("Cancelled during scan.")
                return

            self.logger.info("Checking for duplicate images...")
            duplicates = dup_finder.find_exact_duplicates(scanned)
            if duplicates:
                self.logger.warning(f"Found {len(duplicates)} duplicate group(s).")

            # Only optimize supported, non-duplicate images.
            to_optimize = [
                img for img in scanned
                if img.status != "unsupported" and not img.is_duplicate
            ]

            if self._cancel_event.is_set():
                self.logger.warning("Cancelled before optimization.")
                return

            self.logger.info(f"Optimizing {len(to_optimize)} image(s)...")
            results = optimizer.optimize_batch(
                to_optimize,
                self.source_folder,
                self.output_folder,
                progress_callback=lambda cur, tot: self.on_progress("Optimizing", cur, tot),
            )

            report = reporter.build(scanned, duplicates, results)
            self.logger.info("Pipeline complete.")
            self.on_complete(report)

        except Exception as e:
            tb = traceback.format_exc()
            self.logger.error(f"Pipeline failed: {e}\n{tb}")
            self.on_error(str(e), tb)
