"""
app/gui/theme.py
=================
Single source of truth for the dark theme + brand colors/fonts, so the
whole app has a consistent, professional look.
"""

import customtkinter as ctk

COLORS = {
    "background": "#1a1a1a",
    "surface": "#232323",
    "surface_alt": "#2b2b2b",
    "border": "#3a3a3a",
    "accent": "#3b82f6",
    "accent_hover": "#2563eb",
    "success": "#22c55e",
    "warning": "#eab308",
    "error": "#ef4444",
    "text_primary": "#f5f5f5",
    "text_secondary": "#a3a3a3",
}

FONTS = {
    "heading": ("Segoe UI", 20, "bold"),
    "subheading": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 13),
    "small": ("Segoe UI", 11),
    "monospace": ("Consolas", 12),
}


def apply_dark_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
