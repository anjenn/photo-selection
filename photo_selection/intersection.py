from __future__ import annotations

import shutil
import unicodedata
from pathlib import Path

from .i18n import t


JPEG_EXTENSIONS = frozenset({".jpg", ".jpeg"})
RAW_EXTENSIONS = frozenset(
    {".cr2", ".cr3", ".nef", ".arw", ".dng", ".raf", ".orf", ".rw2"}
)
PHOTO_EXTENSIONS = (
    JPEG_EXTENSIONS
    | RAW_EXTENSIONS
    | {".png", ".gif", ".webp", ".bmp", ".tif", ".tiff", ".heic", ".heif"}
)

# Which files may be copied out of the source folder.
FILE_TYPES: dict[str, frozenset[str]] = {
    "all": PHOTO_EXTENSIONS,
    "jpeg": JPEG_EXTENSIONS,
    "raw": RAW_EXTENSIONS,
}


def normalized_stem(path: Path) -> str:
    return unicodedata.normalize("NFC", path.stem).casefold()


def collect_photo_paths_by_stem(
    folder: Path, extensions: frozenset[str]
) -> dict[str, list[Path]]:
    photos_by_stem: dict[str, list[Path]] = {}
    for path in sorted(folder.rglob("*")):
        if not path.is_file() or path.suffix.casefold() not in extensions:
            continue

        photos_by_stem.setdefault(normalized_stem(path), []).append(path)

    return photos_by_stem


def unique_destination(output_folder: Path, filename: str) -> Path:
    destination = output_folder / filename
    if not destination.exists():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    counter = 2

    while True:
        candidate = output_folder / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def path_is_inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def validate_output_folder(folder_a: Path, folder_b: Path, output_folder: Path) -> None:
    output_folder = output_folder.resolve()
    for source_folder, label in (
        (folder_a.resolve(), t("folder_a")),
        (folder_b.resolve(), t("folder_b")),
    ):
        if output_folder == source_folder:
            raise ValueError(t("err_same_as_source", label=label))
        if path_is_inside(source_folder, output_folder):
            raise ValueError(t("err_contains_source", label=label))


def reset_output_folder(output_folder: Path) -> None:
    if output_folder.exists() and not output_folder.is_dir():
        raise NotADirectoryError(t("err_dest_not_dir", path=output_folder))

    output_folder.mkdir(parents=True, exist_ok=True)
    for child in output_folder.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def copy_photo_intersection(
    folder_a: Path,
    folder_b: Path,
    output_folder: Path,
    source_folder: str,
    file_type: str = "all",
) -> int:
    """Refresh output_folder with one photo per filename found in both A and B.

    Names match ignoring case and extension. Files are copied from the source
    folder ("A" or "B"), limited to the chosen file type. Returns the number
    of files copied.
    """
    if source_folder not in ("A", "B"):
        raise ValueError(t("err_bad_source"))
    if file_type not in FILE_TYPES:
        raise ValueError(t("err_bad_type", types=", ".join(FILE_TYPES)))

    validate_output_folder(folder_a, folder_b, output_folder)
    reset_output_folder(output_folder)

    source, other = (folder_a, folder_b) if source_folder == "A" else (folder_b, folder_a)
    source_photos = collect_photo_paths_by_stem(source, FILE_TYPES[file_type])
    other_stems = collect_photo_paths_by_stem(other, PHOTO_EXTENSIONS).keys()

    copied = 0
    for stem in sorted(source_photos.keys() & other_stems):
        photo_path = source_photos[stem][0]
        shutil.copy2(photo_path, unique_destination(output_folder, photo_path.name))
        copied += 1

    return copied
