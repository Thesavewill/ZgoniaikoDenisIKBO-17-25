"""Точка входа в эмулятор командной строки ОС."""

import argparse
import sys

from PyQt6.QtWidgets import QApplication

from gui import ShellEmulatorWindow


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    """Разбирает аргументы командной строки эмулятора."""
    parser = argparse.ArgumentParser(
        description="Эмулятор языка оболочки ОС"
    )
    parser.add_argument(
        "-v",
        "--vfs",
        type=str,
        default=None,
        help="Путь к физическому расположению VFS",
    )
    parser.add_argument(
        "-s",
        "--script",
        type=str,
        default=None,
        help="Путь к стартовому скрипту",
    )
    return parser.parse_known_args()


def main() -> None:
    """Создает приложение PyQt6 и открывает окно эмулятора."""
    cli_args, qt_args = parse_args()
    app = QApplication([sys.argv[0], *qt_args])
    window = ShellEmulatorWindow(
        vfs_path=cli_args.vfs,
        script_path=cli_args.script,
    )
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()