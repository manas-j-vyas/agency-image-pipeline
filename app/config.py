"""
app/config.py
=============
Centralized, single-source-of-truth configuration.

Responsibility:
- Holds default settings (max width, quality %, output format, thresholds
  for "large image", supported extensions, output folder path, etc.)
- Holds paths (assets, output, logs).
- Provides a single AppConfig object/dataclass that GUI + core modules
  read from and write to (e.g. when the user changes a setting in the GUI).
- No logic beyond simple validation/defaults — this is a data holder,
  not a processing module.

Why it matters:
Every module (scanner, optimizer, report_generator) should pull settings
from here instead of hardcoding values. This is what makes "max width"
or "quality" configurable from the GUI without touching core logic.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AppConfig:
    max_width: int = 1920
    jpg_quality: int = 82
    webp_quality: int = 80
    large_image_threshold_mb: float = 2.0
    convert_to_webp: bool = True
    preserve_transparent_png: bool = True
    supported_formats: tuple = (".jpg", ".jpeg", ".png", ".webp")
    output_folder_name: str = "optimized_output"
    source_folder: Path = None
    output_folder: Path = None
