from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .i18n import t


def collect_files(folder: Path) -> list[Path]:
    return sorted(
        (path for path in folder.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(folder).as_posix().casefold(),
    )


def default_output_path(folder: Path) -> Path:
    safe_name = folder.name or "folder"
    return folder.parent / f"{safe_name}_file_list.txt"


def write_file_list(folder: Path, output_file: Path) -> int:
    files = collect_files(folder)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        t("list_header_folder", folder=folder),
        t("list_header_total", count=len(files)),
        t("list_header_created", time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "",
        t("list_header_files"),
    ]

    lines.extend(path.relative_to(folder).as_posix() for path in files)
    output_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(files)
