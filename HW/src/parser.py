"""Парсер и трансформер AST для учебного конфигурационного языка."""

from pathlib import Path
from typing import Any

from lark import Lark, LarkError, Transformer
from lark.exceptions import VisitError

from .errors import ConfigError, ConfigSyntaxError
from .evaluator import ConstRef, Operator, evaluate_postfix

GRAMMAR_PATH = Path(__file__).parent / "grammar.lark"


class ConfigTransformer(Transformer):
    """Преобразует дерево разбора Lark в структуры данных Python."""

    def __init__(self) -> None:
        """Инициализирует трансформер с пустой таблицей констант."""
        super().__init__()
        self.constants: dict[str, Any] = {}

    def start(self, items: list[Any]) -> Any:
        """Возвращает корневое разобранное значение."""
        return items[-1]

    def const_decl(self, items: list[Any]) -> None:
        """Регистрирует константу в таблице констант."""
        name = str(items[0])
        self.constants[name] = items[1]

    def const_ref(self, items: list[Any]) -> ConstRef:
        """Создаёт ссылку на константу внутри выражения."""
        return ConstRef(str(items[0]))

    def op(self, items: list[Any]) -> Operator:
        """Создаёт оператор для постфиксного выражения."""
        return Operator(str(items[0]))

    def func(self, items: list[Any]) -> Operator:
        """Создаёт функцию для постфиксного выражения."""
        return Operator(str(items[0]))

    def const_expr(self, items: list[Any]) -> Any:
        """Вычисляет постфиксное константное выражение."""
        return evaluate_postfix(items, self.constants)

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
    try:
        return ConfigTransformer().transform(tree)
    except VisitError as exc:
        if isinstance(exc.orig_exc, ConfigError):
            raise exc.orig_exc from exc
        raise