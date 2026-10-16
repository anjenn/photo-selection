"""Find Targets: copy the photos a free-form list refers to out of a folder.

The list can be file names ("IMG_0001.JPG, img_2.png"), bare numbers
("1 2 15번"), ranges ("20~25"), or a File List TXT. Numbers match a photo's
frame number (the last number in its name, ignoring leading zeros and copy
suffixes like "-2" or "(2)"), so "1" finds IMG_0001.JPG and "2637" finds
260913_히나2637.JPG and IMG_2637-2.JPG.
"""
from __future__ import annotations

import locale
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path, PureWindowsPath

from .i18n import STRINGS, t
from .intersection import (
    FILE_TYPES,
    PHOTO_EXTENSIONS,
    collect_photo_paths_by_stem,
    normalize_name,
    reset_output_folder,
    unique_destination,
    validate_output_folder,
)


# A File List TXT has a header that ends with this line (in either language);
# after it come the file names, one per line.
FILE_LIST_MARKERS = {
    strings["list_header_files"].casefold() for strings in STRINGS.values()
}
COUNTER_WORDS = re.compile(r"(\d)\s*(?:번|장|컷)")  # "12번" -> "12"
SPACED_RANGE = re.compile(r"(\d)\s*~\s*(\d)")  # "20 ~ 25" -> "20~25"
SEPARATORS = re.compile(r"[,;/|+、·\s]+")
RANGE = re.compile(r"(\d+)[~\-–](\d+)")
DIGITS = re.compile(r"\d+")
COPY_SUFFIX = re.compile(r"(?:-|\s*\()\d{1,2}\)?$")  # "IMG_2637-2", "IMG_2637 (2)"
EDGE_PUNCTUATION = "\"'`()[]{}<>#.:!?*"
# Suffixes like ".png" are treated as extensions; ".09" in "2026.09.13" is not.
EXTENSION_LIKE = re.compile(r"\.[a-z][a-z0-9]{0,4}")
MAX_RANGE = 5000


@dataclass(frozen=True)
class Target:
    text: str  # as written, for reporting what was not found
    number: int | None = None  # a bare number
    name: str = ""  # otherwise a normalized filename without extension

    @property
    def has_digit(self) -> bool:
        return self.number is not None or any(c.isdigit() for c in self.name)


@dataclass(frozen=True)
class TargetResult:
    copied: int
    found: int
    missing: list[str] = field(default_factory=list)


def canonical(name: str) -> str:
    """Drop leading zeros so that img_0001 and img_1 compare equal."""
    return DIGITS.sub(lambda match: str(int(match.group())), name)


def frame_number(name: str) -> int | None:
    """The last number in a filename, skipping a copy suffix like "-2" or "(2)"."""
    runs = DIGITS.findall(COPY_SUFFIX.sub("", name)) or DIGITS.findall(name)
    return int(runs[-1]) if runs else None


def name_without_extension(name: str) -> str:
    suffix = PureWindowsPath(name).suffix
    if suffix and (
        suffix.casefold() in PHOTO_EXTENSIONS or EXTENSION_LIKE.fullmatch(suffix.casefold())
    ):
        return name[: -len(suffix)]
    return name


def entry_targets(entry: str) -> list[Target]:
    entry = entry.strip().strip(EDGE_PUNCTUATION).strip()
    if not entry:
        return []

    if not any(c.isalpha() for c in entry):
        span = RANGE.fullmatch(entry)
        if span:
            start, end = int(span[1]), int(span[2])
            if start < end <= start + MAX_RANGE:
                return [Target(str(n), number=n) for n in range(start, end + 1)]
        # "1.2.3" or "#7" lists numbers, but "20260913_143052" or "2637-2" is a filename.
        if not any(c in "_-" for c in entry):
            return [Target(run, number=int(run)) for run in DIGITS.findall(entry)]

    name = name_without_extension(PureWindowsPath(entry).name)  # drop any folder path
    return [Target(entry, name=normalize_name(name))] if name else []


def parse_targets(text: str) -> list[Target]:
    """Read file names and numbers out of free-form text, without duplicates."""
    lines = text.splitlines()
    marker = next(
        (i for i, line in enumerate(lines) if line.strip().casefold() in FILE_LIST_MARKERS),
        None,
    )
    if marker is not None:
        entries = lines[marker + 1 :]  # one name per line, so names may contain spaces
    else:
        text = SPACED_RANGE.sub(r"\1~\2", COUNTER_WORDS.sub(r"\1 ", text))
        entries = SEPARATORS.split(text)

    targets: dict[tuple[int | None, str], Target] = {}
    for entry in entries:
        for target in entry_targets(entry):
            targets.setdefault((target.number, target.name), target)
    return list(targets.values())


def count_targets(targets: list[Target]) -> int:
    """Targets worth counting: numbers and names with digits, not stray words."""
    return sum(target.has_digit for target in targets)


def joined_at_boundary(a: str, b: str) -> bool:
    """True if the shorter name (with a digit) starts or ends the longer at a separator.

    So "img_1" matches "studio-img_1" and "img_1_edit", but not "img_10".
    """
    shorter, longer = sorted((a, b), key=len)
    if len(shorter) == len(longer) or not any(c.isdigit() for c in shorter):
        return False
    if longer.endswith(shorter) and not longer[-len(shorter) - 1].isalnum():
        return True
    return longer.startswith(shorter) and not longer[len(shorter)].isalnum()


class PhotoIndex:
    """Photo filenames (normalized, no extension) indexed the ways targets look them up."""

    def __init__(self, keys: list[str]) -> None:
        self.keys = keys
        self.canonical = {key: canonical(key) for key in keys}
        self.by_canonical: dict[str, list[str]] = {}
        self.by_number: dict[int, list[str]] = {}
        for key in keys:
            self.by_canonical.setdefault(self.canonical[key], []).append(key)
            number = frame_number(key)
            if number is not None:
                self.by_number.setdefault(number, []).append(key)

    def find(self, target: Target) -> list[str]:
        if target.number is not None:
            return self.by_number.get(target.number, [])
        if target.name in self.canonical:
            return [target.name]

        name = canonical(target.name)
        if name in self.by_canonical:
            return self.by_canonical[name]
        if not target.has_digit:
            return []
        return [key for key in self.keys if joined_at_boundary(self.canonical[key], name)]


def read_text_file(path: Path) -> str:
    """Read a TXT saved as UTF-8 or in the system's ANSI encoding (e.g. CP949)."""
    data = path.read_bytes()
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode(locale.getpreferredencoding(False), errors="replace")


def copy_target_photos(
    targets: list[Target], folder: Path, output_folder: Path, file_type: str = "all"
) -> TargetResult:
    """Refresh output_folder with one photo per filename the targets refer to.

    The folder's subfolders are searched too. A number can match several
    photos (e.g. IMG_0001 and DSC_0001). Returns how many photos were copied,
    how many targets were found, and which targets were not.
    """
    if not targets:
        raise ValueError(t("err_empty_list"))
    if file_type not in FILE_TYPES:
        raise ValueError(t("err_bad_type", types=", ".join(FILE_TYPES)))

    validate_output_folder(output_folder, (folder, t("photo_folder")))
    reset_output_folder(output_folder)

    photos = collect_photo_paths_by_stem(folder, FILE_TYPES[file_type])
    index = PhotoIndex(list(photos))
    to_copy: dict[str, None] = {}  # ordered set of photo keys
    found = 0
    missing = []
    for target in targets:
        matches = index.find(target)
        if matches:
            found += 1
            to_copy.update(dict.fromkeys(matches))
        elif target.has_digit:
            missing.append(target.text)

    for key in to_copy:
        photo_path = photos[key][0]
        shutil.copy2(photo_path, unique_destination(output_folder, photo_path.name))

    return TargetResult(copied=len(to_copy), found=found, missing=missing)
