@echo off
chcp 65001 > nul
python "%~dp0..\src\main.py" --vfs "%~dp0vfs_min.csv"
python "%~dp0..\src\main.py" --vfs "%~dp0vfs_files.csv"
python "%~dp0..\src\main.py" --vfs "%~dp0vfs_deep.csv" --script "%~dp0startup_stage3.txt"