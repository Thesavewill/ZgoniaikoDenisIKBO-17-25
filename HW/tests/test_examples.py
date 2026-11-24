"""Тесты примеров конфигураций из разных предметных областей."""

from pathlib import Path

from HW.src.cli import translate
from HW.src.parser import parse_config

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def test_game_balance_example() -> None:
    """Проверяет пример конфигурации игрового баланса."""
    text = (EXAMPLES_DIR / "game_balance.conf").read_text(encoding="utf-8")
    result = parse_config(text)
    expected_hp = 100.0
    expected_crit = 30.0
    assert result["health"]["base"] == expected_hp
    assert result["combat"]["critDamage"] == expected_crit
    assert result["health"]["effective"] > expected_hp


def test_server_cluster_example() -> None:
    """Проверяет пример конфигурации сетевого кластера."""
    text = (EXAMPLES_DIR / "server_cluster.conf").read_text(encoding="utf-8")
    result = parse_config(text)
    expected_workers = 12.0
    expected_timeout = 3.5
    assert result["cluster"]["totalWorkers"] == expected_workers
    assert result["cluster"]["requestTimeout"] == expected_timeout


def test_finance_model_example() -> None:
    """Проверяет пример конфигурации финансовой модели."""
    text = (EXAMPLES_DIR / "finance_model.conf").read_text(encoding="utf-8")
    result = parse_config(text)
    expected_amount = 50000.0
    expected_buffer = 5000.0
    assert result["loan"]["amount"] == expected_amount
    assert result["reserve"]["minBuffer"] == expected_buffer


def test_all_examples_translate_to_json() -> None:
    """Проверяет, что каждый пример корректно переводится в JSON."""
    example_files = sorted(EXAMPLES_DIR.glob("*.conf"))
    min_examples = 3
    assert len(example_files) >= min_examples
    for config_path in example_files:
        content = config_path.read_text(encoding="utf-8")
        json_output = translate(content)
        assert json_output.startswith("{")