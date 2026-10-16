# Photo Selection

One app with two tools:

- **Match Photos**: copy the photos whose filenames exist in both Folder A and
  Folder B into Folder C.
- **File List**: save a `.txt` list of every file in a folder, with the total
  count at the top.

## Download (no Python needed)

The ready-to-run Windows app is in the `dist` folder:
[`dist/PhotoSelection.exe`](dist/PhotoSelection.exe). Download it and
double-click it; nothing else needs to be installed.

Windows may show "Windows protected your PC" the first time, because the app is
not code-signed. Click **More info** → **Run anyway**.

## Run the app

Double-click `dist/PhotoSelection.exe`, or `run_photo_selection.bat` to run
from source with Python. Pick a tool at the top (Match Photos or
File List), choose folders with the Browse buttons, then click **Copy photos**
or **Create list**. Progress and the result appear at the bottom of the window,
and the window stays responsive while large folders are copied. When a run
finishes, **Open folder** / **Open file** shows the result.

Running from source requires Python 3.9+ with Tkinter (included in the
standard Windows installer).

### Language / 언어

The app is available in Korean (한국어) and English. It opens in Korean when
Windows is set to Korean and in English otherwise. Switch with the language
box at the top right; the choice is remembered (saved in
`%APPDATA%\PhotoSelection\settings.json`).

## Match Photos

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

## File List

Choose a folder and where to save the TXT file (defaults to
`<folder>_file_list.txt` next to the folder). The file contains the folder
path, the total file count, the created time, and every file in the folder and
its subfolders.

## Run from the terminal

```powershell
python main.py match "C:\folder A" "C:\folder B" "C:\folder C" --source B --type regular
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
    intersection.py        Match Photos logic
    file_list.py           File List logic
    paths.py               shared path helpers
    i18n.py                Korean / English text and the saved language choice
    theme.py               colors, fonts, widget styles, and the logo
    gui.py                 Tkinter window (header, one page per tool)
    cli.py                 terminal commands
```
