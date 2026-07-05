"""
app/gui/widgets.py
===================
Responsibility: Reusable, composed CustomTkinter widgets so
main_window.py stays a clean layout/controller file instead of a
1000-line wall of widget code.

Planned components:

- StatCard(parent, title: str, value: str, icon=None)
      Small rounded card used in the report summary panel
      (e.g. "Total Images: 342", "Space Saved: 128 MB").

- LogConsole(parent)
      Scrollable, monospace, read-only CTkTextbox with an `append(msg)`
      method and auto-scroll — used for "live processing logs".

- SettingsPanel(parent, config: AppConfig, on_change: Callable)
      Groups the max-width slider, quality slider, and format toggles
      (WebP conversion, preserve transparency) into one component bound
      to AppConfig, so main_window.py doesn't manage individual sliders.

- FolderPicker(parent, label: str, on_select: Callable[[Path], None])
      Text field + "Browse" button wrapper around
      tkinter.filedialog.askdirectory.
"""

import customtkinter as ctk


class StatCard(ctk.CTkFrame):
    def __init__(self, master, title: str, value: str, **kwargs):
        super().__init__(master, **kwargs)
        raise NotImplementedError


class LogConsole(ctk.CTkTextbox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def append(self, message: str):
        raise NotImplementedError


class SettingsPanel(ctk.CTkFrame):
    def __init__(self, master, config, on_change=None, **kwargs):
        super().__init__(master, **kwargs)
        raise NotImplementedError


class FolderPicker(ctk.CTkFrame):
    def __init__(self, master, label: str, on_select=None, **kwargs):
        super().__init__(master, **kwargs)
        raise NotImplementedError
