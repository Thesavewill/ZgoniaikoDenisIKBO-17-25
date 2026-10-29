"""Модуль графического интерфейса и обработчика команд эмулятора."""

from pathlib import Path
import shlex

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from vfs import VirtualFileSystem

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 500
FONT_SIZE = 11
LAYOUT_MARGIN = 10
MAIN_SPACING = 8
INPUT_SPACING = 5
DIVIDER_LENGTH = 80
STARTUP_DELAY_MS = 0
MAX_CD_ARGS = 1
REQUIRED_SAVE_ARGS = 1
FIRST_SCRIPT_LINE = 1


class ShellEmulatorWindow(QMainWindow):
    """Главное окно эмулятора командной строки UNIX-подобной ОС."""

    def __init__(
        self,
        vfs_path: str | None = None,
        script_path: str | None = None,
    ) -> None:
        """Инициализирует окно приложения, VFS и стартовый скрипт."""
        super().__init__()
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.vfs_name = Path(vfs_path).name if vfs_path else "default_vfs"
        self.vfs = VirtualFileSystem()

        self.setWindowTitle(f"VFS Emulator — [{self.vfs_name}]")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self._setup_ui()
        self._apply_styles()
        self._print_debug_config()
        self._init_vfs()
        self._print_welcome()

        if self.script_path:
            QTimer.singleShot(STARTUP_DELAY_MS, self._run_startup_script)

    def _setup_ui(self) -> None:
        """Создает основную компоновку виджетов окна."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(
            LAYOUT_MARGIN, LAYOUT_MARGIN, LAYOUT_MARGIN, LAYOUT_MARGIN
        )
        main_layout.setSpacing(MAIN_SPACING)

        font = QFont("Consolas", FONT_SIZE)
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        self.output_area.setFont(font)
        main_layout.addWidget(self.output_area)

        input_layout = self._create_input_layout(font)
        main_layout.addLayout(input_layout)
        self.input_entry.setFocus()

    def _create_input_layout(self, font: QFont) -> QHBoxLayout:
        """Создает нижнюю панель с приглашением к вводу и полем строки."""
        input_layout = QHBoxLayout()
        input_layout.setSpacing(INPUT_SPACING)

        prompt_font = QFont("Consolas", FONT_SIZE)
        prompt_font.setBold(True)

        self.prompt_label = QLabel(f"user@{self.vfs_name}:~$ ", self)
        self.prompt_label.setFont(prompt_font)
        input_layout.addWidget(self.prompt_label)

        self.input_entry = QLineEdit(self)
        self.input_entry.setFont(font)
        self.input_entry.returnPressed.connect(self._on_enter)
        input_layout.addWidget(self.input_entry)
        return input_layout

    def _apply_styles(self) -> None:
        """Применяет таблицу стилей к элементам окна."""
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
        """Выводит отладочную информацию о параметрах запуска."""
        vfs_val = self.vfs_path if self.vfs_path else "не задан"
        script_val = self.script_path if self.script_path else "не задан"
        self.write_output(
            "[DEBUG] Заданные параметры при запуске:\n"
            f"  Путь к VFS (--vfs): {vfs_val}\n"
            f"  Путь к стартовому скрипту (--script): {script_val}\n"
            + "-" * DIVIDER_LENGTH
        )

    def _init_vfs(self) -> None:
        """Загружает VFS из файла и выводит сообщение motd при наличии."""
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

        self.write_output("-" * DIVIDER_LENGTH)

    def _print_welcome(self) -> None:
        """Выводит приветственную подсказку со списком команд."""
        self.write_output(
            f"Эмулятор оболочки запущен. Имя VFS: {self.vfs_name}\n"
            "Доступные команды: ls, cd, vfs-save, exit.\n"
            + "-" * DIVIDER_LENGTH
        )

    def _run_startup_script(self) -> None:
        """Читает стартовый скрипт и запускает построчное выполнение."""
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
            self.write_output(f"Ошибка чтения стартового скрипта: {err}")
            return

        self._execute_script_lines(lines)

    def _execute_script_lines(self, lines: list[str]) -> None:
        """Выполняет команды скрипта до первой ошибки."""
        prompt = self.prompt_label.text()
        for line_num, raw_line in enumerate(lines, start=FIRST_SCRIPT_LINE):
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
        """Добавляет текст в поле вывода и прокручивает историю вниз."""
        self.output_area.append(text)
        scrollbar = self.output_area.verticalScrollBar()
        if scrollbar is not None:
            scrollbar.setValue(scrollbar.maximum())

    def _on_enter(self) -> None:
        """Обрабатывает отправку команды пользователем по клавише Enter."""
        raw_command = self.input_entry.text()
        self.input_entry.clear()

        prompt = self.prompt_label.text()
        self.write_output(f"{prompt}{raw_command}")

        if not raw_command.strip():
            return

        self.execute_command(raw_command)

    def execute_command(self, raw_command: str) -> bool:
        """Разбирает строку с учетом кавычек и вызывает команду."""
        try:
            tokens = shlex.split(raw_command)
        except ValueError as err:
            self.write_output(
                f"Ошибка синтаксиса (неверные кавычки): {err}"
            )
            return False

        if not tokens:
            return True

        return self._dispatch_command(tokens[0], tokens[1:])

    def _dispatch_command(self, cmd_name: str, args: list[str]) -> bool:
        """Перенаправляет вызов соответствующему методу-обработчику."""
        handlers = {
            "exit": self._cmd_exit,
            "ls": self._cmd_ls,
            "cd": self._cmd_cd,
            "vfs-save": self._cmd_vfs_save,
        }
        handler = handlers.get(cmd_name)
        if handler is None:
            self.write_output(f"Ошибка: команда '{cmd_name}' не найдена.")
            return False
        return handler(args)

    def _cmd_exit(self, args: list[str]) -> bool:
        """Завершает работу графического окна эмулятора."""
        if args:
            self.write_output("Ошибка: exit: слишком много аргументов.")
            return False
        self.close()
        return True

    def _cmd_ls(self, args: list[str]) -> bool:
        """Команда-заглушка ls с валидацией флагов."""
        valid_flags = ("-l", "-a", "-la", "-al")
        for arg in args:
            if arg.startswith("-") and arg not in valid_flags:
                self.write_output(f"Ошибка: ls: неверный ключ '{arg}'.")
                return False

        self.write_output(f"[Заглушка] Команда: 'ls', Аргументы: {args}")
        return True

    def _cmd_cd(self, args: list[str]) -> bool:
        """Команда-заглушка cd с проверкой количества аргументов."""
        if len(args) > MAX_CD_ARGS:
            self.write_output("Ошибка: cd: слишком много аргументов.")
            return False

        self.write_output(f"[Заглушка] Команда: 'cd', Аргументы: {args}")
        return True

    def _cmd_vfs_save(self, args: list[str]) -> bool:
        """Сохраняет текущее состояние VFS в указанный файл."""
        if len(args) != REQUIRED_SAVE_ARGS:
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