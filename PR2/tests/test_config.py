"""Модульные тесты загрузки и валидации конфигурации."""

import tempfile
import unittest
from pathlib import Path
from typing import Any

from src.config import ConfigError, load_config, parse_config_dict
from src.main import EXIT_ERROR, EXIT_SUCCESS, run_cli


def get_valid_dict() -> dict[str, Any]:
    """Возвращает эталонный словарь корректных параметров."""
    return {
        "package_name": "express",
        "repository": "https://registry.npmjs.org",
        "test_mode": False,
        "package_version": "4.19.2",
        "output_file": "graph.svg",
        "max_depth": 3,
        "filter_substring": "debug",
    }


class TestConfigValidation(unittest.TestCase):
    """Тесты проверки корректности и обработки ошибок параметров."""

    def test_valid_config_success(self) -> None:
        """Проверяет успешный разбор корректной конфигурации."""
        data = get_valid_dict()
        cfg = parse_config_dict(data)
        self.assertEqual(cfg.package_name, "express")
        self.assertEqual(cfg.max_depth, data["max_depth"])

    def test_invalid_package_name(self) -> None:
        """Проверяет обработку ошибки для параметра package_name."""
        data = get_valid_dict()
        data["package_name"] = "   "
        with self.assertRaises(ConfigError):
            parse_config_dict(data)

    def test_invalid_repository_url(self) -> None:
        """Проверяет обработку ошибки для параметра repository."""
        data = get_valid_dict()
        data["repository"] = "ftp://invalid-url"
        with self.assertRaises(ConfigError):
            parse_config_dict(data)

    def test_invalid_test_mode(self) -> None:
        """Проверяет обработку ошибки для параметра test_mode."""
        data = get_valid_dict()
        data["test_mode"] = "yes"
        with self.assertRaises(ConfigError):
            parse_config_dict(data)

    def test_invalid_package_version(self) -> None:
        """Проверяет обработку ошибки для параметра package_version."""
        data = get_valid_dict()
        data["package_version"] = ""
        with self.assertRaises(ConfigError):
            parse_config_dict(data)

    def test_invalid_output_file(self) -> None:
        """Проверяет обработку ошибки для параметра output_file."""
        data = get_valid_dict()
        data["output_file"] = "graph.png"
        with self.assertRaises(ConfigError):
            parse_config_dict(data)

    def test_invalid_max_depth(self) -> None:
        """Проверяет обработку ошибки для параметра max_depth."""
        data = get_valid_dict()
        data["max_depth"] = 0
        with self.assertRaises(ConfigError):
            parse_config_dict(data)

    def test_invalid_filter_substring(self) -> None:
        """Проверяет обработку ошибки для параметра filter_substring."""
        data = get_valid_dict()
        data["filter_substring"] = 123
        with self.assertRaises(ConfigError):
            parse_config_dict(data)

    def test_missing_file_and_cli_codes(self) -> None:
        """Проверяет обработку отсутствующего файла и коды возврата CLI."""
        with self.assertRaises(ConfigError):
            load_config(Path("non_existent_config.toml"))
        code = run_cli(["-c", "non_existent_config.toml"])
        self.assertEqual(code, EXIT_ERROR)

    def test_cli_valid_toml_file(self) -> None:
        """Проверяет успешный запуск CLI с корректным TOML-файлом."""
        toml_content = (
            'package_name = "express"\n'
            'repository = "https://registry.npmjs.org"\n'
            "test_mode = false\n"
            'package_version = "4.19.2"\n'
            'output_file = "graph.svg"\n'
            "max_depth = 2\n"
            'filter_substring = ""\n'
        )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", encoding="utf-8", delete=False
        ) as tmp:
            tmp.write(toml_content)
            tmp_path = Path(tmp.name)
        try:
            code = run_cli(["-c", str(tmp_path)])
            self.assertEqual(code, EXIT_SUCCESS)
        finally:
            tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()