"""Точка входа CLI-приложения визуализации графа зависимостей."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from src.config import AppConfig, ConfigError, load_config
from src.graph import build_dependency_graph, get_reverse_dependencies
from src.visualizer import generate_dot_source, render_svg

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
    parser.add_argument(
        "-r",
        "--reverse",
        help="Вывести обратные зависимости для заданного пакета.",
    )
    return parser


def print_graph(config: AppConfig, reverse_target: str | None) -> int:
    """Строит граф и рендерит SVG или выводит обратные зависимости."""
    graph = build_dependency_graph(
        start_pkg=config.package_name,
        start_ver=config.package_version,
        repo=config.repository,
        test_mode=config.test_mode,
        max_depth=config.max_depth,
        filter_sub=config.filter_substring,
    )

    if reverse_target:
        rev_deps = get_reverse_dependencies(graph, reverse_target)
        print(f"Обратные зависимости для пакета {reverse_target}:")
        if rev_deps:
            for dep in rev_deps:
                print(f"  {dep}")
        else:
            print("  (нет обратных зависимостей)")
        return EXIT_SUCCESS

    dot_source = generate_dot_source(graph)
    try:
        render_svg(dot_source, config.output_file)
        print(f"DOT-код сгенерирован. SVG сохранен в {config.output_file}")
    except RuntimeError as exc:
        print(f"Ошибка визуализации: {exc}", file=sys.stderr)
        return EXIT_ERROR

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

    return print_graph(config, args.reverse)


if __name__ == "__main__":
    sys.exit(run_cli())
    