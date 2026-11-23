"""Тесты постфиксного вычислителя и обработки ошибок вычисления."""

import pytest

from HW.src.errors import ConfigEvaluationError
from HW.src.parser import parse_config


def test_addition() -> None:
    """Проверяет операцию сложения."""
    expected = 7.5
    assert parse_config("$[5.0 2.5 +]") == expected


def test_subtraction() -> None:
    """Проверяет операцию вычитания с учётом порядка операндов."""
    expected = 6.0
    assert parse_config("$[10.0 4.0 -]") == expected


def test_multiplication() -> None:
    """Проверяет операцию умножения."""
    expected = 15.0
    assert parse_config("$[3.0 5.0 *]") == expected


def test_division() -> None:
    """Проверяет операцию деления."""
    expected = 4.0
    assert parse_config("$[20.0 5.0 /]") == expected


def test_sqrt_function() -> None:
    """Проверяет функцию извлечения квадратного корня."""
    expected = 9.0
    assert parse_config("$[81.0 sqrt()]") == expected


def test_pow_function() -> None:
    """Проверяет функцию возведения в степень."""
    expected = 8.0
    assert parse_config("$[2.0 3.0 pow()]") == expected


def test_complex_postfix_expression() -> None:
    """Проверяет составное постфиксное выражение с константами."""
    text = (
        "x is 3.0\n"
        "y is 4.0\n"
        "table(hyp => $[x 2.0 pow() y 2.0 pow() + sqrt()])"
    )
    expected = {"hyp": 5.0}
    assert parse_config(text) == expected


def test_division_by_zero_error() -> None:
    """Проверяет ошибку при делении на ноль."""
    with pytest.raises(ConfigEvaluationError):
        parse_config("$[10.0 0.0 /]")


def test_sqrt_negative_number_error() -> None:
    """Проверяет ошибку при извлечении корня из отрицательного числа."""
    with pytest.raises(ConfigEvaluationError):
        parse_config("$[1.0 5.0 - sqrt()]")


def test_not_enough_operands_binary() -> None:
    """Проверяет ошибку нехватки операндов для бинарной операции."""
    with pytest.raises(ConfigEvaluationError):
        parse_config("$[5.0 +]")


def test_not_enough_operands_unary() -> None:
    """Проверяет ошибку нехватки операндов для унарной функции."""
    with pytest.raises(ConfigEvaluationError):
        parse_config("$[sqrt()]")


def test_too_many_operands_error() -> None:
    """Проверяет ошибку при избыточных значениях в стеке."""
    with pytest.raises(ConfigEvaluationError):
        parse_config("$[1.0 2.0 3.0 +]")


def test_non_numeric_operand_error() -> None:
    """Проверяет ошибку при арифметике над словарём."""
    text = "cfg is table(a => 1.0)\n$[cfg 2.0 +]"
    with pytest.raises(ConfigEvaluationError):
        parse_config(text)