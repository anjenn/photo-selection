from __future__ import annotations

from datetime import datetime
from pathlib import Path


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
        f"Folder: {folder}",
        f"Total files: {len(files)}",
        f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "Files:",
    ]

    lines.extend(path.relative_to(folder).as_posix() for path in files)
    output_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(files)
