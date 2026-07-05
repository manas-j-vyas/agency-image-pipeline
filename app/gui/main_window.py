"""
app/gui/main_window.py
=======================
Responsibility: The main CustomTkinter application window. This is the
"controller" of the GUI — it owns the layout and wires user actions to
the PipelineWorker, but contains NO image-processing logic itself.

Layout (planned):
- Top bar: folder picker ("Select Project Folder") + Start/Cancel buttons
- Left/Center: settings panel (max width, quality, convert-to-webp
  toggle, preserve-transparency toggle) — bound to AppConfig
- Progress bar (CTkProgressBar) reflecting worker's on_progress callback
- Live log console (scrollable CTkTextbox) reflecting worker's on_log callback
- Bottom: summary report panel populated on_complete (total images,
  space saved, duplicates found, etc.) — see widgets.py for the
  reusable stat-card component

Public API:

    class MainWindow(customtkinter.CTk):
        def __init__(self, config: AppConfig): ...
        def _on_select_folder(self): ...
        def _on_start_clicked(self): ...
        def _handle_progress(self, current, total, message): ...
        def _handle_log(self, message): ...
        def _handle_complete(self, report_data): ...

Design notes:
- Applies dark theme from gui/theme.py at startup.
- Never calls app/core modules directly — always goes through
  app/core/worker.PipelineWorker so processing runs off-thread.
- Uses `self.after(0, ...)` to safely marshal worker callbacks back
  onto the Tkinter main thread.
"""

import customtkinter as ctk

from app.config import AppConfig
from app.gui import theme


class MainWindow(ctk.CTk):
    def __init__(self, config: AppConfig):
        super().__init__()
        self.config = config
        theme.apply_dark_theme()
        self.title("Agency Image Pipeline")
        self.geometry("1100x720")
        self._build_layout()

    def _build_layout(self):
        raise NotImplementedError

    def _on_select_folder(self):
        raise NotImplementedError

    def _on_start_clicked(self):
        raise NotImplementedError

    def _handle_progress(self, current: int, total: int, message: str):
        raise NotImplementedError

    def _handle_log(self, message: str):
        raise NotImplementedError

    def _handle_complete(self, report_data):
        raise NotImplementedError
