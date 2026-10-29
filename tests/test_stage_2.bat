@echo off
chcp 65001 > nul
cd /d "%~dp0"

python "..\src\main.py" --vfs "vfs_min.csv"
python "..\src\main.py" --vfs "vfs_files.csv" --script "startup_ok.txt"
python "..\src\main.py" --vfs "vfs_files.csv" --script "startup_error.txt"
python "..\src\main.py" --vfs "vfs_files.csv" --script "not_found.txt"