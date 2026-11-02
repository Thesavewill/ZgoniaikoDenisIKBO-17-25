"""Точка входа CLI-приложения визуализации графа зависимостей."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from src.config import AppConfig, ConfigError, load_config
from src.graph import build_dependency_graph

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
        help="Путь к конфигурационному файлу TOML.",
    )
    return parser


def print_graph(config: AppConfig) -> int:
    """Строит и выводит граф зависимостей в текстовом виде."""
    graph = build_dependency_graph(
        start_pkg=config.package_name,
        start_ver=config.package_version,
        repo=config.repository,
        test_mode=config.test_mode,
        max_depth=config.max_depth,
        filter_sub=config.filter_substring,
    )

    print(f"Граф зависимостей (глубина {config.max_depth}):")
    for node, edges in graph.items():
        if edges:
            print(f"  {node} -> {', '.join(edges)}")
        else:
            print(f"  {node} -> (нет зависимостей)")
            
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

    return print_graph(config)


if __name__ == "__main__":
    sys.exit(run_cli())