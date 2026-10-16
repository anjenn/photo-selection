# Photo Selection

One app with three tools:

- **Intersection (교집합)**: copy the photos whose filenames exist in both
  Folder A and Folder B into Folder C.
- **Find Targets (타겟 찾기)**: paste a client's selection (file names, or just
  numbers like `12 15 20~25`) and copy those photos out of a folder.
- **File List (파일 목록)**: save a `.txt` list of every file in a folder, with
  the total count at the top.

## Download (no Python needed)

The ready-to-run Windows app is in the `dist` folder:
[`dist/PhotoSelection.exe`](dist/PhotoSelection.exe). Download it and
double-click it; nothing else needs to be installed.

Windows may show "Windows protected your PC" the first time, because the app is
not code-signed. Click **More info** → **Run anyway**.

## Run the app

Double-click `dist/PhotoSelection.exe`, or `run_photo_selection.bat` to run
from source with Python. Pick a tool at the top, fill in the
folders with the Browse buttons, then click the blue button (**Copy photos**,
**Find & copy**, or **Create list**). Progress and the result appear at the bottom of the window,
and the window stays responsive while large folders are copied. When a run
finishes, **Open folder** / **Open file** shows the result.

Running from source requires Python 3.9+ with Tkinter (included in the
standard Windows installer).

### Language / 언어

The app is available in Korean (한국어) and English. It opens in Korean when
Windows is set to Korean and in English otherwise. Switch with the language
box at the top right; the choice is remembered (saved in
`%APPDATA%\PhotoSelection\settings.json`).

## Intersection (교집합)

Files match when their names match, ignoring uppercase/lowercase and the
extension. For example, `IMG_001.CR2` in Folder A matches `IMG_001.JPG` in
Folder B.

- **Copy matching files from**: choose whether the copies come from Folder A or
  Folder B.
- **File types to copy**: `All photos`, `Regular photos only`, or `RAW only`.
  Use `Regular photos only` when the source folder holds both RAW and JPEG
  versions of each shot and you only want the JPEGs.

Recognized photo files (other files are ignored):

| Group | Extensions |
| --- | --- |
| RAW | `.3fr .arw .cr2 .cr3 .crw .dcr .dng .erf .fff .iiq .kdc .mef .mos .mrw .nef .nrw .orf .pef .raf .raw .rwl .rw2 .sr2 .srf .srw .x3f` |
| Regular photos (일반 사진) | `.jpg .jpeg .hif .heif .heic .tif .tiff` |

One file is copied per matching name. **Folder C is emptied first**, so pick a
separate output folder (the app refuses to use Folder A or B, or a folder that
contains them).

Example: Folder A has your culled `.CR2` files, Folder B has every `.JPG`, and
you copy from Folder B. Folder C ends up with only the JPGs you kept.

## Find Targets (타겟 찾기)

Paste the list into the box, or click **Load TXT…**. Then choose the photo
folder to search (subfolders included) and the output folder. The list can be
in any format, the way clients actually send it:

| You write | It finds |
| --- | --- |
| `IMG_0001.JPG, img_2.png` | `IMG_0001.*`, `IMG_0002.*` (extension and leading zeros ignored) |
| `1 2 3`, `1, 2`, one per line, tab-separated, `1/2/3` | the photos numbered 1, 2, 3 |
| `12번 15장`, `#7`, `(8)` | 12, 15, 7, 8 |
| `20~25`, `20-25` | 20 through 25 |
| `2637` | `260913_히나2637.JPG`, `IMG_2637.CR2`, … |
| `studio-IMG_0001` | `IMG_0001.*` |
| a File List TXT | every file it lists |

- A **number** matches a photo's frame number: the last number in its name,
  ignoring leading zeros and copy suffixes like `-2` or `(2)`. If two cameras
  both have frame 1 (`IMG_0001`, `DSC_0001`), both are copied.
- **Words** without digits (greetings, "사진", "jpg") are ignored unless a
  photo has exactly that name.
- Targets that match nothing are listed after the run. **Copy missing names**
  puts them on the clipboard so you can send them back to the client.
- **File types to copy** works as in Intersection, and **the output folder is
  emptied first**.
- TXT files can be UTF-8 or ANSI/CP949 (what older Korean Notepad saves).

## File List (파일 목록)

Choose a folder and where to save the TXT file (defaults to
`<folder>_file_list.txt` next to the folder). The file contains the folder
path, the total file count, the created time, and every file in the folder and
its subfolders.

## Run from the terminal

```powershell
python main.py match "C:\folder A" "C:\folder B" "C:\folder C" --source B --type regular
python main.py target "12 15 20~25" "C:\photos" "C:\selected" --type regular
python main.py target "C:\client_list.txt" "C:\photos" "C:\selected"
python main.py list "C:\folder" "C:\folder_file_list.txt"
```

Leave out any path and it is asked for in the terminal. Add `--lang ko` or
`--lang en` before the command to pick the language for that run (for example
`python main.py --lang en list ...`). See `python main.py match --help` for all
options.

## Build the .exe

```powershell
pip install pyinstaller
pyinstaller PhotoSelection.spec
```

The app is written to `dist/PhotoSelection.exe`. That file is committed so it
can be downloaded straight from GitHub, so rebuild and commit it whenever the
code changes.

## Project layout

```text
main.py                    entry point: opens the app, or runs a terminal command
run_photo_selection.bat    double-click launcher
PhotoSelection.spec        PyInstaller build config
dist/PhotoSelection.exe    ready-to-run app (no Python needed)
photo_selection/
    intersection.py        Intersection logic and shared photo helpers
    targets.py             Find Targets: list parsing and matching
    file_list.py           File List logic
    paths.py               shared path helpers
    i18n.py                Korean / English text and the saved language choice
    theme.py               colors, fonts, widget styles, and the logo
    gui.py                 Tkinter window (header, one page per tool)
    cli.py                 terminal commands
```
