"""Модуль виртуальной файловой системы (VFS) в оперативной памяти."""

import base64
import binascii
import csv
from pathlib import Path, PurePosixPath

EXPECTED_CSV_COLUMNS = 3
FIRST_DATA_LINE = 2


class VFSNode:
    """Узел дерева виртуальной файловой системы."""

    def __init__(
        self,
        name: str,
        node_type: str,
        content: bytes = b"",
    ) -> None:
        """Инициализирует узел файла или директории."""
        self.name = name
        self.node_type = node_type
        self.content = content
        self.children: dict[str, VFSNode] = {}


class VirtualFileSystem:
    """Класс управления виртуальной файловой системой в памяти."""

    def __init__(self) -> None:
        """Создает пустую корневую директорию VFS."""
        self.root = VFSNode("/", "dir")
        self.is_loaded = False

    def load_from_csv(self, file_path: str) -> None:
        """Загружает структуру VFS из CSV-файла в оперативную память."""
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"файл '{file_path}' не найден.")

        new_root = VFSNode("/", "dir")
        try:
            self._read_csv_rows(path, new_root)
        except csv.Error as err:
            raise ValueError(f"ошибка чтения CSV: {err}") from err
        except UnicodeDecodeError as err:
            raise ValueError("требуется кодировка UTF-8.") from err

        self.root = new_root
        self.is_loaded = True

    def _read_csv_rows(self, path: Path, root: VFSNode) -> None:
        """Читает и валидирует строки CSV-файла."""
        with path.open("r", encoding="utf-8", newline="") as csv_file:
            reader = csv.reader(csv_file)
            header = next(reader, None)
            if header != ["path", "type", "content"]:
                raise ValueError(
                    "неверный заголовок (ожидается: path,type,content)."
                )

            for line_num, row in enumerate(reader, start=FIRST_DATA_LINE):
                if len(row) != EXPECTED_CSV_COLUMNS:
                    raise ValueError(
                        f"строка {line_num}: ожидается 3 столбца."
                    )
                self._insert_node(root, row, line_num)

    def _insert_node(
        self,
        root: VFSNode,
        row: list[str],
        line_num: int,
    ) -> None:
        """Добавляет один элемент из строки CSV в дерево VFS."""
        raw_path = row[0].strip()
        node_type = row[1].strip()
        b64_content = row[2].strip()

        content_bytes = self._validate_and_decode(
            raw_path, node_type, b64_content, line_num
        )
        posix_path = PurePosixPath(raw_path)
        parts = [p for p in posix_path.parts if p != "/"]
        if not parts:
            return

        parent = self._get_parent_dir(root, parts[:-1], line_num)
        self._set_child_node(
            parent, parts[-1], node_type, content_bytes, line_num
        )

    def _validate_and_decode(
        self,
        raw_path: str,
        node_type: str,
        b64_content: str,
        line_num: int,
    ) -> bytes:
        """Проверяет корректность пути, типа узла и декодирует base64."""
        if not raw_path.startswith("/"):
            raise ValueError(
                f"строка {line_num}: путь '{raw_path}' "
                "должен начинаться с '/'."
            )
        if node_type not in ("dir", "file"):
            raise ValueError(
                f"строка {line_num}: неизвестный тип '{node_type}'."
            )
        return self._decode_content(node_type, b64_content, line_num)

    def _decode_content(
        self,
        node_type: str,
        b64_content: str,
        line_num: int,
    ) -> bytes:
        """Декодирует содержимое файла из формата base64."""
        if node_type == "dir":
            if b64_content:
                raise ValueError(
                    f"строка {line_num}: у папки не может быть контента."
                )
            return b""

        try:
            return base64.b64decode(
                b64_content.encode("ascii"), validate=True
            )
        except (binascii.Error, UnicodeEncodeError) as err:
            raise ValueError(
                f"строка {line_num}: некорректные данные base64."
            ) from err

    def _get_parent_dir(
        self,
        root: VFSNode,
        parts: list[str],
        line_num: int,
    ) -> VFSNode:
        """Находит или создает цепочку родительских директорий."""
        current = root
        for part in parts:
            if part not in current.children:
                current.children[part] = VFSNode(part, "dir")
            elif current.children[part].node_type != "dir":
                raise ValueError(
                    f"строка {line_num}: '{part}' является файлом."
                )
            current = current.children[part]
        return current

    def _set_child_node(
        self,
        parent: VFSNode,
        name: str,
        node_type: str,
        content: bytes,
        line_num: int,
    ) -> None:
        """Создает или обновляет целевой узел в родительской папке."""
        if name in parent.children:
            existing = parent.children[name]
            if existing.node_type != node_type:
                raise ValueError(
                    f"строка {line_num}: конфликт типов для '{name}'."
                )
            existing.content = content
        else:
            parent.children[name] = VFSNode(name, node_type, content)

    def save_to_csv(self, target_path: str) -> None:
        """Сохраняет состояние VFS из памяти в CSV-файл на диске."""
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
        """Рекурсивно обходит дерево VFS и формирует строки для CSV."""
        for name, child in sorted(node.children.items()):
            child_path = current_path / name
            b64_str = ""
            if child.node_type == "file":
                b64_str = base64.b64encode(child.content).decode("ascii")
            rows.append([str(child_path), child.node_type, b64_str])
            if child.node_type == "dir":
                self._collect_rows(child, child_path, rows)

    def get_motd(self) -> str | None:
        """Возвращает содержимое файла /motd из корня VFS, если он есть."""
        motd_node = self.root.children.get("motd")
        if motd_node and motd_node.node_type == "file":
            return motd_node.content.decode("utf-8", errors="replace")
        return None
