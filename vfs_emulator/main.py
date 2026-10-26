import shlex
import sys

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


class ShellEmulatorWindow(QMainWindow):
    def __init__(self, vfs_name: str = "default_vfs") -> None:
        super().__init__()
        self.vfs_name = vfs_name
        self.setWindowTitle(f"VFS Emulator — [{self.vfs_name}]")
        self.resize(1000, 500)

        self._setup_ui()
        self._apply_styles()
        self._print_welcome()

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

    def _print_welcome(self) -> None:
        self.write_output(
            f"Эмулятор оболочки запущен. Имя VFS: {self.vfs_name}\n"
            "Доступные команды: ls, cd, exit.\n"
            + "-" * 80
        )

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


def main() -> None:
    app = QApplication(sys.argv)
    window = ShellEmulatorWindow(vfs_name="my_vfs")
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()