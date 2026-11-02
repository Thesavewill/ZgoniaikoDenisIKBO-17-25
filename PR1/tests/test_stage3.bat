@echo off
chcp 65001 > nul
cd /d "%~dp0"

python "..\src\main.py" --vfs "vfs_min.csv"
python "..\src\main.py" --vfs "vfs_files.csv"
python "..\src\main.py" --vfs "vfs_deep.csv" --script "startup_stage3.txt"
python "..\src\main.py" --vfs "missing_vfs.csv"
python "..\src\main.py" --vfs "vfs_broken.csv"