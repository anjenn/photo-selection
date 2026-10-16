from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable

from .file_list import default_output_path, write_file_list
from .i18n import LANGUAGES, get_language, save_language, set_language, t
from .intersection import copy_photo_intersection
from .paths import clean_path, validate_folder


FILE_TYPE_KEYS = {"all": "type_all", "jpeg": "type_jpeg", "raw": "type_raw"}


class ToolTab(ttk.Frame):
    """A notebook tab with path rows, a Run button, and a status line."""

    busy_key = ""

    def __init__(self, parent: ttk.Notebook, idle_key: str) -> None:
        super().__init__(parent, padding=18)
        self.columnconfigure(1, weight=1)
        # Widgets whose text is re-read from the strings table on language change.
        self.translated_widgets: list[tuple[tk.Widget, str]] = []
        self.status_var = tk.StringVar()
        self.set_status(idle_key)

    def translated(self, widget_class: type[tk.Widget], parent: tk.Widget, key: str, **options):
        widget = widget_class(parent, text=t(key), **options)
        self.translated_widgets.append((widget, key))
        return widget

    def set_status(self, key: str, **values: object) -> None:
        self.status = (key, values)
        self.status_var.set(t(key, **values))

    def retranslate(self) -> None:
        for widget, key in self.translated_widgets:
            widget.configure(text=t(key))
        key, values = self.status
        self.set_status(key, **values)

    def add_path_row(
        self,
        row: int,
        label_key: str,
        variable: tk.StringVar,
        button_key: str,
        command: Callable[[], None],
    ) -> None:
        self.translated(ttk.Label, self, label_key).grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(self, textvariable=variable, width=56).grid(
            row=row, column=1, sticky="ew", padx=10, pady=6
        )
        self.translated(ttk.Button, self, button_key, width=12, command=command).grid(
            row=row, column=2, sticky="e", pady=6
        )

    def add_folder_row(self, row: int, label_key: str, variable: tk.StringVar) -> None:
        self.add_path_row(row, label_key, variable, "browse", lambda: self.choose_folder(variable))

    def add_choice_row(
        self, row: int, label_key: str, variable: tk.StringVar, choices: dict[str, str]
    ) -> None:
        self.translated(ttk.Label, self, label_key).grid(row=row, column=0, sticky="w", pady=6)
        frame = ttk.Frame(self)
        frame.grid(row=row, column=1, sticky="w", padx=10, pady=6)
        for value, text_key in choices.items():
            self.translated(
                ttk.Radiobutton, frame, text_key, variable=variable, value=value
            ).pack(side="left", padx=(0, 18))

    def add_run_row(self, row: int) -> None:
        self.translated(ttk.Button, self, "run", width=16, command=self.run).grid(
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
        self.set_status(self.busy_key)
        self.update_idletasks()
        try:
            done_message, (status_key, status_values) = self.execute()
        except Exception as error:
            messagebox.showerror(t("error_title"), str(error))
            self.set_status("failed_status")
        else:
            messagebox.showinfo(t("done_title"), done_message)
            self.set_status(status_key, **status_values)

    def execute(self) -> tuple[str, tuple[str, dict[str, object]]]:
        """Do the tab's work; return (dialog message, (status key, status values))."""
        raise NotImplementedError


class MatchPhotosTab(ToolTab):
    busy_key = "match_busy"

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, "match_idle")
        self.folder_a_var = tk.StringVar()
        self.folder_b_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.source_var = tk.StringVar(value="B")
        self.file_type_var = tk.StringVar(value="all")

        self.add_folder_row(0, "folder_a_label", self.folder_a_var)
        self.add_folder_row(1, "folder_b_label", self.folder_b_var)
        self.add_folder_row(2, "folder_c_label", self.output_var)
        self.add_choice_row(
            3, "source_label", self.source_var, {"A": "folder_a", "B": "folder_b"}
        )
        self.add_choice_row(4, "file_type_label", self.file_type_var, FILE_TYPE_KEYS)
        self.add_run_row(5)

    def execute(self) -> tuple[str, tuple[str, dict[str, object]]]:
        if not (self.folder_a_var.get() and self.folder_b_var.get() and self.output_var.get()):
            raise ValueError(t("need_three_folders"))

        folder_a = clean_path(self.folder_a_var.get())
        folder_b = clean_path(self.folder_b_var.get())
        output_folder = clean_path(self.output_var.get())
        source = self.source_var.get()

        validate_folder(folder_a, t("folder_a"))
        validate_folder(folder_b, t("folder_b"))

        copied = copy_photo_intersection(
            folder_a, folder_b, output_folder, source, self.file_type_var.get()
        )
        return (
            t("match_done", count=copied, source=source, folder=output_folder),
            ("match_done_status", {"count": copied}),
        )


class FileListTab(ToolTab):
    busy_key = "list_busy"

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, "list_idle")
        self.folder_var = tk.StringVar()
        self.output_var = tk.StringVar()

        self.add_path_row(
            0, "list_folder_label", self.folder_var, "browse", self.choose_list_folder
        )
        self.add_path_row(1, "list_output_label", self.output_var, "save_as", self.choose_output)
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
            filetypes=[(t("text_files"), "*.txt"), (t("all_files"), "*.*")],
            initialfile=initial_file,
        )
        if output_file:
            self.output_var.set(output_file)

    def execute(self) -> tuple[str, tuple[str, dict[str, object]]]:
        if not self.folder_var.get():
            raise ValueError(t("need_folder"))

        folder = clean_path(self.folder_var.get())
        output_file = (
            clean_path(self.output_var.get())
            if self.output_var.get()
            else default_output_path(folder)
        )

        validate_folder(folder, t("folder"))

        total = write_file_list(folder, output_file)
        self.output_var.set(str(output_file))
        return (
            t("list_done", count=total, file=output_file),
            ("list_done_status", {"count": total}),
        )


class PhotoSelectionApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root

        top_bar = ttk.Frame(root, padding=(8, 8, 8, 0))
        top_bar.pack(fill="x")
        self.language_box = ttk.Combobox(
            top_bar, state="readonly", width=10, values=list(LANGUAGES.values())
        )
        self.language_box.current(list(LANGUAGES).index(get_language()))
        self.language_box.bind("<<ComboboxSelected>>", self.change_language)
        self.language_box.pack(side="right")
        self.language_label = ttk.Label(top_bar)
        self.language_label.pack(side="right", padx=(0, 6))

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)
        self.tabs = [(MatchPhotosTab(self.notebook), "tab_match"), (FileListTab(self.notebook), "tab_list")]
        for tab, key in self.tabs:
            self.notebook.add(tab, text=t(key))

        self.retranslate()

    def change_language(self, _event: tk.Event | None = None) -> None:
        language = list(LANGUAGES)[self.language_box.current()]
        set_language(language)
        save_language(language)
        self.language_box.selection_clear()
        self.retranslate()

    def retranslate(self) -> None:
        self.root.title(t("app_title"))
        self.language_label.configure(text=t("language"))
        for tab, key in self.tabs:
            self.notebook.tab(tab, text=t(key))
            tab.retranslate()

        self.root.update_idletasks()
        self.root.minsize(self.root.winfo_reqwidth(), self.root.winfo_reqheight())


def run_gui() -> None:
    root = tk.Tk()
    PhotoSelectionApp(root)
    root.mainloop()
