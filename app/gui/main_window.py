"""
app/gui/main_window.py
=======================
Main CustomTkinter application window — the GUI controller. Contains
NO image-processing logic; it only wires user actions to
app/core/worker.PipelineWorker and renders results.
"""

import os
import subprocess
import sys
import webbrowser
from pathlib import Path

import customtkinter as ctk

from app.config import AppConfig, get_logs_dir, APP_NAME
from app.gui import theme, dialogs
from app.gui.widgets import StatCard, LogConsole, FolderPicker
from app.core.worker import PipelineWorker
from app.core.models import ReportData
from app.reports.html_report import export_html
from app.reports.json_report import export_json
from app.utils.file_utils import human_readable_size
from app.utils.logger import PipelineLogger


class MainWindow(ctk.CTk):
    def __init__(self, config: AppConfig):
        super().__init__()
        self.config = config
        self.worker = None
        self.last_report: ReportData = None
        self.output_folder: Path = None

        theme.apply_dark_theme()
        self.title(f"{APP_NAME.replace('_', ' ')}")
        self.geometry(f"{config.window_w}x{config.window_h}")
        self.minsize(980, 640)
        self.configure(fg_color=theme.COLORS["background"])

        log_file = get_logs_dir() / "pipeline.log"
        self.logger = PipelineLogger(log_file, ui_callback=self._on_log_from_worker_thread)

        self._build_menu()
        self._build_layout()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_menu(self):
        import tkinter as tk
        menu_bar = tk.Menu(self)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Settings…", command=self._open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Open Logs Folder", command=self._open_logs_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        menu_bar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=lambda: dialogs.AboutDialog(self))
        menu_bar.add_cascade(label="Help", menu=help_menu)

        try:
            self.configure(menu=menu_bar)
        except Exception:
            # CTk is a subclass of tkinter.Tk, so this should always work,
            # but fall back to the native tk call just in case.
            self.tk.call(self._w, "configure", "-menu", menu_bar)

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Header -------------------------------------------------
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="Agency Image Pipeline", font=theme.FONTS["heading"]).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkButton(
            header, text="⚙ Settings", width=110, fg_color="transparent", border_width=1,
            command=self._open_settings
        ).grid(row=0, column=1, sticky="e")

        # --- Folder selection ----------------------------------------
        folder_row = ctk.CTkFrame(self, fg_color=theme.COLORS["surface"], corner_radius=10)
        folder_row.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 14))
        folder_row.grid_columnconfigure(0, weight=1)
        folder_row.grid_columnconfigure(1, weight=1)

        self.source_picker = FolderPicker(folder_row, "Project image folder", on_select=self._on_source_selected)
        self.source_picker.grid(row=0, column=0, sticky="ew", padx=(16, 8), pady=16)
        if self.config.last_source_folder:
            self.source_picker.set(self.config.last_source_folder)

        self.output_picker = FolderPicker(folder_row, "Output folder (optional)")
        self.output_picker.grid(row=0, column=1, sticky="ew", padx=(8, 16), pady=16)
        if self.config.last_output_folder:
            self.output_picker.set(self.config.last_output_folder)

        # --- Main content: log console + report panel ----------------
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 10))
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        log_frame = ctk.CTkFrame(content, fg_color=theme.COLORS["surface"], corner_radius=10)
        log_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(log_frame, text="Live Processing Log", font=theme.FONTS["subheading"]).grid(
            row=0, column=0, sticky="w", padx=16, pady=(14, 6)
        )
        self.log_console = LogConsole(log_frame)
        self.log_console.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))

        report_frame = ctk.CTkFrame(content, fg_color=theme.COLORS["surface"], corner_radius=10)
        report_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        report_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(report_frame, text="Report Summary", font=theme.FONTS["subheading"]).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(14, 10)
        )

        self.stat_total = StatCard(report_frame, "Total Images")
        self.stat_total.grid(row=1, column=0, sticky="ew", padx=(16, 8), pady=6)
        self.stat_saved = StatCard(report_frame, "Space Saved")
        self.stat_saved.grid(row=1, column=1, sticky="ew", padx=(8, 16), pady=6)
        self.stat_original = StatCard(report_frame, "Original Size")
        self.stat_original.grid(row=2, column=0, sticky="ew", padx=(16, 8), pady=6)
        self.stat_optimized = StatCard(report_frame, "Optimized Size")
        self.stat_optimized.grid(row=2, column=1, sticky="ew", padx=(8, 16), pady=6)
        self.stat_duplicates = StatCard(report_frame, "Duplicate Groups")
        self.stat_duplicates.grid(row=3, column=0, sticky="ew", padx=(16, 8), pady=6)
        self.stat_skipped = StatCard(report_frame, "Skipped / Unsupported")
        self.stat_skipped.grid(row=3, column=1, sticky="ew", padx=(8, 16), pady=6)

        self.open_output_btn = ctk.CTkButton(
            report_frame, text="Open Output Folder", command=self._open_output_folder, state="disabled"
        )
        self.open_output_btn.grid(row=4, column=0, columnspan=2, sticky="ew", padx=16, pady=(14, 6))

        self.export_report_btn = ctk.CTkButton(
            report_frame, text="Export Report (HTML)", fg_color="transparent", border_width=1,
            command=self._export_report, state="disabled"
        )
        self.export_report_btn.grid(row=5, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 16))

        # --- Footer: progress + start/cancel --------------------------
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 20))
        footer.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(footer, text="Ready.", font=theme.FONTS["small"],
                                          text_color=theme.COLORS["text_secondary"])
        self.status_label.grid(row=0, column=0, sticky="w")

        self.progress_bar = ctk.CTkProgressBar(footer)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(6, 10))

        btn_row = ctk.CTkFrame(footer, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="e")
        self.cancel_btn = ctk.CTkButton(
            btn_row, text="Cancel", fg_color="transparent", border_width=1,
            command=self._on_cancel_clicked, state="disabled"
        )
        self.cancel_btn.grid(row=0, column=0, padx=(0, 10))
        self.start_btn = ctk.CTkButton(
            btn_row, text="Start Processing", width=160, command=self._on_start_clicked
        )
        self.start_btn.grid(row=0, column=1)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _on_source_selected(self, path: str):
        if not self.output_picker.get():
            self.output_picker.set(str(Path(path) / self.config.output_folder_name))

    def _open_settings(self):
        dialogs.SettingsDialog(self, self.config, on_save=lambda cfg: self.logger.info("Settings updated."))

    def _on_start_clicked(self):
        source = self.source_picker.get().strip()
        if not source:
            dialogs.show_error(self, "No Folder Selected", "Please select a project image folder first.")
            return
        source_path = Path(source)
        if not source_path.exists() or not source_path.is_dir():
            dialogs.show_error(self, "Invalid Folder", f"The selected folder does not exist:\n{source}")
            return

        output = self.output_picker.get().strip() or str(source_path / self.config.output_folder_name)
        output_path = Path(output)

        self.config.last_source_folder = str(source_path)
        self.config.last_output_folder = str(output_path)
        self.config.save()

        self.output_folder = output_path
        self.log_console.clear()
        self._reset_stat_cards()
        self.open_output_btn.configure(state="disabled")
        self.export_report_btn.configure(state="disabled")
        self.start_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.progress_bar.set(0)
        self.status_label.configure(text="Starting…")

        self.worker = PipelineWorker(
            config=self.config,
            source_folder=source_path,
            output_folder=output_path,
            logger=self.logger,
            on_progress=self._on_progress_from_worker_thread,
            on_complete=self._on_complete_from_worker_thread,
            on_error=self._on_error_from_worker_thread,
        )
        self.worker.start()

    def _on_cancel_clicked(self):
        if self.worker:
            self.worker.cancel()
            self.status_label.configure(text="Cancelling…")
            self.cancel_btn.configure(state="disabled")

    def _open_output_folder(self):
        if not self.output_folder or not self.output_folder.exists():
            return
        if sys.platform == "win32":
            os.startfile(str(self.output_folder))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(self.output_folder)])
        else:
            subprocess.Popen(["xdg-open", str(self.output_folder)])

    def _open_logs_folder(self):
        logs_dir = get_logs_dir()
        if sys.platform == "win32":
            os.startfile(str(logs_dir))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(logs_dir)])
        else:
            subprocess.Popen(["xdg-open", str(logs_dir)])

    def _export_report(self):
        if not self.last_report:
            return
        try:
            html_path = self.output_folder / "report.html"
            json_path = self.output_folder / "report.json"
            export_html(self.last_report, html_path)
            export_json(self.last_report, json_path)
            self.logger.info(f"Report exported to {html_path}")
            webbrowser.open(str(html_path))
        except Exception as e:
            dialogs.show_error(self, "Export Failed", "Could not export the report.", details=str(e))

    def _on_close(self):
        if self.worker and self.worker.is_alive():
            self.worker.cancel()
        self.destroy()

    # ------------------------------------------------------------------
    # Callbacks from worker thread -> marshalled onto the GUI thread
    # ------------------------------------------------------------------

    def _on_log_from_worker_thread(self, level: str, message: str):
        self.after(0, lambda: self.log_console.append(level, message))

    def _on_progress_from_worker_thread(self, stage: str, current: int, total: int):
        def update():
            fraction = (current / total) if total else 0
            self.progress_bar.set(fraction)
            self.status_label.configure(text=f"{stage}… ({current}/{total})")
        self.after(0, update)

    def _on_complete_from_worker_thread(self, report: ReportData):
        self.after(0, lambda: self._render_report(report))

    def _on_error_from_worker_thread(self, message: str, details: str):
        def show():
            self.start_btn.configure(state="normal")
            self.cancel_btn.configure(state="disabled")
            self.status_label.configure(text="Failed.")
            dialogs.show_error(
                self, "Processing Failed",
                f"Something went wrong while processing images:\n{message}",
                details=details,
            )
        self.after(0, show)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _reset_stat_cards(self):
        for card in (self.stat_total, self.stat_saved, self.stat_original,
                     self.stat_optimized, self.stat_duplicates, self.stat_skipped):
            card.set_value("-")

    def _render_report(self, report: ReportData):
        self.last_report = report
        self.progress_bar.set(1.0)
        self.status_label.configure(text="Done.")
        self.start_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.open_output_btn.configure(state="normal")
        self.export_report_btn.configure(state="normal")

        self.stat_total.set_value(str(report.total_images))
        self.stat_saved.set_value(human_readable_size(report.total_saved))
        self.stat_original.set_value(human_readable_size(report.total_original_size))
        self.stat_optimized.set_value(human_readable_size(report.total_optimized_size))
        self.stat_duplicates.set_value(str(len(report.duplicate_groups)))
        self.stat_skipped.set_value(str(len(report.skipped_images)))
