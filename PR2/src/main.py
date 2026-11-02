"""Точка входа CLI-приложения визуализации графа зависимостей."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from src.config import AppConfig, ConfigError, load_config

EXIT_SUCCESS = 0
EXIT_ERROR = 1


def build_parser() -> argparse.ArgumentParser:
    """Создает парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Инструмент визуализации графа зависимостей пакетов."
    )
    parser.add_argument(
        "-c",
        "--config",
        default="config.toml",
        help="Путь к конфигурационному файлу формата TOML.",
    )
    return parser


def print_config(config: AppConfig) -> None:
    """Выводит все настраиваемые параметры в формате ключ-значение."""
    for key, value in config.to_dict().items():
        print(f"{key}={value}")


def run_cli(argv: Sequence[str] | None = None) -> int:
    """Запускает CLI-приложение и возвращает код завершения."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = load_config(Path(args.config))
    except ConfigError as exc:
        print(f"Ошибка конфигурации: {exc}", file=sys.stderr)
        return EXIT_ERROR

    print_config(config)
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(run_cli())