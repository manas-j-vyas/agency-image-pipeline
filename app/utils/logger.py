"""
app/utils/logger.py
====================
Responsibility: A tiny logging abstraction that both writes to a
rotating log file AND forwards messages to the GUI's live log console
(via a callback), without core modules needing to know Tkinter exists.

Public API:

    class PipelineLogger:
        def __init__(self, log_file: Path, ui_callback: Callable[[str], None] | None = None): ...
        def info(self, message: str): ...
        def warning(self, message: str): ...
        def error(self, message: str): ...

Design notes:
- Core modules (scanner, optimizer, etc.) accept a `logger` argument
  of this type — never `print()` directly. That's what lets the GUI's
  "Live processing logs" panel show real-time output cleanly.
"""

from pathlib import Path
from typing import Callable, Optional


class PipelineLogger:
    def __init__(self, log_file: Path, ui_callback: Optional[Callable[[str], None]] = None):
        self.log_file = log_file
        self.ui_callback = ui_callback

    def info(self, message: str):
        raise NotImplementedError

    def warning(self, message: str):
        raise NotImplementedError

    def error(self, message: str):
        raise NotImplementedError
