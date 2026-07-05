"""
app/gui/dialogs.py
====================
Modal dialogs used across the app: error dialogs (with expandable
technical details), the Settings screen, and the About box. Keeping
these in one place gives the app a consistent "commercial software"
feel instead of ad-hoc tkinter.messagebox calls scattered everywhere.
"""

import customtkinter as ctk
import webbrowser
from tkinter import filedialog

from app.gui import theme
from app.config import APP_NAME, APP_VERSION


class ErrorDialog(ctk.CTkToplevel):
    """A professional error dialog with an expandable 'Show details'
    section for the stack trace, instead of crashing to a console the
    end user will never see (since the .exe runs windowed)."""

    def __init__(self, master, title: str, message: str, details: str = ""):
        super().__init__(master)
        self.title(title)
        self.geometry("520x220")
        self.minsize(420, 180)
        self.configure(fg_color=theme.COLORS["background"])
        self.grab_set()
        self.resizable(True, True)

        icon_label = ctk.CTkLabel(
            self, text="⚠", font=("Segoe UI", 32), text_color=theme.COLORS["error"]
        )
        icon_label.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="n")

        msg_label = ctk.CTkLabel(
            self, text=message, font=theme.FONTS["body"], wraplength=380, justify="left"
        )
        msg_label.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="w")

        self.grid_columnconfigure(1, weight=1)

        self._details = details
        self._details_visible = False
        self._details_box = None

        button_row = ctk.CTkFrame(self, fg_color="transparent")
        button_row.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 10))
        button_row.grid_columnconfigure(0, weight=1)

        if details:
            self._toggle_btn = ctk.CTkButton(
                button_row, text="Show details", width=110,
                fg_color="transparent", border_width=1, command=self._toggle_details
            )
            self._toggle_btn.grid(row=0, column=1, padx=(0, 10))

        ok_btn = ctk.CTkButton(button_row, text="OK", width=90, command=self.destroy)
        ok_btn.grid(row=0, column=2)

    def _toggle_details(self):
        if self._details_visible:
            self._details_box.destroy()
            self._toggle_btn.configure(text="Show details")
            self.geometry("520x220")
        else:
            self._details_box = ctk.CTkTextbox(
                self, height=140, font=theme.FONTS["monospace"], wrap="word"
            )
            self._details_box.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=20, pady=(0, 15))
            self._details_box.insert("1.0", self._details)
            self._details_box.configure(state="disabled")
            self._toggle_btn.configure(text="Hide details")
            self.geometry("520x380")
        self._details_visible = not self._details_visible


def show_error(master, title: str, message: str, details: str = ""):
    ErrorDialog(master, title, message, details)


class SettingsDialog(ctk.CTkToplevel):
    """Editable settings screen bound to AppConfig. Changes are saved
    to disk on 'Save', so they persist across launches."""

    def __init__(self, master, config, on_save=None):
        super().__init__(master)
        self.config = config
        self.on_save = on_save
        self.title("Settings")
        self.geometry("460x520")
        self.configure(fg_color=theme.COLORS["background"])
        self.grab_set()
        self.resizable(False, False)

        pad = {"padx": 24, "pady": (14, 4)}

        ctk.CTkLabel(self, text="Processing Settings", font=theme.FONTS["heading"]).pack(
            anchor="w", padx=24, pady=(20, 10)
        )

        # Max width
        ctk.CTkLabel(self, text="Max image width (px)", font=theme.FONTS["body"]).pack(anchor="w", **pad)
        self.max_width_var = ctk.StringVar(value=str(config.max_width))
        ctk.CTkEntry(self, textvariable=self.max_width_var).pack(fill="x", padx=24)

        # JPG quality
        ctk.CTkLabel(self, text=f"JPG quality: {config.jpg_quality}", font=theme.FONTS["body"]).pack(
            anchor="w", **pad
        )
        self.jpg_quality_var = ctk.IntVar(value=config.jpg_quality)
        jpg_slider = ctk.CTkSlider(self, from_=40, to=100, variable=self.jpg_quality_var,
                                    command=lambda v: self._update_label(jpg_label, "JPG quality", v))
        jpg_slider.pack(fill="x", padx=24)
        jpg_label = ctk.CTkLabel(self, text="", font=theme.FONTS["small"], text_color=theme.COLORS["text_secondary"])
        jpg_label.pack(anchor="w", padx=24)

        # WebP quality
        ctk.CTkLabel(self, text=f"WebP quality: {config.webp_quality}", font=theme.FONTS["body"]).pack(
            anchor="w", **pad
        )
        self.webp_quality_var = ctk.IntVar(value=config.webp_quality)
        webp_slider = ctk.CTkSlider(self, from_=40, to=100, variable=self.webp_quality_var,
                                     command=lambda v: self._update_label(webp_label, "WebP quality", v))
        webp_slider.pack(fill="x", padx=24)
        webp_label = ctk.CTkLabel(self, text="", font=theme.FONTS["small"], text_color=theme.COLORS["text_secondary"])
        webp_label.pack(anchor="w", padx=24)

        # Large image threshold
        ctk.CTkLabel(self, text="Large image threshold (MB)", font=theme.FONTS["body"]).pack(anchor="w", **pad)
        self.threshold_var = ctk.StringVar(value=str(config.large_image_threshold_mb))
        ctk.CTkEntry(self, textvariable=self.threshold_var).pack(fill="x", padx=24)

        # Toggles
        self.convert_webp_var = ctk.BooleanVar(value=config.convert_to_webp)
        ctk.CTkSwitch(self, text="Convert JPG/PNG to WebP", variable=self.convert_webp_var).pack(
            anchor="w", padx=24, pady=(16, 4)
        )

        self.preserve_alpha_var = ctk.BooleanVar(value=config.preserve_transparent_png)
        ctk.CTkSwitch(self, text="Preserve transparent PNGs", variable=self.preserve_alpha_var).pack(
            anchor="w", padx=24, pady=4
        )

        # Buttons
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=(24, 20), side="bottom")
        ctk.CTkButton(btn_row, text="Cancel", fg_color="transparent", border_width=1,
                      command=self.destroy).pack(side="right", padx=(10, 0))
        ctk.CTkButton(btn_row, text="Save", command=self._save).pack(side="right")

    def _update_label(self, label_widget, name, value):
        label_widget.configure(text=f"{name}: {int(float(value))}")

    def _save(self):
        try:
            self.config.max_width = max(100, int(self.max_width_var.get()))
            self.config.large_image_threshold_mb = max(0.1, float(self.threshold_var.get()))
        except ValueError:
            show_error(self, "Invalid Setting", "Max width and threshold must be numeric values.")
            return

        self.config.jpg_quality = int(self.jpg_quality_var.get())
        self.config.webp_quality = int(self.webp_quality_var.get())
        self.config.convert_to_webp = bool(self.convert_webp_var.get())
        self.config.preserve_transparent_png = bool(self.preserve_alpha_var.get())
        self.config.save()

        if self.on_save:
            self.on_save(self.config)
        self.destroy()


class AboutDialog(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("About")
        self.geometry("380x260")
        self.configure(fg_color=theme.COLORS["background"])
        self.grab_set()
        self.resizable(False, False)

        ctk.CTkLabel(self, text=APP_NAME.replace("_", " "), font=theme.FONTS["heading"]).pack(pady=(30, 6))
        ctk.CTkLabel(self, text=f"Version {APP_VERSION}", font=theme.FONTS["body"],
                     text_color=theme.COLORS["text_secondary"]).pack()
        ctk.CTkLabel(
            self,
            text="Internal image auditing & optimization tool.\nBuilt for agency production workflows.",
            font=theme.FONTS["body"], justify="center"
        ).pack(pady=20)
        ctk.CTkButton(self, text="Close", command=self.destroy).pack(pady=10)


def ask_directory(title: str = "Select Folder") -> str:
    return filedialog.askdirectory(title=title)
