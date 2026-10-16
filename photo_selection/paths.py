from __future__ import annotations

from pathlib import Path


def clean_path(value: str) -> Path:
    """Accept paths pasted from Explorer with or without surrounding quotes."""
    return Path(value.strip().strip('"').strip("'")).expanduser()


def validate_folder(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{label} does not exist: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"{label} is not a folder: {path}")
