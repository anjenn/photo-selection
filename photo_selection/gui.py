from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable

from .file_list import default_output_path, write_file_list
from .intersection import copy_photo_intersection
from .paths import clean_path, validate_folder


FILE_TYPE_LABELS = {"all": "All photos", "jpeg": "JPEG only", "raw": "RAW only"}


class ToolTab(ttk.Frame):
    """A notebook tab with path rows, a Run button, and a status line."""

    busy_message = "Working..."

    def __init__(self, parent: ttk.Notebook, idle_message: str) -> None:
        super().__init__(parent, padding=18)
        self.columnconfigure(1, weight=1)
        self.status_var = tk.StringVar(value=idle_message)

    def add_path_row(
        self,
        row: int,
        label: str,
        variable: tk.StringVar,
        button_text: str,
        command: Callable[[], None],
    ) -> None:
        ttk.Label(self, text=label).grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(self, textvariable=variable, width=56).grid(
            row=row, column=1, sticky="ew", padx=10, pady=6
        )
        ttk.Button(self, text=button_text, width=12, command=command).grid(
            row=row, column=2, sticky="e", pady=6
        )

    def add_folder_row(self, row: int, label: str, variable: tk.StringVar) -> None:
        self.add_path_row(row, label, variable, "Browse", lambda: self.choose_folder(variable))

    def add_choice_row(
        self, row: int, label: str, variable: tk.StringVar, choices: dict[str, str]
    ) -> None:
        ttk.Label(self, text=label).grid(row=row, column=0, sticky="w", pady=6)
        frame = ttk.Frame(self)
        frame.grid(row=row, column=1, sticky="w", padx=10, pady=6)
        for value, text in choices.items():
            ttk.Radiobutton(frame, text=text, variable=variable, value=value).pack(
                side="left", padx=(0, 18)
            )

    def add_run_row(self, row: int) -> None:
        ttk.Button(self, text="Run", width=16, command=self.run).grid(
            row=row, column=2, sticky="e", pady=(18, 0)
        )
        ttk.Label(self, textvariable=self.status_var).grid(
            row=row + 1, column=0, columnspan=3, sticky="ew", pady=(18, 0)
        )

    def choose_folder(self, variable: tk.StringVar) -> str:
        folder = filedialog.askdirectory()
        if folder:
            variable.set(folder)
        return folder

    def run(self) -> None:
        self.status_var.set(self.busy_message)
        self.update_idletasks()
        try:
            done_message, done_status = self.execute()
        except Exception as error:
            messagebox.showerror("Error", str(error))
            self.status_var.set("Could not finish. Check the folder paths.")
        else:
            messagebox.showinfo("Done", done_message)
            self.status_var.set(done_status)

    def execute(self) -> tuple[str, str]:
        """Do the tab's work; return (dialog message, status line)."""
        raise NotImplementedError


class MatchPhotosTab(ToolTab):
    busy_message = "Copying matching photos..."

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(
            parent, "Choose folders, then click Run. Folder C is emptied before copying."
        )
        self.folder_a_var = tk.StringVar()
        self.folder_b_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.source_var = tk.StringVar(value="B")
        self.file_type_var = tk.StringVar(value="all")

        self.add_folder_row(0, "Folder A - photos", self.folder_a_var)
        self.add_folder_row(1, "Folder B - photos", self.folder_b_var)
        self.add_folder_row(2, "Folder C - output", self.output_var)
        self.add_choice_row(
            3, "Copy matching files from", self.source_var, {"A": "Folder A", "B": "Folder B"}
        )
        self.add_choice_row(4, "File types to copy", self.file_type_var, FILE_TYPE_LABELS)
        self.add_run_row(5)

    def execute(self) -> tuple[str, str]:
        if not (self.folder_a_var.get() and self.folder_b_var.get() and self.output_var.get()):
            raise ValueError("Please choose all three folders.")

        folder_a = clean_path(self.folder_a_var.get())
        folder_b = clean_path(self.folder_b_var.get())
        output_folder = clean_path(self.output_var.get())
        source = self.source_var.get()

        validate_folder(folder_a, "Folder A")
        validate_folder(folder_b, "Folder B")

        copied = copy_photo_intersection(
            folder_a, folder_b, output_folder, source, self.file_type_var.get()
        )
        return (
            f"Copied {copied} matching photo(s) from Folder {source} to:\n{output_folder}",
            f"Done. Copied {copied} matching photo(s).",
        )


class FileListTab(ToolTab):
    busy_message = "Creating TXT file list..."

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, "Choose a folder, then click Run.")
        self.folder_var = tk.StringVar()
        self.output_var = tk.StringVar()

        self.add_path_row(
            0, "Folder - files to list", self.folder_var, "Browse", self.choose_list_folder
        )
        self.add_path_row(1, "Output TXT file", self.output_var, "Save As", self.choose_output)
        self.add_run_row(2)

    def choose_list_folder(self) -> None:
        folder = self.choose_folder(self.folder_var)
        if folder and not self.output_var.get():
            self.output_var.set(str(default_output_path(clean_path(folder))))

    def choose_output(self) -> None:
        initial_file = "file_list.txt"
        if self.folder_var.get():
            initial_file = default_output_path(clean_path(self.folder_var.get())).name

        output_file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=initial_file,
        )
        if output_file:
            self.output_var.set(output_file)

    def execute(self) -> tuple[str, str]:
        if not self.folder_var.get():
            raise ValueError("Please choose a folder.")

        folder = clean_path(self.folder_var.get())
        output_file = (
            clean_path(self.output_var.get())
            if self.output_var.get()
            else default_output_path(folder)
        )

        validate_folder(folder, "Folder")

        total = write_file_list(folder, output_file)
        self.output_var.set(str(output_file))
        return (
            f"Listed {total} file(s) in:\n{output_file}",
            f"Done. Listed {total} file(s).",
        )


def run_gui() -> None:
    root = tk.Tk()
    root.title("Photo Selection")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=8, pady=8)
    notebook.add(MatchPhotosTab(notebook), text="Match Photos")
    notebook.add(FileListTab(notebook), text="File List")

    root.update_idletasks()
    root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())
    root.mainloop()
