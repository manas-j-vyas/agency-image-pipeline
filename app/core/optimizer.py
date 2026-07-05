"""
app/core/optimizer.py
======================
STEP 4 of the workflow: resize, compress, and optionally convert each
image to WebP, writing results into the output folder while mirroring
the original subfolder structure.
"""

from pathlib import Path
from typing import Callable, Optional, List

from PIL import Image

from app.core.models import ImageInfo, OptimizationResult
from app.config import AppConfig
from app.utils import file_utils


class Optimizer:
    def __init__(self, config: AppConfig, logger=None):
        self.config = config
        self.logger = logger

    def optimize_one(self, image: ImageInfo, source_root: Path, output_root: Path) -> OptimizationResult:
        original_size = image.size_bytes
        try:
            with Image.open(image.path) as img:
                img = self._apply_exif_orientation(img)
                has_alpha = img.mode in ("RGBA", "LA") or (
                    img.mode == "P" and "transparency" in img.info
                )

                # Resize (maintain aspect ratio) if wider than max_width.
                if img.width > self.config.max_width:
                    ratio = self.config.max_width / float(img.width)
                    new_size = (self.config.max_width, max(1, int(img.height * ratio)))
                    img = img.resize(new_size, Image.LANCZOS)

                target_dir = file_utils.ensure_output_subfolder(source_root, output_root, image.path)

                convert_to_webp = self.config.convert_to_webp
                keep_alpha = has_alpha and self.config.preserve_transparent_png

                if convert_to_webp:
                    out_path = target_dir / (image.path.stem + ".webp")
                    save_img = img.convert("RGBA") if keep_alpha else img.convert("RGB")
                    save_img.save(out_path, "WEBP", quality=self.config.webp_quality, method=6)
                elif image.extension in (".jpg", ".jpeg"):
                    out_path = target_dir / image.path.name
                    save_img = img.convert("RGB")
                    save_img.save(out_path, "JPEG", quality=self.config.jpg_quality, optimize=True)
                elif image.extension == ".png":
                    out_path = target_dir / image.path.name
                    save_img = img if keep_alpha else img.convert("RGB")
                    save_img.save(out_path, "PNG", optimize=True)
                else:
                    # Already webp or other supported type -> re-save as-is.
                    out_path = target_dir / image.path.name
                    img.save(out_path)

            optimized_size = file_utils.get_file_size(out_path)
            saved_bytes = max(0, original_size - optimized_size)
            saved_percent = (saved_bytes / original_size * 100) if original_size else 0.0

            if self.logger:
                self.logger.info(
                    f"Optimized {image.filename}: "
                    f"{file_utils.human_readable_size(original_size)} -> "
                    f"{file_utils.human_readable_size(optimized_size)} "
                    f"({saved_percent:.1f}% saved)"
                )

            return OptimizationResult(
                source=image,
                output_path=out_path,
                original_size_bytes=original_size,
                optimized_size_bytes=optimized_size,
                saved_bytes=saved_bytes,
                saved_percent=saved_percent,
                success=True,
            )

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to optimize {image.filename}: {e}")
            return OptimizationResult(
                source=image,
                original_size_bytes=original_size,
                success=False,
                error_message=str(e),
            )

    def optimize_batch(
        self,
        images: List[ImageInfo],
        source_root: Path,
        output_root: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[OptimizationResult]:
        results = []
        total = len(images)
        output_root.mkdir(parents=True, exist_ok=True)
        for i, image in enumerate(images, start=1):
            results.append(self.optimize_one(image, source_root, output_root))
            if progress_callback:
                progress_callback(i, total)
        return results

    @staticmethod
    def _apply_exif_orientation(img: Image.Image) -> Image.Image:
        try:
            from PIL import ImageOps
            return ImageOps.exif_transpose(img)
        except Exception:
            return img
