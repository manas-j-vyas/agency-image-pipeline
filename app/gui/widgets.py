"""
app/gui/widgets.py
===================
Reusable composed CustomTkinter widgets, kept separate from
main_window.py so that file stays a clean layout/controller.
"""

import customtkinter as ctk
from app.gui import theme


class StatCard(ctk.CTkFrame):
    """Small rounded card used in the report summary panel,
    e.g. 'Total Images: 342'."""

    def __init__(self, master, title: str, value: str = "-", **kwargs):
        super().__init__(master, fg_color=theme.COLORS["surface"], corner_radius=10, **kwargs)
        self.title_label = ctk.CTkLabel(
            self, text=title, font=theme.FONTS["small"], text_color=theme.COLORS["text_secondary"]
        )
        self.title_label.pack(anchor="w", padx=16, pady=(12, 0))
        self.value_label = ctk.CTkLabel(self, text=value, font=("Segoe UI", 22, "bold"))
        self.value_label.pack(anchor="w", padx=16, pady=(0, 12))

    def set_value(self, value: str):
        self.value_label.configure(text=value)


class LogConsole(ctk.CTkTextbox):
    """Scrollable, read-only, color-tagged log console."""

    def __init__(self, master, **kwargs):
        super().__init__(master, font=theme.FONTS["monospace"], wrap="word", **kwargs)
        self.configure(state="disabled")

        # CTkTextbox proxies most tkinter.Text methods, but to stay safe
        # across customtkinter versions we fall back to the internal
        # tkinter Text widget for tag configuration if needed.
        self._tag_target = self if hasattr(self, "tag_config") else getattr(self, "_textbox", self)

        colors = {
            "INFO": theme.COLORS["text_primary"],
            "WARNING": theme.COLORS["warning"],
            "ERROR": theme.COLORS["error"],
            "DEBUG": theme.COLORS["text_secondary"],
        }
        for tag, color in colors.items():
            try:
                self._tag_target.tag_config(tag, foreground=color)
            except Exception:
                pass  # Worst case: log still works, just without color coding.

    def append(self, level: str, message: str):
        self.configure(state="normal")
        try:
            self.insert("end", f"[{level}] {message}\n", level)
        except Exception:
            # Fallback if this CTk version doesn't accept a tag arg to insert().
            self.insert("end", f"[{level}] {message}\n")
        self.see("end")
        self.configure(state="disabled")

    def clear(self):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")


class FolderPicker(ctk.CTkFrame):
    """Label + text field + Browse button, wired to a callback."""

    def __init__(self, master, label: str, on_select=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_select = on_select

        ctk.CTkLabel(self, text=label, font=theme.FONTS["body"]).grid(
            row=0, column=0, sticky="w", pady=(0, 4)
        )

        self.path_var = ctk.StringVar(value="")
        self.entry = ctk.CTkEntry(self, textvariable=self.path_var, placeholder_text="No folder selected")
        self.entry.grid(row=1, column=0, sticky="ew", padx=(0, 8))

        self.browse_btn = ctk.CTkButton(self, text="Browse…", width=100, command=self._browse)
        self.browse_btn.grid(row=1, column=1)

        self.grid_columnconfigure(0, weight=1)

    def _browse(self):
        from app.gui.dialogs import ask_directory
        path = ask_directory()
        if path:
            self.path_var.set(path)
            if self.on_select:
                self.on_select(path)

    def get(self) -> str:
        return self.path_var.get()

    def set(self, path: str):
        self.path_var.set(path)
