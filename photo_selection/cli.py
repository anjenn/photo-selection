from __future__ import annotations

import argparse
from pathlib import Path

from .file_list import default_output_path, write_file_list
from .i18n import LANGUAGES, load_language, set_language, t
from .intersection import FILE_TYPES, copy_photo_intersection
from .paths import clean_path, validate_folder


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Photo Selection tools. Run with no arguments to open the app window."
    )
    parser.add_argument(
        "--lang",
        choices=tuple(LANGUAGES),
        help="language for this run (default: the one chosen in the app, else the system's)",
    )
    commands = parser.add_subparsers(dest="command", metavar="command")

    match = commands.add_parser(
        "match",
        help="copy photos whose filenames exist in both folder A and folder B",
        description=(
            "Empty folder C, then copy one photo per filename found in both folder A "
            "and folder B. Names match even if extensions differ. Missing arguments "
            "are asked for in the terminal."
        ),
    )
    match.add_argument("folder_a", nargs="?", help="folder A containing photos")
    match.add_argument("folder_b", nargs="?", help="folder B containing photos")
    match.add_argument("output_folder", nargs="?", help="folder C to create/refresh")
    match.add_argument(
        "--source",
        type=str.upper,
        choices=("A", "B"),
        help="copy matching files from folder A or folder B",
    )
    match.add_argument(
        "--type",
        dest="file_type",
        type=str.lower,
        choices=tuple(FILE_TYPES),
        default="all",
        help="file types to copy from the source folder (default: all)",
    )

    file_list = commands.add_parser(
        "list",
        help="write a TXT list of every file in a folder",
        description=(
            "Write a TXT list of every file in a folder and its subfolders, "
            "with the total count at the top."
        ),
    )
    file_list.add_argument("folder", nargs="?", help="folder containing files to list")
    file_list.add_argument(
        "output_file",
        nargs="?",
        help="TXT file to create (default: <folder>_file_list.txt next to the folder)",
    )

    return parser


def ask_for_path(label: str, current_value: str | None) -> Path:
    if current_value:
        return clean_path(current_value)

    return clean_path(input(f"{label}: "))


def ask_for_source(current_value: str | None) -> str:
    if current_value:
        return current_value

    while True:
        source = input(f"{t('prompt_source')}: ").strip().upper()
        if source in {"A", "B"}:
            return source
        print(t("prompt_source_retry"))


def run_match(args: argparse.Namespace) -> None:
    folder_a = ask_for_path(t("prompt_folder_a"), args.folder_a)
    folder_b = ask_for_path(t("prompt_folder_b"), args.folder_b)
    output_folder = ask_for_path(t("prompt_folder_c"), args.output_folder)
    source = ask_for_source(args.source)

    validate_folder(folder_a, t("folder_a"))
    validate_folder(folder_b, t("folder_b"))

    copied = copy_photo_intersection(folder_a, folder_b, output_folder, source, args.file_type)
    print(t("match_done", count=copied, source=source, folder=output_folder))


def run_list(args: argparse.Namespace) -> None:
    folder = ask_for_path(t("prompt_list_folder"), args.folder)
    output_file = (
        clean_path(args.output_file) if args.output_file else default_output_path(folder)
    )

    validate_folder(folder, t("folder"))

    total = write_file_list(folder, output_file)
    print(t("list_done", count=total, file=output_file))


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    set_language(args.lang or load_language())

    if args.command is None:
        # Imported here so the terminal commands work without Tkinter.
        from .gui import run_gui

        run_gui()
        return

    try:
        if args.command == "match":
            run_match(args)
        else:
            run_list(args)
    except (OSError, ValueError) as error:
        raise SystemExit(t("cli_error", message=error)) from error
