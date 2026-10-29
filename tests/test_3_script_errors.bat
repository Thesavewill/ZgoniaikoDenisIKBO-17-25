@echo off
chcp 65001 > nul
python "%~dp0..\src\main.py" --vfs "%~dp0vfs_files.csv" --script "%~dp0startup_error.txt"
python "%~dp0..\src\main.py" --vfs "%~dp0vfs_files.csv" --script "%~dp0not_found.txt"