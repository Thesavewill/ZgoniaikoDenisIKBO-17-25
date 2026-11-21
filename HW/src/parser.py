"""Парсер и трансформер AST для учебного конфигурационного языка."""

from pathlib import Path
from typing import Any

from lark import Lark, LarkError, Transformer

GRAMMAR_PATH = Path(__file__).parent / "grammar.lark"


class ConfigError(Exception):
    """Базовое исключение для ошибок трансляции конфигурации."""


class ConfigSyntaxError(ConfigError):
    """Исключение при обнаружении синтаксической ошибки во входном тексте."""


class ConfigTransformer(Transformer):
    """Преобразует дерево разбора Lark в структуры данных Python."""

    def start(self, items: list[Any]) -> Any:
        """Возвращает корневое разобранное значение."""
        return items[0]

    def number(self, items: list[Any]) -> float:
        """Преобразует токен NUMBER в число с плавающей точкой."""
        return float(items[0])

    def pair(self, items: list[Any]) -> tuple[str, Any]:
        """Преобразует пару ключ-значение в кортеж."""
        return (str(items[0]), items[1])

    def table(self, items: list[tuple[str, Any]]) -> dict[str, Any]:
        """Преобразует список пар ключ-значение в словарь."""
        return dict(items)


def build_parser() -> Lark:
    """Загружает грамматику Lark и создаёт экземпляр парсера."""
    grammar_text = GRAMMAR_PATH.read_text(encoding="utf-8")
    return Lark(grammar_text, parser="lalr", start="start")


def parse_config(text: str) -> Any:
    """Разбирает текст конфигурации в объекты Python."""
    parser = build_parser()
    try:
        tree = parser.parse(text)
    except LarkError as exc:
        raise ConfigSyntaxError(f"Синтаксическая ошибка: {exc}") from exc
    return ConfigTransformer().transform(tree)