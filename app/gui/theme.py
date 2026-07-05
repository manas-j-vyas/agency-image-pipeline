"""
app/gui/theme.py
=================
Responsibility: Single place defining the dark theme + brand colors,
so the whole app has a consistent professional look instead of
scattered color codes across widgets.

Contents (to be implemented):
- apply_dark_theme(): sets customtkinter.set_appearance_mode("dark")
  and set_default_color_theme(...)
- COLORS dict: background, surface, accent, success, warning, error,
  text_primary, text_secondary — used by widgets.py and main_window.py
- FONTS dict: heading, body, monospace (for the log console)
"""

import customtkinter as ctk

COLORS = {
    "background": "#1a1a1a",
    "surface": "#242424",
    "accent": "#3b82f6",
    "success": "#22c55e",
    "warning": "#eab308",
    "error": "#ef4444",
    "text_primary": "#f5f5f5",
    "text_secondary": "#a3a3a3",
}

FONTS = {
    "heading": ("Segoe UI", 20, "bold"),
    "body": ("Segoe UI", 13),
    "monospace": ("Consolas", 12),
}


def apply_dark_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
