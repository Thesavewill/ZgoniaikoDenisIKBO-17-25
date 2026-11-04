"""Модуль загрузки и валидации конфигурации из TOML-файла."""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MIN_DEPTH = 1
URL_PREFIXES = ("http://", "https://")
REQUIRED_KEYS = (
    "package_name",
    "repository",
    "test_mode",
    "package_version",
    "output_file",
    "max_depth",
    "filter_substring",
)


class ConfigError(ValueError):
    """Исключение при некорректных параметрах конфигурации."""


@dataclass(frozen=True)
class AppConfig:
    """Структура параметров конфигурации приложения."""

    package_name: str
    repository: str
    test_mode: bool
    package_version: str
    output_file: str
    max_depth: int
    filter_substring: str

    def to_dict(self) -> dict[str, Any]:
        """Возвращает параметры конфигурации в виде словаря."""
        return {
            "package_name": self.package_name,
            "repository": self.repository,
            "test_mode": self.test_mode,
            "package_version": self.package_version,
            "output_file": self.output_file,
            "max_depth": self.max_depth,
            "filter_substring": self.filter_substring,
        }


def _require_non_empty_str(data: dict[str, Any], key: str) -> str:
    """Проверяет, что параметр является непустой строкой."""
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(
            f"Параметр '{key}' должен быть непустой строкой."
        )
    return value.strip()


def _require_str(data: dict[str, Any], key: str) -> str:
    """Проверяет, что параметр является строкой."""
    value = data.get(key)
    if not isinstance(value, str):
        raise ConfigError(f"Параметр '{key}' должен быть строкой.")
    return value


def _require_bool(data: dict[str, Any], key: str) -> bool:
    """Проверяет, что параметр является логическим значением."""
    value = data.get(key)
    if not isinstance(value, bool):
        raise ConfigError(
            f"Параметр '{key}' должен иметь тип bool."
        )
    return value


def _require_positive_int(data: dict[str, Any], key: str) -> int:
    """Проверяет, что параметр является целым числом >= MIN_DEPTH."""
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(
            f"Параметр '{key}' должен быть целым числом."
        )
    if value < MIN_DEPTH:
        raise ConfigError(
            f"Параметр '{key}' должен быть не меньше {MIN_DEPTH}."
        )
    return value


def _validate_repository(repository: str, test_mode: bool) -> str:
    """Проверяет корректность URL или пути к репозиторию."""
    if not test_mode and not repository.startswith(URL_PREFIXES):
        raise ConfigError(
            "В обычном режиме 'repository' должен начинаться "
            "с http:// или https://."
        )
    return repository


def _validate_output_file(filename: str) -> str:
    """Проверяет корректность имени выходного файла графа."""
    if not filename.endswith(".svg"):
        raise ConfigError(
            "Параметр 'output_file' должен иметь расширение .svg."
        )
    return filename


def parse_config_dict(data: dict[str, Any]) -> AppConfig:
    """Валидирует словарь параметров и создает объект AppConfig."""
    missing = [key for key in REQUIRED_KEYS if key not in data]
    if missing:
        joined = ", ".join(missing)
        raise ConfigError(f"Отсутствуют обязательные параметры: {joined}")

    package_name = _require_non_empty_str(data, "package_name")
    test_mode = _require_bool(data, "test_mode")
    raw_repo = _require_non_empty_str(data, "repository")
    repository = _validate_repository(raw_repo, test_mode)
    package_version = _require_non_empty_str(data, "package_version")
    raw_output = _require_non_empty_str(data, "output_file")
    output_file = _validate_output_file(raw_output)
    max_depth = _require_positive_int(data, "max_depth")
    filter_substring = _require_str(data, "filter_substring")

    return AppConfig(
        package_name=package_name,
        repository=repository,
        test_mode=test_mode,
        package_version=package_version,
        output_file=output_file,
        max_depth=max_depth,
        filter_substring=filter_substring,
    )


def load_config(config_path: str | Path) -> AppConfig:
    """Загружает и валидирует конфигурацию из TOML-файла."""
    path = Path(config_path)
    if not path.is_file():
        raise ConfigError(f"Файл конфигурации не найден: {path}")
    try:
        raw_bytes = path.read_bytes()
        data = tomllib.loads(raw_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"Ошибка чтения TOML-файла: {exc}") from exc
    return parse_config_dict(data)
