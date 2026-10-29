@echo off
chcp 65001 > nul
python "%~dp0..\src\main.py" --vfs "%~dp0missing_vfs.csv"
python "%~dp0..\src\main.py" --vfs "%~dp0vfs_broken.csv"