"""User-facing text in English and Korean, plus the remembered language choice."""
from __future__ import annotations

import json
import locale
import os
import sys
from pathlib import Path


LANGUAGES = {"ko": "한국어", "en": "English"}

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "app_title": "Photo Selection",
        "app_subtitle": "Intersect folders, pull photos from a name list, and list folder contents.",
        "language": "Language",
        "tab_match": "Intersection",
        "tab_list": "File List",
        "browse": "Browse…",
        "save_as": "Save As…",
        "open_folder": "Open folder",
        "open_file": "Open file",
        "folder": "Folder",
        "folder_a": "Folder A",
        "folder_b": "Folder B",
        # Match Photos
        "match_description": (
            "Copies the photos whose filenames appear in both Folder A and Folder B "
            "(extensions are ignored)."
        ),
        "section_folders": "FOLDERS",
        "section_options": "OPTIONS",
        "folder_c_label": "Folder C (output)",
        "match_warning": "⚠  Everything already in Folder C is deleted before copying.",
        "source_label": "Copy files from",
        "file_type_label": "File types",
        "type_all": "All photos",
        "type_regular": "Regular photos only",
        "type_raw": "RAW only",
        "match_run": "Copy photos",
        "match_idle": "Choose the folders, then click Copy photos.",
        "match_busy": "Copying matching photos…",
        "need_three_folders": "Please choose all three folders.",
        "match_done": "Copied {count} matching photo(s) from Folder {source} to:\n{folder}",
        "match_done_status": "Done. Copied {count} matching photo(s) to Folder C.",
        "match_none": "No matching filenames found, so Folder C is empty.",
        # Find Targets
        "tab_target": "Find Targets",
        "target_description": (
            "Finds the photos a list refers to, by file name or just by number, in the "
            "photo folder (and its subfolders) and copies them to the output folder."
        ),
        "section_targets": "TARGET LIST",
        "load_txt": "Load TXT…",
        "clear": "Clear",
        "target_hint": (
            "Write file names or just numbers in any format: IMG_0001.JPG, 12 15, 20~25, "
            "one per line, tab-separated... Extensions and leading zeros are ignored."
        ),
        "name_count": "{count} target(s)",
        "photo_folder": "Photo folder",
        "output_folder": "Output folder",
        "target_warning": "⚠  Everything already in the output folder is deleted before copying.",
        "target_run": "Find & copy",
        "target_idle": "Enter the file names and folders, then click Find & copy.",
        "target_busy": "Finding and copying the listed photos…",
        "need_target_folders": "Please choose the photo folder and the output folder.",
        "target_done_status": "Done. Found all {found} target(s) and copied {count} photo(s).",
        "target_partial": (
            "Copied {count} photo(s). {missing_count} target(s) were not found: {names}"
        ),
        "target_none": "No photos in the photo folder match the list, so the output folder is empty.",
        "and_more": "{names} and {count} more",
        "copy_missing": "Copy missing names",
        "copied": "Copied",
        # File List
        "list_description": (
            "Saves a TXT list of every file in a folder and its subfolders, "
            "with the total count at the top."
        ),
        "section_locations": "LOCATIONS",
        "list_folder_label": "Folder to list",
        "list_output_label": "Save list as",
        "list_run": "Create list",
        "list_idle": "Choose a folder, then click Create list.",
        "list_busy": "Creating the file list…",
        "text_files": "Text files",
        "all_files": "All files",
        "need_folder": "Please choose a folder.",
        "list_done": "Listed {count} file(s) in:\n{file}",
        "list_done_status": "Done. Listed {count} file(s).",
        "list_header_folder": "Folder: {folder}",
        "list_header_total": "Total files: {count}",
        "list_header_created": "Created: {time}",
        "list_header_files": "Files:",
        # Errors
        "err_not_found": "{label} does not exist: {path}",
        "err_not_dir": "{label} is not a folder: {path}",
        "err_same_as_source": "Destination folder cannot be the same as {label}.",
        "err_contains_source": (
            "Destination folder cannot contain {label}. Choose a separate output folder."
        ),
        "err_dest_not_dir": "Destination is not a folder: {path}",
        "err_bad_source": "Source folder must be A or B.",
        "err_bad_type": "File type must be one of: {types}.",
        "err_empty_list": "The list has no file names or numbers.",
        # Terminal
        "prompt_folder_a": "Folder A path (photos)",
        "prompt_folder_b": "Folder B path (photos)",
        "prompt_folder_c": "Folder C path (output)",
        "prompt_source": "Copy matching files from folder (A or B)",
        "prompt_source_retry": "Please enter A or B.",
        "prompt_list_folder": "Folder path",
        "prompt_names": "File names or numbers (or the path of a TXT file with them)",
        "prompt_photo_folder": "Photo folder path",
        "prompt_output_folder": "Output folder path",
        "target_cli_done": "Found {found} target(s); copied {count} photo(s) to: {folder}",
        "target_cli_missing": "Not found ({count}):",
        "cli_error": "Error: {message}",
    },
    "ko": {
        "app_title": "사진 셀렉",
        "app_subtitle": "폴더 교집합, 목록으로 사진 찾기, 파일 목록 만들기를 한 곳에서 할 수 있습니다.",
        "language": "언어",
        "tab_match": "교집합",
        "tab_list": "파일 목록",
        "browse": "찾아보기...",
        "save_as": "저장 위치...",
        "open_folder": "폴더 열기",
        "open_file": "파일 열기",
        "folder": "폴더",
        "folder_a": "A 폴더",
        "folder_b": "B 폴더",
        # Match Photos
        "match_description": (
            "A 폴더와 B 폴더에 같은 이름으로 있는 사진을 C 폴더로 복사합니다 (확장자 무시)."
        ),
        "section_folders": "폴더",
        "section_options": "옵션",
        "folder_c_label": "C 폴더 (결과)",
        "match_warning": "⚠  복사 전에 C 폴더 안의 기존 파일이 모두 삭제됩니다.",
        "source_label": "복사할 원본 폴더",
        "file_type_label": "파일 형식",
        "type_all": "모든 사진",
        "type_regular": "일반 사진만",
        "type_raw": "RAW만",
        "match_run": "사진 복사",
        "match_idle": "폴더를 선택한 뒤 사진 복사를 누르세요.",
        "match_busy": "일치하는 사진을 복사하는 중...",
        "need_three_folders": "세 폴더를 모두 선택하세요.",
        "match_done": "{source} 폴더에서 일치하는 사진 {count}장을 복사했습니다:\n{folder}",
        "match_done_status": "완료. 일치하는 사진 {count}장을 C 폴더에 복사했습니다.",
        "match_none": "일치하는 파일 이름이 없어 C 폴더가 비어 있습니다.",
        # Find Targets
        "tab_target": "타겟 찾기",
        "target_description": (
            "목록에 적힌 파일 이름이나 번호로 사진 폴더(하위 폴더 포함)에서 사진을 찾아 "
            "결과 폴더로 복사합니다."
        ),
        "section_targets": "타겟 목록",
        "load_txt": "TXT 불러오기...",
        "clear": "지우기",
        "target_hint": (
            "파일 이름이나 번호만 자유롭게 적으세요: IMG_0001.JPG, 12 15, 20~25번, 줄바꿈, "
            "탭 구분 등. 확장자와 앞자리 0은 무시합니다."
        ),
        "name_count": "타겟 {count}개",
        "photo_folder": "사진 폴더",
        "output_folder": "결과 폴더",
        "target_warning": "⚠  복사 전에 결과 폴더 안의 기존 파일이 모두 삭제됩니다.",
        "target_run": "찾아서 복사",
        "target_idle": "파일 이름과 폴더를 입력한 뒤 찾아서 복사를 누르세요.",
        "target_busy": "목록의 사진을 찾아 복사하는 중...",
        "need_target_folders": "사진 폴더와 결과 폴더를 선택하세요.",
        "target_done_status": "완료. 타겟 {found}개를 모두 찾아 사진 {count}장을 복사했습니다.",
        "target_partial": (
            "사진 {count}장을 복사했습니다. 타겟 중 {missing_count}개는 찾지 못했습니다: {names}"
        ),
        "target_none": "목록과 일치하는 사진이 사진 폴더에 없어 결과 폴더가 비어 있습니다.",
        "and_more": "{names} 외 {count}개",
        "copy_missing": "누락 목록 복사",
        "copied": "복사됨",
        # File List
        "list_description": (
            "폴더와 하위 폴더의 모든 파일 목록을 전체 개수와 함께 TXT 파일로 저장합니다."
        ),
        "section_locations": "위치",
        "list_folder_label": "목록을 만들 폴더",
        "list_output_label": "저장할 TXT 파일",
        "list_run": "목록 만들기",
        "list_idle": "폴더를 선택한 뒤 목록 만들기를 누르세요.",
        "list_busy": "파일 목록을 만드는 중...",
        "text_files": "텍스트 파일",
        "all_files": "모든 파일",
        "need_folder": "폴더를 선택하세요.",
        "list_done": "파일 {count}개의 목록을 저장했습니다:\n{file}",
        "list_done_status": "완료. 파일 {count}개의 목록을 저장했습니다.",
        "list_header_folder": "폴더: {folder}",
        "list_header_total": "전체 파일 수: {count}",
        "list_header_created": "생성 시각: {time}",
        "list_header_files": "파일 목록:",
        # Errors
        "err_not_found": "{label}를 찾을 수 없습니다: {path}",
        "err_not_dir": "{label} 경로가 폴더가 아닙니다: {path}",
        "err_same_as_source": "결과 폴더는 {label}와 같을 수 없습니다.",
        "err_contains_source": (
            "결과 폴더 안에 {label}가 들어 있습니다. 별도의 결과 폴더를 선택하세요."
        ),
        "err_dest_not_dir": "결과 경로가 폴더가 아닙니다: {path}",
        "err_bad_source": "원본 폴더는 A 또는 B여야 합니다.",
        "err_bad_type": "파일 형식은 다음 중 하나여야 합니다: {types}.",
        "err_empty_list": "목록에서 파일 이름이나 번호를 찾지 못했습니다.",
        # Terminal
        "prompt_folder_a": "A 폴더 경로 (사진)",
        "prompt_folder_b": "B 폴더 경로 (사진)",
        "prompt_folder_c": "C 폴더 경로 (결과)",
        "prompt_source": "어느 폴더에서 복사할까요? (A 또는 B)",
        "prompt_source_retry": "A 또는 B를 입력하세요.",
        "prompt_list_folder": "폴더 경로",
        "prompt_names": "파일 이름 또는 번호 목록 (또는 목록 TXT 파일 경로)",
        "prompt_photo_folder": "사진 폴더 경로",
        "prompt_output_folder": "결과 폴더 경로",
        "target_cli_done": "타겟 {found}개를 찾아 사진 {count}장을 복사했습니다: {folder}",
        "target_cli_missing": "찾지 못한 이름 ({count}개):",
        "cli_error": "오류: {message}",
    },
}

SETTINGS_FILE = (
    Path(os.environ.get("APPDATA") or Path.home()) / "PhotoSelection" / "settings.json"
)

_language = "en"


def t(key: str, **values: object) -> str:
    return STRINGS[_language][key].format(**values)


def get_language() -> str:
    return _language


def set_language(language: str) -> None:
    global _language
    if language not in LANGUAGES:
        raise ValueError(f"Unknown language: {language}")
    _language = language


def system_language() -> str:
    if sys.platform == "win32":
        import ctypes

        # Primary language ID 0x12 is Korean.
        ui_language = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        return "ko" if ui_language & 0x3FF == 0x12 else "en"

    name = locale.getlocale()[0] or os.environ.get("LANG", "")
    return "ko" if name.lower().startswith(("ko", "korean")) else "en"


def load_language() -> str:
    """The language saved from the app window, else the system's language."""
    try:
        saved = json.loads(SETTINGS_FILE.read_text(encoding="utf-8")).get("language")
    except (OSError, ValueError, AttributeError):
        saved = None
    return saved if saved in LANGUAGES else system_language()


def save_language(language: str) -> None:
    try:
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS_FILE.write_text(json.dumps({"language": language}), encoding="utf-8")
    except OSError:
        pass  # Not remembering the choice is fine; the app still works.
