from __future__ import annotations

import os
import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, ttk
from typing import Callable

from . import theme
from .file_list import default_output_path, write_file_list
from .i18n import LANGUAGES, get_language, save_language, set_language, t
from .intersection import copy_photo_intersection
from .paths import clean_path, validate_folder
from .targets import copy_target_photos, count_targets, parse_targets, read_text_file
from .theme import px


FILE_TYPE_KEYS = {"all": "type_all", "regular": "type_regular", "raw": "type_raw"}
MISSING_SHOWN = 8  # missing targets listed in the status line before "and N more"

# What a finished job reports: (status kind, status key, status values, path to open).
JobResult = tuple[str, str, dict[str, object], Path]


def open_path(path: Path) -> None:
    if hasattr(os, "startfile"):
        os.startfile(path)
    else:
        webbrowser.open(path.as_uri())


def wrap_to_width(label: ttk.Label) -> None:
    """Wrap a label's text to whatever width the layout gives it.

    width=1 stops the text from requesting width itself; otherwise the label
    and the window would keep resizing each other.
    """
    label.configure(width=1, wraplength=px(400))
    label.bind(
        "<Configure>",
        lambda event: label.configure(wraplength=max(event.width - px(4), px(40))),
    )


class ToolPage(ttk.Frame):
    """One tool: a description, cards of inputs, and an action bar with status."""

    run_key = ""
    busy_key = ""
    idle_key = ""
    open_key = ""

    def __init__(self, parent: ttk.Notebook, description_key: str) -> None:
        super().__init__(parent, padding=(px(24), px(18), px(24), px(20)))
        self.columnconfigure(0, weight=1)
        # Widgets whose text is re-read from the strings table on language change.
        self.translated_widgets: list[tuple[tk.Widget, str]] = []
        self.status: tuple[str, str | None, str | None, dict[str, object]] = (
            "idle", self.idle_key, None, {}
        )
        self.status_var = tk.StringVar()
        self.result_path: Path | None = None
        self.next_row = 0

        description = self.translated(ttk.Label, self, description_key, style="Muted.TLabel")
        self.place_row(description, pady=(0, px(14)))
        wrap_to_width(description)

    def translated(self, widget_class: type[tk.Widget], parent: tk.Widget, key: str, **options):
        widget = widget_class(parent, text=t(key), **options)
        self.translated_widgets.append((widget, key))
        return widget

    def place_row(self, widget: tk.Widget, **grid_options) -> None:
        widget.grid(row=self.next_row, column=0, sticky="ew", **grid_options)
        self.next_row += 1

    def add_card(self, title_key: str) -> ttk.Frame:
        card = ttk.Frame(self, style="Card.TFrame", padding=(px(18), px(12), px(18), px(14)))
        card.columnconfigure(1, weight=1)
        self.translated(ttk.Label, card, title_key, style="Section.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, px(6))
        )
        self.place_row(card, pady=(0, px(14)))
        return card

    def add_path_row(
        self,
        card: ttk.Frame,
        row: int,
        label_key: str,
        variable: tk.StringVar,
        button_key: str,
        command: Callable[[], None],
    ) -> None:
        self.translated(ttk.Label, card, label_key, style="Card.TLabel").grid(
            row=row, column=0, sticky="w", padx=(0, px(16)), pady=px(5)
        )
        ttk.Entry(card, textvariable=variable, width=46).grid(
            row=row, column=1, sticky="ew", pady=px(5)
        )
        self.translated(ttk.Button, card, button_key, command=command).grid(
            row=row, column=2, sticky="ew", padx=(px(8), 0), pady=px(5)
        )

    def add_folder_row(
        self, card: ttk.Frame, row: int, label_key: str, variable: tk.StringVar
    ) -> None:
        self.add_path_row(
            card, row, label_key, variable, "browse", lambda: self.choose_folder(variable)
        )

    def add_choice_row(
        self,
        card: ttk.Frame,
        row: int,
        label_key: str,
        variable: tk.StringVar,
        choices: dict[str, str],
    ) -> None:
        self.translated(ttk.Label, card, label_key, style="Card.TLabel").grid(
            row=row, column=0, sticky="w", padx=(0, px(16)), pady=px(4)
        )
        options = ttk.Frame(card, style="Surface.TFrame")
        options.grid(row=row, column=1, columnspan=2, sticky="w", pady=px(4))
        for value, text_key in choices.items():
            self.translated(
                ttk.Radiobutton, options, text_key, variable=variable, value=value
            ).pack(side="left", padx=(0, px(20)))

    def add_action_bar(self) -> None:
        """A full-width status line, then right-aligned buttons: column 1 is free for
        extra buttons, then Open and Run."""
        status = ttk.Frame(self)
        status.columnconfigure(1, weight=1)
        self.place_row(status, pady=(px(2), px(10)))

        dot_size = px(8)
        self.status_dot = tk.Canvas(
            status,
            width=dot_size,
            height=dot_size,
            background=theme.BG,
            highlightthickness=0,
            borderwidth=0,
        )
        self.status_dot.create_oval(0, 0, dot_size - 1, dot_size - 1, outline="", tags="dot")
        self.status_dot.grid(row=0, column=0, sticky="n", padx=(px(2), px(8)), pady=(px(6), 0))
        self.status_label = ttk.Label(status, textvariable=self.status_var)
        self.status_label.grid(row=0, column=1, sticky="ew")
        wrap_to_width(self.status_label)

        self.action_bar = bar = ttk.Frame(self)
        bar.columnconfigure(0, weight=1)
        self.place_row(bar)
        self.open_button = self.translated(
            ttk.Button, bar, self.open_key, command=self.open_result
        )
        self.open_button.grid(row=0, column=2, padx=(px(8), 0))
        self.open_button.grid_remove()
        self.run_button = self.translated(
            ttk.Button, bar, self.run_key, style="Accent.TButton", command=self.run
        )
        self.run_button.grid(row=0, column=3, padx=(px(8), 0))

        self.progress = ttk.Progressbar(
            self, mode="indeterminate", style="Idle.Horizontal.TProgressbar"
        )
        self.place_row(self.progress, pady=(px(14), 0))
        self.refresh_status()

    def set_status(
        self, kind: str, key: str | None = None, text: str | None = None, **values: object
    ) -> None:
        self.status = (kind, key, text, values)
        self.refresh_status()

    def refresh_status(self) -> None:
        kind, key, text, values = self.status
        self.status_var.set(t(key, **values) if key else text)
        self.status_label.configure(style=f"{kind.title()}.Status.TLabel")
        self.status_dot.itemconfigure("dot", fill=theme.STATUS_COLORS[kind])

    def retranslate(self) -> None:
        for widget, key in self.translated_widgets:
            widget.configure(text=t(key))
        self.refresh_status()

    def choose_folder(self, variable: tk.StringVar) -> str:
        folder = filedialog.askdirectory(initialdir=variable.get() or None)
        if folder:
            variable.set(folder)
        return folder

    def set_busy(self, busy: bool) -> None:
        self.run_button.state(["disabled"] if busy else ["!disabled"])
        if busy:
            self.progress.configure(style="Busy.Horizontal.TProgressbar")
            self.progress.start(12)
        else:
            self.progress.stop()
            self.progress.configure(style="Idle.Horizontal.TProgressbar")

    def clear_result(self) -> None:
        """Hide the buttons that act on the previous run's result."""
        self.open_button.grid_remove()

    def show_result(self) -> None:
        self.open_button.grid()

    def run(self) -> None:
        self.clear_result()
        try:
            job = self.create_job()
        except (OSError, ValueError) as error:
            self.set_status("error", text=str(error))
            return

        self.set_busy(True)
        self.set_status("busy", self.busy_key)
        outcome: dict[str, object] = {}

        def work() -> None:
            try:
                outcome["result"] = job()
            except Exception as error:
                outcome["error"] = error

        worker = threading.Thread(target=work, daemon=True)
        worker.start()
        self.after(100, self.wait_for, worker, outcome)

    def wait_for(self, worker: threading.Thread, outcome: dict[str, object]) -> None:
        if worker.is_alive():
            self.after(100, self.wait_for, worker, outcome)
            return

        self.set_busy(False)
        if "error" in outcome:
            self.set_status("error", text=str(outcome["error"]))
            return

        kind, key, values, self.result_path = outcome["result"]
        self.set_status(kind, key, **values)
        self.show_result()

    def open_result(self) -> None:
        if self.result_path is None:
            return
        try:
            open_path(self.result_path)
        except OSError as error:
            self.set_status("error", text=str(error))

    def create_job(self) -> Callable[[], JobResult]:
        """Check the inputs and return the work to run in the background."""
        raise NotImplementedError


class MatchPhotosPage(ToolPage):
    run_key = "match_run"
    busy_key = "match_busy"
    idle_key = "match_idle"
    open_key = "open_folder"

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, "match_description")
        self.folder_a_var = tk.StringVar()
        self.folder_b_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.source_var = tk.StringVar(value="B")
        self.file_type_var = tk.StringVar(value="all")

        folders = self.add_card("section_folders")
        self.add_folder_row(folders, 1, "folder_a", self.folder_a_var)
        self.add_folder_row(folders, 2, "folder_b", self.folder_b_var)
        self.add_folder_row(folders, 3, "folder_c_label", self.output_var)
        self.translated(ttk.Label, folders, "match_warning", style="Warning.TLabel").grid(
            row=4, column=1, columnspan=2, sticky="ew", pady=(px(4), 0)
        )

        options = self.add_card("section_options")
        self.add_choice_row(
            options, 1, "source_label", self.source_var, {"A": "folder_a", "B": "folder_b"}
        )
        self.add_choice_row(options, 2, "file_type_label", self.file_type_var, FILE_TYPE_KEYS)

        self.add_action_bar()

    def create_job(self) -> Callable[[], JobResult]:
        if not (self.folder_a_var.get() and self.folder_b_var.get() and self.output_var.get()):
            raise ValueError(t("need_three_folders"))

        folder_a = clean_path(self.folder_a_var.get())
        folder_b = clean_path(self.folder_b_var.get())
        output_folder = clean_path(self.output_var.get())
        source = self.source_var.get()
        file_type = self.file_type_var.get()

        validate_folder(folder_a, t("folder_a"))
        validate_folder(folder_b, t("folder_b"))

        def job() -> JobResult:
            copied = copy_photo_intersection(folder_a, folder_b, output_folder, source, file_type)
            if copied == 0:
                return ("warning", "match_none", {}, output_folder)
            return ("success", "match_done_status", {"count": copied}, output_folder)

        return job


class TargetFinderPage(ToolPage):
    run_key = "target_run"
    busy_key = "target_busy"
    idle_key = "target_idle"
    open_key = "open_folder"

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, "target_description")
        self.photo_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.file_type_var = tk.StringVar(value="all")
        self.missing: list[str] = []

        targets = self.add_card("section_targets")
        self.add_target_box(targets)

        folders = self.add_card("section_folders")
        self.add_folder_row(folders, 1, "photo_folder", self.photo_var)
        self.add_folder_row(folders, 2, "output_folder", self.output_var)
        self.translated(ttk.Label, folders, "target_warning", style="Warning.TLabel").grid(
            row=3, column=1, columnspan=2, sticky="ew", pady=(px(4), 0)
        )

        options = self.add_card("section_options")
        self.add_choice_row(options, 1, "file_type_label", self.file_type_var, FILE_TYPE_KEYS)

        self.add_action_bar()
        self.missing_button = self.translated(
            ttk.Button, self.action_bar, "copy_missing", command=self.copy_missing
        )
        self.missing_button.grid(row=0, column=1, padx=(px(8), 0))
        self.missing_button.grid_remove()
        self.update_count()

    def add_target_box(self, card: ttk.Frame) -> None:
        box = tk.Frame(
            card,
            background=theme.SURFACE,
            highlightthickness=1,
            highlightbackground=theme.BORDER,
            highlightcolor=theme.ACCENT,
        )
        box.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, px(6)))
        box.columnconfigure(0, weight=1)
        self.text = tk.Text(
            box,
            height=5,
            width=40,
            wrap="word",
            undo=True,
            font="TkTextFont",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            background=theme.SURFACE,
            foreground=theme.TEXT,
            insertbackground=theme.TEXT,
            selectbackground=theme.ACCENT,
            selectforeground=theme.SURFACE,
            padx=px(8),
            pady=px(6),
        )
        self.text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(box, orient="vertical", command=self.text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text.configure(yscrollcommand=scrollbar.set)
        # Show the accent border while typing, like the entries.
        self.text.bind("<FocusIn>", lambda _e: box.configure(highlightbackground=theme.ACCENT))
        self.text.bind("<FocusOut>", lambda _e: box.configure(highlightbackground=theme.BORDER))
        self.text.bind("<<Modified>>", self.on_text_modified)

        buttons = ttk.Frame(card, style="Surface.TFrame")
        buttons.grid(row=1, column=2, sticky="n", padx=(px(8), 0))
        self.translated(ttk.Button, buttons, "load_txt", command=self.load_txt).pack(fill="x")
        self.translated(ttk.Button, buttons, "clear", command=self.clear_text).pack(
            fill="x", pady=(px(6), 0)
        )

        hint = self.translated(ttk.Label, card, "target_hint", style="Hint.TLabel")
        hint.grid(row=2, column=0, columnspan=2, sticky="ew")
        wrap_to_width(hint)
        self.count_label = ttk.Label(card, style="Count.TLabel")
        self.count_label.grid(row=2, column=2, sticky="ne", padx=(px(8), 0))

    def list_text(self) -> str:
        return self.text.get("1.0", "end-1c")

    def on_text_modified(self, _event: tk.Event | None = None) -> None:
        if self.text.edit_modified():
            self.text.edit_modified(False)
            self.update_count()

    def update_count(self) -> None:
        count = count_targets(parse_targets(self.list_text()))
        self.count_label.configure(text=t("name_count", count=count))

    def retranslate(self) -> None:
        super().retranslate()
        self.update_count()

    def load_txt(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=[(t("text_files"), "*.txt"), (t("all_files"), "*.*")]
        )
        if not path:
            return
        try:
            content = read_text_file(Path(path))
        except OSError as error:
            self.set_status("error", text=str(error))
            return
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)

    def clear_text(self) -> None:
        self.text.delete("1.0", "end")
        self.text.focus_set()

    def clear_result(self) -> None:
        super().clear_result()
        self.missing_button.grid_remove()

    def show_result(self) -> None:
        super().show_result()
        if self.missing:
            self.missing_button.grid()

    def copy_missing(self) -> None:
        self.clipboard_clear()
        self.clipboard_append("\n".join(self.missing))
        self.missing_button.configure(text=t("copied"))
        self.after(1500, lambda: self.missing_button.configure(text=t("copy_missing")))

    def create_job(self) -> Callable[[], JobResult]:
        targets = parse_targets(self.list_text())
        if not targets:
            raise ValueError(t("err_empty_list"))
        if not (self.photo_var.get() and self.output_var.get()):
            raise ValueError(t("need_target_folders"))

        photo_folder = clean_path(self.photo_var.get())
        output_folder = clean_path(self.output_var.get())
        file_type = self.file_type_var.get()
        validate_folder(photo_folder, t("photo_folder"))

        def job() -> JobResult:
            result = copy_target_photos(targets, photo_folder, output_folder, file_type)
            self.missing = result.missing
            if result.copied == 0:
                return ("warning", "target_none", {}, output_folder)
            if result.missing:
                shown = ", ".join(result.missing[:MISSING_SHOWN])
                extra = len(result.missing) - MISSING_SHOWN
                names = t("and_more", names=shown, count=extra) if extra > 0 else shown
                values = {
                    "count": result.copied,
                    "missing_count": len(result.missing),
                    "names": names,
                }
                return ("warning", "target_partial", values, output_folder)
            values = {"found": result.found, "count": result.copied}
            return ("success", "target_done_status", values, output_folder)

        return job


class FileListPage(ToolPage):
    run_key = "list_run"
    busy_key = "list_busy"
    idle_key = "list_idle"
    open_key = "open_file"

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, "list_description")
        self.folder_var = tk.StringVar()
        self.output_var = tk.StringVar()

        locations = self.add_card("section_locations")
        self.add_path_row(
            locations, 1, "list_folder_label", self.folder_var, "browse", self.choose_list_folder
        )
        self.add_path_row(
            locations, 2, "list_output_label", self.output_var, "save_as", self.choose_output
        )

        self.add_action_bar()

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

    def create_job(self) -> Callable[[], JobResult]:
        if not self.folder_var.get():
            raise ValueError(t("need_folder"))

        folder = clean_path(self.folder_var.get())
        output_file = (
            clean_path(self.output_var.get())
            if self.output_var.get()
            else default_output_path(folder)
        )
        validate_folder(folder, t("folder"))
        self.output_var.set(str(output_file))

        def job() -> JobResult:
            total = write_file_list(folder, output_file)
            return ("success", "list_done_status", {"count": total}, output_file)

        return job


class PhotoSelectionApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.columnconfigure(0, weight=1)
        root.rowconfigure(2, weight=1)

        header = self.build_header()
        header.grid(row=0, column=0, sticky="ew")
        tk.Frame(root, height=1, background=theme.BORDER).grid(row=1, column=0, sticky="ew")

        self.notebook = ttk.Notebook(root, style="Plain.TNotebook")
        self.notebook.grid(row=2, column=0, sticky="nsew")
        self.pages: list[tuple[ToolPage, str]] = [
            (MatchPhotosPage(self.notebook), "tab_match"),
            (TargetFinderPage(self.notebook), "tab_target"),
            (FileListPage(self.notebook), "tab_list"),
        ]
        self.nav_items: list[tuple[ttk.Label, tk.Frame]] = []
        for index, (page, key) in enumerate(self.pages):
            self.notebook.add(page)
            self.add_nav_item(index, key)

        root.bind("<Control-Tab>", lambda _event: self.show_page(self.current_page + 1))
        self.show_page(0)
        self.retranslate()

    def build_header(self) -> ttk.Frame:
        header = ttk.Frame(self.root, style="Surface.TFrame", padding=(px(24), px(18), px(24), 0))
        header.columnconfigure(1, weight=1)

        theme.draw_logo(header, px(42)).grid(row=0, column=0, rowspan=2, padx=(0, px(14)))
        self.title_label = ttk.Label(header, style="Title.TLabel")
        self.title_label.grid(row=0, column=1, sticky="sw")
        self.subtitle_label = ttk.Label(header, style="Subtitle.TLabel")
        self.subtitle_label.grid(row=1, column=1, sticky="nw")

        language = ttk.Frame(header, style="Surface.TFrame")
        language.grid(row=0, column=2, rowspan=2, sticky="e")
        self.language_label = ttk.Label(language, style="Header.TLabel")
        self.language_label.pack(side="left", padx=(0, px(8)))
        self.language_box = ttk.Combobox(
            language, state="readonly", width=9, values=list(LANGUAGES.values())
        )
        self.language_box.current(list(LANGUAGES).index(get_language()))
        self.language_box.bind("<<ComboboxSelected>>", self.change_language)
        self.language_box.pack(side="left")

        self.nav = ttk.Frame(header, style="Surface.TFrame")
        self.nav.grid(row=2, column=0, columnspan=3, sticky="w", pady=(px(18), 0))
        return header

    def add_nav_item(self, index: int, key: str) -> None:
        label = ttk.Label(self.nav, text=t(key), style="Nav.TLabel", cursor="hand2")
        label.grid(row=0, column=index, padx=(0, px(26)), sticky="w")
        label.bind("<Button-1>", lambda _event: self.show_page(index))
        underline = tk.Frame(self.nav, height=px(3), background=theme.SURFACE)
        underline.grid(row=1, column=index, padx=(0, px(26)), sticky="ew")
        self.nav_items.append((label, underline))

    def show_page(self, index: int) -> None:
        self.current_page = index % len(self.pages)
        self.notebook.select(self.current_page)
        for item_index, (label, underline) in enumerate(self.nav_items):
            active = item_index == self.current_page
            label.configure(style="NavActive.Nav.TLabel" if active else "Nav.TLabel")
            underline.configure(background=theme.ACCENT if active else theme.SURFACE)

    def change_language(self, _event: tk.Event | None = None) -> None:
        language = list(LANGUAGES)[self.language_box.current()]
        set_language(language)
        save_language(language)
        self.language_box.selection_clear()
        theme.apply_fonts(self.root)
        self.retranslate()

    def retranslate(self) -> None:
        self.root.title(t("app_title"))
        self.title_label.configure(text=t("app_title"))
        self.subtitle_label.configure(text=t("app_subtitle"))
        self.language_label.configure(text=t("language"))
        for (page, key), (label, _underline) in zip(self.pages, self.nav_items):
            label.configure(text=t(key))
            page.retranslate()

        self.root.update_idletasks()
        self.root.minsize(self.root.winfo_reqwidth(), self.root.winfo_reqheight())


def run_gui() -> None:
    theme.enable_dpi_awareness()
    root = tk.Tk()
    theme.setup_theme(root)
    PhotoSelectionApp(root)
    root.mainloop()
