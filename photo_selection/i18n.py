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
        "language": "Language",
        "tab_match": "Match Photos",
        "tab_list": "File List",
        "browse": "Browse",
        "save_as": "Save As",
        "run": "Run",
        "done_title": "Done",
        "error_title": "Error",
        "failed_status": "Could not finish. Check the folder paths.",
        "folder": "Folder",
        "folder_a": "Folder A",
        "folder_b": "Folder B",
        # Match Photos
        "match_idle": "Choose folders, then click Run. Folder C is emptied before copying.",
        "match_busy": "Copying matching photos...",
        "folder_a_label": "Folder A - photos",
        "folder_b_label": "Folder B - photos",
        "folder_c_label": "Folder C - output",
        "source_label": "Copy matching files from",
        "file_type_label": "File types to copy",
        "type_all": "All photos",
        "type_regular": "Regular photos only",
        "type_raw": "RAW only",
        "need_three_folders": "Please choose all three folders.",
        "match_done": "Copied {count} matching photo(s) from Folder {source} to:\n{folder}",
        "match_done_status": "Done. Copied {count} matching photo(s).",
        # File List
        "list_idle": "Choose a folder, then click Run.",
        "list_busy": "Creating TXT file list...",
        "list_folder_label": "Folder - files to list",
        "list_output_label": "Output TXT file",
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
        # Terminal
        "prompt_folder_a": "Folder A path (photos)",
        "prompt_folder_b": "Folder B path (photos)",
        "prompt_folder_c": "Folder C path (output)",
        "prompt_source": "Copy matching files from folder (A or B)",
        "prompt_source_retry": "Please enter A or B.",
        "prompt_list_folder": "Folder path",
        "cli_error": "Error: {message}",
    },
    "ko": {
        "app_title": "사진 셀렉",
        "language": "언어",
        "tab_match": "사진 매칭",
        "tab_list": "파일 목록",
        "browse": "찾아보기",
        "save_as": "저장 위치",
        "run": "실행",
        "done_title": "완료",
        "error_title": "오류",
        "failed_status": "완료하지 못했습니다. 폴더 경로를 확인하세요.",
        "folder": "폴더",
        "folder_a": "A 폴더",
        "folder_b": "B 폴더",
        # Match Photos
        "match_idle": "폴더를 선택한 뒤 실행을 누르세요. 복사 전에 C 폴더는 비워집니다.",
        "match_busy": "일치하는 사진을 복사하는 중...",
        "folder_a_label": "A 폴더 - 사진",
        "folder_b_label": "B 폴더 - 사진",
        "folder_c_label": "C 폴더 - 결과",
        "source_label": "복사할 원본 폴더",
        "file_type_label": "복사할 파일 형식",
        "type_all": "모든 사진",
        "type_regular": "일반 사진만",
        "type_raw": "RAW만",
        "need_three_folders": "세 폴더를 모두 선택하세요.",
        "match_done": "{source} 폴더에서 일치하는 사진 {count}장을 복사했습니다:\n{folder}",
        "match_done_status": "완료. 일치하는 사진 {count}장을 복사했습니다.",
        # File List
        "list_idle": "폴더를 선택한 뒤 실행을 누르세요.",
        "list_busy": "TXT 파일 목록을 만드는 중...",
        "list_folder_label": "목록을 만들 폴더",
        "list_output_label": "저장할 TXT 파일",
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
        # Terminal
        "prompt_folder_a": "A 폴더 경로 (사진)",
        "prompt_folder_b": "B 폴더 경로 (사진)",
        "prompt_folder_c": "C 폴더 경로 (결과)",
        "prompt_source": "어느 폴더에서 복사할까요? (A 또는 B)",
        "prompt_source_retry": "A 또는 B를 입력하세요.",
        "prompt_list_folder": "폴더 경로",
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
