@echo off
chcp 65001 > nul
python "%~dp0src\main.py" --vfs "%~dp0tests\vfs_deep.csv"