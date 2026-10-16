# Photo Selection

One app with two tools:

- **Match Photos**: copy the photos whose filenames exist in both Folder A and
  Folder B into Folder C.
- **File List**: save a `.txt` list of every file in a folder, with the total
  count at the top.

## Run the app

Double-click `run_photo_selection.bat` (or `PhotoSelection.exe` if you built
it), pick a tab, choose folders with the Browse buttons, then click Run.

Requires Python 3.9+ with Tkinter (included in the standard Windows installer).

## Match Photos

Files match when their names match, ignoring uppercase/lowercase and the
extension. For example, `IMG_001.CR2` in Folder A matches `IMG_001.JPG` in
Folder B.

- **Copy matching files from**: choose whether the copies come from Folder A or
  Folder B.
- **File types to copy**: `All photos`, `JPEG only`, or `RAW only`. Use
  `JPEG only` when the source folder holds both RAW and JPEG versions of each
  shot and you only want the JPEGs.

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
python main.py match "C:\folder A" "C:\folder B" "C:\folder C" --source B --type jpeg
python main.py list "C:\folder" "C:\folder_file_list.txt"
```

Leave out any path and it is asked for in the terminal. See
`python main.py match --help` for all options.

## Build the .exe

```powershell
pip install pyinstaller
pyinstaller PhotoSelection.spec
```

The app is written to `dist/PhotoSelection.exe`.

## Project layout

```text
main.py                    entry point: opens the app, or runs a terminal command
run_photo_selection.bat    double-click launcher
PhotoSelection.spec        PyInstaller build config
photo_selection/
    intersection.py        Match Photos logic
    file_list.py           File List logic
    paths.py               shared path helpers
    gui.py                 Tkinter window (one tab per tool)
    cli.py                 terminal commands
```
