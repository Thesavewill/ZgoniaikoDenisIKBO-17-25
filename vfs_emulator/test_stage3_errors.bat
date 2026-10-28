@echo off
chcp 65001 > nul
python main.py --vfs "missing_vfs.csv"
python main.py --vfs "vfs_broken.csv"