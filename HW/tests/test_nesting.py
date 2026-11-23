"""Тесты сложной вложенности, комментариев внутри структур и цепочек."""

import pytest

from HW.src.parser import parse_config


def test_comments_inside_table() -> None:
    """Проверяет однострочные и многострочные комментарии внутри словаря."""
    text = (
        "table(\n"
        "  # комментарий перед ключом\n"
        "  alpha => 1.0, # комментарий после значения\n"
        "  {{! многострочный\nкомментарий }} beta => 2.0,\n"
        ")"
    )
    expected = {"alpha": 1.0, "beta": 2.0}
    assert parse_config(text) == expected


def test_comments_inside_postfix_expression() -> None:
    """Проверяет комментарии внутри постфиксного выражения."""
    text = "$[10.0 {{! слагаемое }} 5.0 # оператор\n +]"
    expected = 15.0
    assert parse_config(text) == expected


def test_chained_constant_expressions() -> None:
    """Проверяет цепочку констант, вычисляемых друг через друга."""
    text = (
        "a is 2.0\n"
        "b is $[a 3.0 pow()]\n"
        "c is $[b 1.0 + sqrt()]\n"
        "table(a => $[a], b => $[b], c => $[c])"
    )
    expected = {"a": 2.0, "b": 8.0, "c": 3.0}
    assert parse_config(text) == expected


def test_nested_tables_with_constants_and_math() -> None:
    """Проверяет глубокую вложенность со словарями-константами и математикой."""
    text = (
        "base is 100.0\n"
        "limits is table(min => 1.0, max => $[base 2.0 *])\n"
        "table(\n"
        "  cluster => table(\n"
        "    node => table(\n"
        "      limits => $[limits],\n"
        "      half => $[base 2.0 /],\n"
        "    )\n"
        "  )\n"
        ")"
    )
    expected = {
        "cluster": {
            "node": {
                "limits": {"min": 1.0, "max": 200.0},
                "half": 50.0,
            }
        }
    }
    assert parse_config(text) == expected


def test_duplicate_keys_last_wins() -> None:
    """Проверяет поведение при повторяющемся ключе в словаре."""
    text = "table(k => 1.0, k => 2.5)"
    expected = {"k": 2.5}
    assert parse_config(text) == expected


def test_negative_result_from_subtraction() -> None:
    """Проверяет получение отрицательного числа через вычитание."""
    text = "table(delta => $[3.0 10.0 -])"
    expected = {"delta": -7.0}
    assert parse_config(text) == expected


def test_float_precision_in_division() -> None:
    """Проверяет точность вычислений с плавающей точкой."""
    result = parse_config("$[1.0 4.0 /]")
    expected = 0.25
    assert result == pytest.approx(expected)