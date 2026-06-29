import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox


class GenerationCompleteDialog(tk.Toplevel):
    def __init__(self, parent, report_path: str):
        super().__init__(parent)
        self.report_path = report_path
        self.title("Report generated")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._center_on_screen()
        self.protocol("WM_DELETE_WINDOW", self._close)

        self.bind("<Return>", lambda event: self._close())
        self.bind("<Escape>", lambda event: self._close())

        self.wait_window(self)

    def _build_ui(self):
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="The report was generated successfully.",
            font=("Arial", 11, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        ttk.Label(
            frame,
            text=f"Location:\n{self.report_path}",
            wraplength=440,
            justify="left",
        ).pack(anchor="w", pady=(0, 16))

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x")

        ttk.Button(buttons, text="Open folder", command=self._open_folder).pack(side="left")
        ttk.Button(buttons, text="Open file", command=self._open_file).pack(side="left", padx=8)
        ttk.Button(buttons, text="OK", command=self._close).pack(side="right")

    def _open_path(self, path: str):
        if not path or not os.path.exists(path):
            messagebox.showwarning("Open path", "The requested path does not exist.")
            return

        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def _open_folder(self):
        self._open_path(os.path.dirname(self.report_path))

    def _open_file(self):
        self._open_path(self.report_path)

    def _close(self):
        self.destroy()

    def _center_on_screen(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 2, 0)
        self.geometry(f"{width}x{height}+{x}+{y}")
