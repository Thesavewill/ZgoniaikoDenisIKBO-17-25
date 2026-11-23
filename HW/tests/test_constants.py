"""Тесты объявления, подстановки и области видимости констант."""

import pytest

from HW.src.errors import ConfigEvaluationError
from HW.src.parser import parse_config


def test_simple_numeric_constant() -> None:
    """Проверяет объявление и подстановку числовой константы."""
    text = "rate is 0.5\ntable(discount => $[rate])"
    expected = {"discount": 0.5}
    assert parse_config(text) == expected


def test_multiple_constants() -> None:
    """Проверяет работу с несколькими константами."""
    text = "a is 1.0\nb is 2.0\ntable(first => $[a], second => $[b])"
    expected = {"first": 1.0, "second": 2.0}
    assert parse_config(text) == expected


def test_constant_referencing_constant() -> None:
    """Проверяет объявление константы через другую константу."""
    text = "base is 10.0\ncopy is $[base]\ntable(val => $[copy])"
    expected = {"val": 10.0}
    assert parse_config(text) == expected


def test_constant_holding_table() -> None:
    """Проверяет хранение словаря в константе."""
    text = (
        "defaults is table(timeout => 30.0, retries => 3.0)\n"
        "table(service => $[defaults])"
    )
    expected = {"service": {"timeout": 30.0, "retries": 3.0}}
    assert parse_config(text) == expected


def test_constant_inside_nested_table() -> None:
    """Проверяет подстановку констант во вложенные словари."""
    text = "port is 8080.0\ntable(net => table(http => $[port]))"
    expected = {"net": {"http": 8080.0}}
    assert parse_config(text) == expected


def test_constant_redeclaration() -> None:
    """Проверяет переопределение ранее объявленной константы."""
    text = "ver is 1.0\nver is 2.0\ntable(version => $[ver])"
    expected = {"version": 2.0}
    assert parse_config(text) == expected


def test_undefined_constant_raises_error() -> None:
    """Проверяет ошибку при обращении к необъявленной константе."""
    with pytest.raises(ConfigEvaluationError):
        parse_config("table(x => $[missing])")


def test_constant_used_before_declaration() -> None:
    """Проверяет ошибку при использовании константы до объявления."""
    text = "a is $[b]\nb is 5.0\ntable(res => $[a])"
    with pytest.raises(ConfigEvaluationError):
        parse_config(text)