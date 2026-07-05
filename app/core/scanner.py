"""
app/core/scanner.py
====================
STEP 2 + 3 of the workflow: recursively scan a folder, classify every
image (supported format / unsupported / large), and compute a content
hash used later for duplicate detection.
"""

from pathlib import Path
from typing import Callable, Optional, List

from PIL import Image, UnidentifiedImageError

from app.core.models import ImageInfo
from app.config import AppConfig
from app.utils import file_utils, hash_utils


class Scanner:
    def __init__(self, config: AppConfig, logger=None):
        self.config = config
        self.logger = logger

    def scan(
        self,
        folder: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[ImageInfo]:
        all_files = [
            p for p in file_utils.iter_files_recursive(folder)
            if file_utils.looks_like_image_file(p)
        ]
        total = len(all_files)
        results: List[ImageInfo] = []
        threshold_bytes = self.config.large_image_threshold_mb * 1024 * 1024

        for i, path in enumerate(all_files, start=1):
            size_bytes = file_utils.get_file_size(path)
            ext = path.suffix.lower()
            width, height = 0, 0
            status = "pending"

            if not file_utils.is_supported_extension(path, self.config.supported_formats):
                status = "unsupported"
                if self.logger:
                    self.logger.warning(f"Unsupported format skipped: {path.name}")
            else:
                try:
                    with Image.open(path) as img:
                        width, height = img.size
                except (UnidentifiedImageError, OSError) as e:
                    status = "unsupported"
                    if self.logger:
                        self.logger.warning(f"Could not read image {path.name}: {e}")

            file_hash = ""
            if status != "unsupported":
                file_hash = hash_utils.file_sha256(path)

            info = ImageInfo(
                path=path,
                filename=path.name,
                extension=ext,
                size_bytes=size_bytes,
                width=width,
                height=height,
                file_hash=file_hash,
                is_large=size_bytes > threshold_bytes,
                is_duplicate=False,
                status=status,
            )
            results.append(info)

            if progress_callback:
                progress_callback(i, total)

        if self.logger:
            self.logger.info(f"Scan complete: {total} image file(s) found under {folder}")
        return results
