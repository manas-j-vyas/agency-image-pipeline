"""
main.py
========
Application entry point.

Responsibility:
- Bootstraps the CustomTkinter application.
- Initializes global config/theme.
- Launches MainWindow (app/gui/main_window.py).
- Contains NO business logic — this file only wires things together.

This keeps the entry point tiny and testable; all real logic lives in
app/core and app/gui.
"""

from app.gui.main_window import MainWindow
from app.config import AppConfig


def main():
    config = AppConfig()
    app = MainWindow(config)
    app.mainloop()


if __name__ == "__main__":
    main()
