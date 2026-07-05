"""
app/core/scanner.py
====================
Responsibility: STEP 2 + 3 of the workflow.

- Recursively walks the selected project folder.
- Builds an ImageInfo for every file found.
- Classifies each file:
    * supported (jpg/jpeg/png/webp) vs unsupported
    * "large" if size_bytes > config.large_image_threshold_mb
- Reads width/height via Pillow (Image.open, without full decode when possible).
- Delegates hash computation to utils/hash_utils.py (kept separate so
  duplicate_finder.py can reuse the same hashing logic independently).

Public API (to be implemented):

    class Scanner:
        def __init__(self, config: AppConfig, logger): ...
        def scan(self, folder: Path) -> list[ImageInfo]:
            '''Walks folder recursively, returns list[ImageInfo].
            Emits progress via logger/callback for the GUI progress bar.'''

Design notes:
- Scanning is I/O bound and can be slow on huge folders, so `scan()`
  accepts an optional `progress_callback(current, total)` used by
  worker.py to update the GUI without the scanner knowing about Tkinter.
- Scanner does NOT modify or optimize anything — pure read/detect only.
  This separation keeps optimize logic (which touches disk output)
  independent and independently testable.
"""

from pathlib import Path
from typing import Callable, Optional, List

from app.core.models import ImageInfo
from app.config import AppConfig


class Scanner:
    def __init__(self, config: AppConfig, logger=None):
        self.config = config
        self.logger = logger

    def scan(
        self,
        folder: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[ImageInfo]:
        raise NotImplementedError
