@echo off
chcp 65001 > nul
python main.py --vfs "vfs_min.csv"
python main.py --vfs "vfs_files.csv"
python main.py --vfs "vfs_deep.csv" --script "startup_stage3.txt"