"""Точка входа CLI-приложения визуализации графа зависимостей."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from src.config import AppConfig, ConfigError, load_config
from src.fetcher import FetchError, fetch_package_data

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


def print_dependencies(config: AppConfig) -> int:
    """Получает и выводит прямые зависимости пакета."""
    try:
        deps = fetch_package_data(
            config.repository, config.package_name, config.package_version
        )
    except FetchError as exc:
        print(f"Ошибка получения зависимостей: {exc}", file=sys.stderr)
        return EXIT_ERROR

    print(
        f"Прямые зависимости {config.package_name}@"
        f"{config.package_version}:"
    )
    if not deps:
        print("  (нет зависимостей)")
    for name, ver in deps.items():
        print(f"  {name}: {ver}")
    return EXIT_SUCCESS


def run_cli(argv: Sequence[str] | None = None) -> int:
    """Запускает CLI-приложение и возвращает код завершения."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = load_config(Path(args.config))
    except ConfigError as exc:
        print(f"Ошибка конфигурации: {exc}", file=sys.stderr)
        return EXIT_ERROR

    return print_dependencies(config)


if __name__ == "__main__":
    sys.exit(run_cli())