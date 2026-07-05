"""
app/utils/file_utils.py
========================
Small, reusable filesystem helpers used across core modules.
"""

from pathlib import Path
from typing import Iterator, Tuple


def iter_files_recursive(folder: Path) -> Iterator[Path]:
    """Yields every file (not directory) under folder, recursively."""
    for path in folder.rglob("*"):
        if path.is_file():
            yield path


def get_file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def human_readable_size(num_bytes: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:,.1f} {unit}" if unit != "B" else f"{int(num_bytes)} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:,.1f} PB"


def ensure_output_subfolder(source_root: Path, output_root: Path, file_path: Path) -> Path:
    """
    Mirrors the file's location relative to source_root into output_root,
    creating any needed subfolders, and returns the target directory
    (NOT including the filename).
    """
    try:
        relative = file_path.parent.relative_to(source_root)
    except ValueError:
        relative = Path(".")
    target_dir = output_root / relative
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def is_supported_extension(path: Path, supported: Tuple[str, ...]) -> bool:
    return path.suffix.lower() in supported


KNOWN_IMAGE_EXTENSIONS = (
    ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".tif",
    ".heic", ".heif", ".svg", ".ico", ".avif",
)


def looks_like_image_file(path: Path) -> bool:
    """Broader check than is_supported_extension — used to flag files
    that ARE images but are in an unsupported format (vs. non-image
    files, which are ignored entirely)."""
    return path.suffix.lower() in KNOWN_IMAGE_EXTENSIONS
