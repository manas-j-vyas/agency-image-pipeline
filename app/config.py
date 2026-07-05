"""
app/config.py
=============
Centralized application configuration + persistence.

Settings are saved to a JSON file in the user's OS-standard app-data
folder (NOT next to the .exe, since a double-click-installed program
should never require write access to Program Files):

    Windows: %APPDATA%/AgencyImagePipeline/settings.json
    macOS/Linux (dev use): ~/.agency_image_pipeline/settings.json

This is what lets a non-technical user's preferences (max width,
quality, last used folder, etc.) persist between launches with no
manual file editing.
"""

import json
import os
from dataclasses import dataclass, asdict, field
from pathlib import Path

APP_NAME = "AgencyImagePipeline"
APP_VERSION = "1.0.0"


def get_app_data_dir() -> Path:
    """Cross-platform per-user app data directory."""
    if os.name == "nt":
        base = os.environ.get("APPDATA", str(Path.home()))
        path = Path(base) / APP_NAME
    else:
        path = Path.home() / f".{APP_NAME.lower()}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_logs_dir() -> Path:
    path = get_app_data_dir() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


SETTINGS_FILE = get_app_data_dir() / "settings.json"


@dataclass
class AppConfig:
    max_width: int = 1920
    jpg_quality: int = 82
    webp_quality: int = 80
    large_image_threshold_mb: float = 2.0
    convert_to_webp: bool = True
    preserve_transparent_png: bool = True
    delete_duplicates_from_output: bool = True
    supported_formats: tuple = (".jpg", ".jpeg", ".png", ".webp")
    output_folder_name: str = "optimized_output"
    last_source_folder: str = ""
    last_output_folder: str = ""
    window_w: int = 1180
    window_h: int = 760

    # --- persistence -----------------------------------------------------

    def save(self):
        data = asdict(self)
        data.pop("supported_formats", None)  # not user-editable
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError:
            # Non-fatal: app still works this session, just won't persist.
            pass

    @classmethod
    def load(cls) -> "AppConfig":
        config = cls()
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for key, value in data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
            except (OSError, json.JSONDecodeError):
                # Corrupted settings file -> fall back to defaults silently.
                pass
        return config

    def resolve_output_folder(self, source_folder: Path) -> Path:
        if self.last_output_folder:
            candidate = Path(self.last_output_folder)
            if candidate.is_absolute():
                return candidate
        return source_folder / self.output_folder_name
