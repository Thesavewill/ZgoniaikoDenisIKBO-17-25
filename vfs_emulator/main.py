import argparse
import base64
import binascii
import csv
import shlex
import sys
from pathlib import Path, PurePosixPath

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class VFSNode:
    def __init__(
        self,
        name: str,
        node_type: str,
        content: bytes = b"",
    ) -> None:
        self.name = name
        self.node_type = node_type
        self.content = content
        self.children: dict[str, VFSNode] = {}


class VirtualFileSystem:
    def __init__(self) -> None:
        self.root = VFSNode("/", "dir")
        self.is_loaded = False

    def load_from_csv(self, file_path: str) -> None:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"файл '{file_path}' не найден.")

        new_root = VFSNode("/", "dir")

        try:
            with path.open("r", encoding="utf-8", newline="") as csv_file:
                reader = csv.reader(csv_file)
                header = next(reader, None)
                if header != ["path", "type", "content"]:
                    raise ValueError(
                        "неверный заголовок CSV "
                        "(ожидается: path,type,content)."
                    )

                for line_num, row in enumerate(reader, start=2):
                    if len(row) != 3:
                        raise ValueError(
                            f"строка {line_num}: ожидается 3 столбца."
                        )
                    raw_path, node_type, b64_content = row
                    self._insert_node(
                        new_root,
                        raw_path.strip(),
                        node_type.strip(),
                        b64_content.strip(),
                        line_num,
                    )
        except csv.Error as err:
            raise ValueError(f"ошибка чтения CSV: {err}") from err
        except UnicodeDecodeError as err:
            raise ValueError("файл должен быть в кодировке UTF-8.") from err

        self.root = new_root
        self.is_loaded = True

    def _insert_node(
        self,
        root: VFSNode,
        raw_path: str,
        node_type: str,
        b64_content: str,
        line_num: int,
    ) -> None:
        if not raw_path.startswith("/"):
            raise ValueError(
                f"строка {line_num}: путь '{raw_path}' "
                "должен начинаться с '/'."
            )

        if node_type not in ("dir", "file"):
            raise ValueError(
                f"строка {line_num}: неизвестный тип '{node_type}'."
            )

        if node_type == "dir":
            if b64_content:
                raise ValueError(
                    f"строка {line_num}: у папки не может быть контента."
                )
            content_bytes = b""
        else:
            try:
                content_bytes = base64.b64decode(
                    b64_content.encode("ascii"),
                    validate=True,
                )
            except (binascii.Error, UnicodeEncodeError) as err:
                raise ValueError(
                    f"строка {line_num}: некорректные данные base64."
                ) from err

        posix_path = PurePosixPath(raw_path)
        parts = [p for p in posix_path.parts if p != "/"]
        if not parts:
            return

        current = root
        for part in parts[:-1]:
            if part not in current.children:
                current.children[part] = VFSNode(part, "dir")
            elif current.children[part].node_type != "dir":
                raise ValueError(
                    f"строка {line_num}: '{part}' является файлом, "
                    "а не папкой."
                )
            current = current.children[part]

        target_name = parts[-1]
        if target_name in current.children:
            existing = current.children[target_name]
            if existing.node_type != node_type:
                raise ValueError(
                    f"строка {line_num}: конфликт типов для '{raw_path}'."
                )
            existing.content = content_bytes
        else:
            current.children[target_name] = VFSNode(
                target_name,
                node_type,
                content_bytes,
            )

    def save_to_csv(self, target_path: str) -> None:
        if not self.is_loaded:
            raise RuntimeError("VFS не загружена в память.")

        rows: list[list[str]] = [["path", "type", "content"]]
        self._collect_rows(self.root, PurePosixPath("/"), rows)

        out_path = Path(target_path)
        with out_path.open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(rows)

    def _collect_rows(
        self,
        node: VFSNode,
        current_path: PurePosixPath,
        rows: list[list[str]],
    ) -> None:
        for name, child in sorted(node.children.items()):
            child_path = current_path / name
            b64_str = ""
            if child.node_type == "file":
                b64_str = base64.b64encode(child.content).decode("ascii")
            rows.append([str(child_path), child.node_type, b64_str])
            if child.node_type == "dir":
                self._collect_rows(child, child_path, rows)

    def get_motd(self) -> str | None:
        motd_node = self.root.children.get("motd")
        if motd_node and motd_node.node_type == "file":
            return motd_node.content.decode("utf-8", errors="replace")
        return None


class ShellEmulatorWindow(QMainWindow):
    def __init__(
        self,
        vfs_path: str | None = None,
        script_path: str | None = None,
    ) -> None:
        super().__init__()
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.vfs_name = Path(vfs_path).name if vfs_path else "default_vfs"
        self.vfs = VirtualFileSystem()

        self.setWindowTitle(f"VFS Emulator — [{self.vfs_name}]")
        self.resize(1000, 500)

        self._setup_ui()
        self._apply_styles()
        self._print_debug_config()
        self._init_vfs()
        self._print_welcome()

        if self.script_path:
            QTimer.singleShot(0, self._run_startup_script)

    def _setup_ui(self) -> None:
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        font = QFont("Consolas", 11)

        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        self.output_area.setFont(font)
        main_layout.addWidget(self.output_area)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(5)

        prompt_font = QFont("Consolas", 11)
        prompt_font.setBold(True)

        self.prompt_label = QLabel(f"user@{self.vfs_name}:~$ ", self)
        self.prompt_label.setFont(prompt_font)
        input_layout.addWidget(self.prompt_label)

        self.input_entry = QLineEdit(self)
        self.input_entry.setFont(font)
        self.input_entry.returnPressed.connect(self._on_enter)
        input_layout.addWidget(self.input_entry)

        main_layout.addLayout(input_layout)
        self.input_entry.setFocus()

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background-color: #1e1e1e;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
            }
            QLabel {
                color: #4ec9b0;
            }
            QLineEdit {
                color: #ffffff;
                border-radius: 3px;
                padding: 2px;
            }
            """
        )

    def _print_debug_config(self) -> None:
        vfs_val = self.vfs_path if self.vfs_path else "не задан"
        script_val = self.script_path if self.script_path else "не задан"
        self.write_output(
            "Заданные параметры при запуске:\n"
            f"  Путь к VFS (--vfs): {vfs_val}\n"
            f"  Путь к стартовому скрипту (--script): {script_val}\n"
            + "-" * 80
        )

    def _init_vfs(self) -> None:
        if not self.vfs_path:
            return

        try:
            self.vfs.load_from_csv(self.vfs_path)
            self.write_output(
                f"VFS '{self.vfs_name}' успешно загружена в память."
            )
            motd_text = self.vfs.get_motd()
            if motd_text is not None:
                self.write_output(f"[MOTD] {motd_text}")
        except FileNotFoundError as err:
            self.write_output(f"Ошибка загрузки VFS: {err}")
        except ValueError as err:
            self.write_output(
                f"Ошибка загрузки VFS (неверный формат): {err}"
            )
        except OSError as err:
            self.write_output(f"Ошибка чтения файла VFS: {err}")

        self.write_output("-" * 80)

    def _print_welcome(self) -> None:
        self.write_output(
            f"Эмулятор оболочки запущен. Имя VFS: {self.vfs_name}\n"
            "Доступные команды: ls, cd, vfs-save, exit.\n"
            + "-" * 80
        )

    def _run_startup_script(self) -> None:
        if not self.script_path:
            return

        path = Path(self.script_path)
        if not path.is_file():
            self.write_output(
                "Ошибка исполнения стартового скрипта: "
                f"файл '{self.script_path}' не найден."
            )
            return

        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as err:
            self.write_output(
                f"Ошибка чтения стартового скрипта: {err}"
            )
            return

        prompt = self.prompt_label.text()
        for line_num, raw_line in enumerate(lines, start=1):
            command = raw_line.strip()
            if not command:
                continue

            self.write_output(f"{prompt}{command}")
            if not self.execute_command(command):
                self.write_output(
                    "Ошибка во время исполнения стартового скрипта "
                    f"(строка {line_num}): выполнение остановлено."
                )
                break

    def write_output(self, text: str) -> None:
        self.output_area.append(text)
        scrollbar = self.output_area.verticalScrollBar()
        if scrollbar is not None:
            scrollbar.setValue(scrollbar.maximum())

    def _on_enter(self) -> None:
        raw_command = self.input_entry.text()
        self.input_entry.clear()

        prompt = self.prompt_label.text()
        self.write_output(f"{prompt}{raw_command}")

        if not raw_command.strip():
            return

        self.execute_command(raw_command)

    def execute_command(self, raw_command: str) -> bool:
        try:
            tokens = shlex.split(raw_command)
        except ValueError as err:
            self.write_output(
                f"Ошибка синтаксиса (неверные кавычки): {err}"
            )
            return False

        if not tokens:
            return True

        cmd_name = tokens[0]
        args = tokens[1:]

        if cmd_name == "exit":
            if args:
                self.write_output(
                    "Ошибка: exit: слишком много аргументов."
                )
                return False
            self.close()
            return True

        if cmd_name == "ls":
            return self._cmd_ls(args)

        if cmd_name == "cd":
            return self._cmd_cd(args)

        if cmd_name == "vfs-save":
            return self._cmd_vfs_save(args)

        self.write_output(f"Ошибка: команда '{cmd_name}' не найдена.")
        return False

    def _cmd_ls(self, args: list[str]) -> bool:
        valid_flags = ("-l", "-a", "-la", "-al")
        for arg in args:
            if arg.startswith("-") and arg not in valid_flags:
                self.write_output(
                    f"Ошибка: ls: неверный ключ '{arg}'."
                )
                return False

        self.write_output(f"[Заглушка] Команда: 'ls', Аргументы: {args}")
        return True

    def _cmd_cd(self, args: list[str]) -> bool:
        if len(args) > 1:
            self.write_output(
                "Ошибка: cd: слишком много аргументов."
            )
            return False

        self.write_output(f"[Заглушка] Команда: 'cd', Аргументы: {args}")
        return True

    def _cmd_vfs_save(self, args: list[str]) -> bool:
        if len(args) != 1:
            self.write_output(
                "Ошибка: vfs-save: укажите ровно один путь к файлу."
            )
            return False

        target_path = args[0]
        try:
            self.vfs.save_to_csv(target_path)
        except (RuntimeError, OSError) as err:
            self.write_output(f"Ошибка сохранения VFS: {err}")
            return False

        self.write_output(
            f"Состояние VFS успешно сохранено в '{target_path}'."
        )
        return True


def parse_args() -> tuple[argparse.Namespace, list[str]]:
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