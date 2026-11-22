"""Стековый вычислитель постфиксных константных выражений."""

import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .errors import ConfigEvaluationError

MIN_UNARY_OPERANDS = 1
MIN_BINARY_OPERANDS = 2
EXPECTED_STACK_SIZE = 1
ZERO_VALUE = 0.0


@dataclass(frozen=True)
class ConstRef:
    """Ссылка на объявленную константу внутри выражения."""

    name: str


@dataclass(frozen=True)
class Operator:
    """Оператор или функция внутри постфиксного выражения."""

    symbol: str


def _ensure_number(value: Any) -> float:
    """Проверяет, что значение является числом, и возвращает float."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigEvaluationError(
            f"Ожидалось числовое значение, получено: {type(value).__name__}"
        )
    return float(value)


def _safe_divide(left: float, right: float) -> float:
    """Выполняет деление с проверкой делителя на ноль."""
    if right == ZERO_VALUE:
        raise ConfigEvaluationError("Деление на ноль в константном выражении")
    return left / right


def _safe_sqrt(value: float) -> float:
    """Вычисляет квадратный корень с проверкой на отрицательное число."""
    if value < ZERO_VALUE:
        raise ConfigEvaluationError(
            "Невозможно извлечь квадратный корень из отрицательного числа"
        )
    return math.sqrt(value)


BINARY_OPERATIONS: dict[str, Callable[[float, float], float]] = {
    "+": lambda left, right: left + right,
    "-": lambda left, right: left - right,
    "*": lambda left, right: left * right,
    "/": _safe_divide,
    "pow()": math.pow,
}

UNARY_OPERATIONS: dict[str, Callable[[float], float]] = {
    "sqrt()": _safe_sqrt,
}


def _apply_operator(symbol: str, stack: list[Any]) -> None:
    """Применяет унарный или бинарный оператор к вершине стека."""
    if symbol in UNARY_OPERATIONS:
        if len(stack) < MIN_UNARY_OPERANDS:
            raise ConfigEvaluationError(f"Недостаточно операндов для {symbol}")
        operand = _ensure_number(stack.pop())
        stack.append(UNARY_OPERATIONS[symbol](operand))
        return

    if symbol in BINARY_OPERATIONS:
        if len(stack) < MIN_BINARY_OPERANDS:
            raise ConfigEvaluationError(f"Недостаточно операндов для {symbol}")
        right = _ensure_number(stack.pop())
        left = _ensure_number(stack.pop())
        stack.append(BINARY_OPERATIONS[symbol](left, right))
        return

    raise ConfigEvaluationError(f"Неизвестная операция: {symbol}")


def evaluate_postfix(
    items: list[Any],
    constants: dict[str, Any],
) -> Any:
    """Вычисляет постфиксное выражение с учётом таблицы констант."""
    stack: list[Any] = []
    for item in items:
        if isinstance(item, ConstRef):
            if item.name not in constants:
                raise ConfigEvaluationError(
                    f"Неизвестная константа: {item.name}"
                )
            stack.append(constants[item.name])
        elif isinstance(item, Operator):
            _apply_operator(item.symbol, stack)
        else:
            stack.append(item)

    if len(stack) != EXPECTED_STACK_SIZE:
        raise ConfigEvaluationError(
            "Некорректное постфиксное выражение: неверный баланс операндов"
        )
    return stack[0]