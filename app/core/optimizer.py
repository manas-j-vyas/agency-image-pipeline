"""
app/core/optimizer.py
======================
Responsibility: STEP 4 of the workflow — the actual image processing.

For each ImageInfo NOT marked as duplicate/unsupported/skipped:
1. Open with Pillow.
2. Resize if width > config.max_width (maintain aspect ratio).
3. Decide output format:
   - If config.convert_to_webp: JPG/PNG -> WebP
   - If PNG has alpha channel AND config.preserve_transparent_png:
     keep RGBA mode through resize/convert (WebP supports alpha too).
   - Otherwise keep original format but re-compress.
4. Save into config.output_folder, mirroring the original relative
   subfolder structure (so the agency's folder layout is preserved).
5. Return an OptimizationResult with before/after sizes.

Public API:

    class Optimizer:
        def __init__(self, config: AppConfig, logger=None): ...
        def optimize_one(self, image: ImageInfo) -> OptimizationResult: ...
        def optimize_batch(
            self,
            images: list[ImageInfo],
            progress_callback: Callable[[int, int], None] | None = None,
        ) -> list[OptimizationResult]: ...

Design notes:
- optimize_one() is the unit of work — easy to unit test with a single
  file, and easy to parallelize later (e.g. ThreadPoolExecutor/
  ProcessPoolExecutor) without rewriting logic.
- All Pillow-specific quirks (EXIF orientation, ICC profiles, CMYK,
  alpha handling) are isolated here so scanner/report stay format-agnostic.
- Never overwrites the source file — always writes to config.output_folder.
"""

from pathlib import Path
from typing import Callable, Optional, List

from app.core.models import ImageInfo, OptimizationResult
from app.config import AppConfig


class Optimizer:
    def __init__(self, config: AppConfig, logger=None):
        self.config = config
        self.logger = logger

    def optimize_one(self, image: ImageInfo) -> OptimizationResult:
        raise NotImplementedError

    def optimize_batch(
        self,
        images: List[ImageInfo],
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[OptimizationResult]:
        raise NotImplementedError
