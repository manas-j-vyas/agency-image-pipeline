"""
main.py
========
Application entry point.

Responsibilities:
- Sets up a global exception hook so that ANY uncaught error shows a
  proper dialog instead of silently vanishing (critical for a
  windowed .exe with no visible console).
- Initializes config + logger.
- Launches MainWindow.

Contains NO business logic — everything else lives in app/core and app/gui.
"""

import sys
import traceback

from app.config import AppConfig, get_logs_dir


def _install_global_exception_hook():
    """Catches any exception that isn't already handled somewhere else
    (e.g. an error during GUI construction itself) and shows a dialog
    instead of the app just disappearing, which is what happens by
    default in a windowed PyInstaller build."""

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        details = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

        try:
            log_file = get_logs_dir() / "crash.log"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(details + "\n" + ("-" * 60) + "\n")
        except OSError:
            pass

        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Agency Image Pipeline - Unexpected Error",
                f"An unexpected error occurred and the application must close.\n\n{exc_value}\n\n"
                f"Details were saved to:\n{get_logs_dir() / 'crash.log'}",
            )
            root.destroy()
        except Exception:
            pass  # last resort: nothing else we can safely do

    sys.excepthook = handle_exception


def main():
    _install_global_exception_hook()

    config = AppConfig.load()

    from app.gui.main_window import MainWindow
    app = MainWindow(config)
    app.mainloop()


if __name__ == "__main__":
    main()
