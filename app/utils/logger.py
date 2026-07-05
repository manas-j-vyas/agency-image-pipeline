"""
app/utils/logger.py
====================
Logging abstraction: writes every message to a rotating log file on
disk (for support/debugging after the fact) AND forwards it to the
GUI's live log console via a callback, without core modules needing
to know Tkinter exists.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Callable, Optional


class PipelineLogger:
    def __init__(self, log_file: Path, ui_callback: Optional[Callable[[str, str], None]] = None):
        """
        ui_callback(level: str, message: str) -> None
            Called for every log line so the GUI can render it with
            appropriate color/tagging (info/warning/error).
        """
        self.ui_callback = ui_callback

        self._logger = logging.getLogger("agency_image_pipeline")
        self._logger.setLevel(logging.DEBUG)
        self._logger.handlers.clear()

        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=2_000_000, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
        )
        self._logger.addHandler(file_handler)

    def _emit(self, level: str, message: str):
        getattr(self._logger, level.lower())(message)
        if self.ui_callback:
            self.ui_callback(level, message)

    def info(self, message: str):
        self._emit("INFO", message)

    def warning(self, message: str):
        self._emit("WARNING", message)

    def error(self, message: str):
        self._emit("ERROR", message)

    def debug(self, message: str):
        self._emit("DEBUG", message)
