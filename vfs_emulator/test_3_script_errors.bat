@echo off
chcp 65001 > nul
python main.py --vfs "C:\vfs\test_vfs.csv" --script "startup_error.txt"
python main.py --vfs "C:\vfs\test_vfs.csv" --script "not_found.txt"