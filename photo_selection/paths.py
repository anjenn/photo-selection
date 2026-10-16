from __future__ import annotations

from pathlib import Path

from .i18n import t


def clean_path(value: str) -> Path:
    """Accept paths pasted from Explorer with or without surrounding quotes."""
    return Path(value.strip().strip('"').strip("'")).expanduser()


def validate_folder(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(t("err_not_found", label=label, path=path))
    if not path.is_dir():
        raise NotADirectoryError(t("err_not_dir", label=label, path=path))
