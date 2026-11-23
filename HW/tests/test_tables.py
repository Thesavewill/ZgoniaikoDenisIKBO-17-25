"""Тесты разбора словарей, вложенных структур и имён ключей."""

import pytest

from HW.src.errors import ConfigSyntaxError
from HW.src.parser import parse_config


def test_empty_table() -> None:
    """Проверяет разбор пустого словаря."""
    expected: dict[str, float] = {}
    assert parse_config("table()") == expected


def test_single_pair_table() -> None:
    """Проверяет словарь с одной парой ключ-значение."""
    expected = {"width": 1920.0}
    assert parse_config("table(width => 1920.0)") == expected


def test_multiple_pairs_table() -> None:
    """Проверяет словарь с несколькими парами."""
    text = "table(x => 1.0, y => 2.5, z => 3.)"
    expected = {"x": 1.0, "y": 2.5, "z": 3.0}
    assert parse_config(text) == expected


def test_trailing_comma_in_table() -> None:
    """Проверяет поддержку висячей запятой в словаре."""
    text = "table(\n  a => 1.0,\n  b => 2.0,\n)"
    expected = {"a": 1.0, "b": 2.0}
    assert parse_config(text) == expected


def test_nested_tables() -> None:
    """Проверяет вложенные словари."""
    text = "table(outer => table(inner => 5.5), flag => 1.0)"
    expected = {"outer": {"inner": 5.5}, "flag": 1.0}
    assert parse_config(text) == expected


def test_deeply_nested_tables() -> None:
    """Проверяет многоуровневую вложенность словарей."""
    text = "table(a => table(b => table(c => 10.0)))"
    expected = {"a": {"b": {"c": 10.0}}}
    assert parse_config(text) == expected


def test_valid_identifier_names() -> None:
    """Проверяет допустимые форматы имён ключей."""
    text = "table(_priv => 1.0, Key2 => 2.0, aBC9 => 3.0)"
    expected = {"_priv": 1.0, "Key2": 2.0, "aBC9": 3.0}
    assert parse_config(text) == expected


def test_invalid_identifier_starts_with_digit() -> None:
    """Проверяет ошибку для имени, начинающегося с цифры."""
    with pytest.raises(ConfigSyntaxError):
        parse_config("table(1key => 1.0)")


def test_missing_arrow_in_pair() -> None:
    """Проверяет ошибку при отсутствии оператора =>."""
    with pytest.raises(ConfigSyntaxError):
        parse_config("table(key 1.0)")


def test_missing_comma_between_pairs() -> None:
    """Проверяет ошибку при отсутствии запятой между парами."""
    with pytest.raises(ConfigSyntaxError):
        parse_config("table(a => 1.0 b => 2.0)")