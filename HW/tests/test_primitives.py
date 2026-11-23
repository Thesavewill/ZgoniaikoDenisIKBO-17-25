"""Тесты разбора чисел, комментариев и базовых синтаксических ошибок."""

import pytest

from HW.src.errors import ConfigSyntaxError
from HW.src.parser import parse_config


def test_number_with_trailing_dot() -> None:
    """Проверяет число с точкой без дробной части."""
    expected = 42.0
    assert parse_config("42.") == expected


def test_number_with_fraction() -> None:
    """Проверяет стандартное число с плавающей точкой."""
    expected = 3.1415
    assert parse_config("3.1415") == expected


def test_number_zero() -> None:
    """Проверяет разбор нуля."""
    expected = 0.0
    assert parse_config("0.0") == expected


def test_single_line_comment() -> None:
    """Проверяет игнорирование однострочных комментариев."""
    text = "# Комментарий в начале\n12.5 # Комментарий в конце\n"
    expected = 12.5
    assert parse_config(text) == expected


def test_multi_line_comment() -> None:
    """Проверяет игнорирование многострочных комментариев."""
    text = "{{!\nМногострочный\nкомментарий\n}}\n7.25"
    expected = 7.25
    assert parse_config(text) == expected


def test_mixed_comments_and_whitespace() -> None:
    """Проверяет комбинацию обоих видов комментариев и пробелов."""
    text = (
        "# Первый комментарий\n"
        "{{! Второй\nкомментарий }}\n"
        "   99.1   \n"
        "# Финальный комментарий"
    )
    expected = 99.1
    assert parse_config(text) == expected


def test_invalid_integer_without_dot() -> None:
    """Проверяет ошибку для целого числа без точки."""
    with pytest.raises(ConfigSyntaxError):
        parse_config("42")


def test_unclosed_multiline_comment() -> None:
    """Проверяет ошибку при незакрытом многострочном комментарии."""
    with pytest.raises(ConfigSyntaxError):
        parse_config("{{! Незакрытый комментарий 1.0")


def test_empty_input() -> None:
    """Проверяет ошибку при пустом вводе."""
    with pytest.raises(ConfigSyntaxError):
        parse_config("   \n\t  ")