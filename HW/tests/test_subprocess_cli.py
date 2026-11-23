"""Тесты запуска CLI-инструмента в отдельном процессе."""

import json
import os
import subprocess
import sys
from pathlib import Path

from HW.src.cli import EXIT_ERROR, EXIT_SUCCESS

REPO_ROOT = Path(__file__).resolve().parents[2]


def run_cli_process(input_text: str) -> subprocess.CompletedProcess[str]:
    """Запускает python -m HW.src.cli с передачей текста в stdin."""
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, "-m", "HW.src.cli"],
        input=input_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(REPO_ROOT),
        env=env,
        check=False,
    )


def test_subprocess_valid_table() -> None:
    """Проверяет вывод корректного JSON в stdout."""
    proc = run_cli_process("x is 4.0\ntable(val => $[x sqrt()])")
    expected = {"val": 2.0}
    assert proc.returncode == EXIT_SUCCESS
    assert json.loads(proc.stdout) == expected
    assert proc.stderr == ""


def test_subprocess_default_indent_two_spaces() -> None:
    """Проверяет форматирование JSON с отступом в два пробела."""
    proc = run_cli_process("table(a => 1.5)")
    expected_out = '{\n  "a": 1.5\n}\n'
    assert proc.returncode == EXIT_SUCCESS
    assert proc.stdout == expected_out


def test_subprocess_syntax_error_exit_code() -> None:
    """Проверяет код возврата и stderr при синтаксической ошибке."""
    proc = run_cli_process("table(a => )")
    assert proc.returncode == EXIT_ERROR
    assert proc.stdout == ""
    assert "Ошибка:" in proc.stderr


def test_subprocess_evaluation_error_exit_code() -> None:
    """Проверяет код возврата и stderr при ошибке вычисления."""
    proc = run_cli_process("$[5.0 0.0 /]")
    assert proc.returncode == EXIT_ERROR
    assert proc.stdout == ""
    assert "Ошибка:" in proc.stderr