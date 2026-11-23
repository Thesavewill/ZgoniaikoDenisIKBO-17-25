"""Интеграционные тесты интерфейса командной строки."""

import io
import json

import pytest

from HW.src.cli import EXIT_ERROR, EXIT_SUCCESS, main, translate


def test_translate_returns_valid_json() -> None:
    """Проверяет преобразование конфигурации в корректный JSON."""
    raw = translate("table(a => 1.0, b => 2.5)")
    expected = {"a": 1.0, "b": 2.5}
    assert json.loads(raw) == expected


def test_main_success(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Проверяет успешное выполнение CLI через stdin/stdout."""
    monkeypatch.setattr("sys.stdin", io.StringIO("table(ok => 1.0)"))
    code = main()
    captured = capsys.readouterr()
    expected = {"ok": 1.0}
    assert code == EXIT_SUCCESS
    assert json.loads(captured.out) == expected
    assert captured.err == ""


def test_main_strips_utf8_bom(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Проверяет удаление BOM-маркера в начале входного потока."""
    monkeypatch.setattr("sys.stdin", io.StringIO("\ufefftable(n => 4.0)"))
    code = main()
    captured = capsys.readouterr()
    expected = {"n": 4.0}
    assert code == EXIT_SUCCESS
    assert json.loads(captured.out) == expected


def test_main_syntax_error_returns_error_code(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Проверяет код возврата и вывод stderr при синтаксической ошибке."""
    monkeypatch.setattr("sys.stdin", io.StringIO("table(broken"))
    code = main()
    captured = capsys.readouterr()
    assert code == EXIT_ERROR
    assert captured.out == ""
    assert "Ошибка:" in captured.err


def test_main_evaluation_error_returns_error_code(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Проверяет код возврата и вывод stderr при ошибке вычисления."""
    monkeypatch.setattr("sys.stdin", io.StringIO("$[1.0 0.0 /]"))
    code = main()
    captured = capsys.readouterr()
    assert code == EXIT_ERROR
    assert captured.out == ""
    assert "Ошибка:" in captured.err