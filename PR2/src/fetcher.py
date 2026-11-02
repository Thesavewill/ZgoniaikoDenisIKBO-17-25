"""Модуль для получения зависимостей пакетов из npm-репозитория."""

import json
import urllib.error
import urllib.request


class FetchError(Exception):
    """Исключение при ошибках получения данных пакета."""


def fetch_package_data(
    registry_url: str, package_name: str, version: str
) -> dict[str, str]:
    """
    Получает прямые зависимости для заданной версии пакета.

    Args:
        registry_url: Базовый URL репозитория.
        package_name: Имя npm пакета.
        version: Версия пакета.

    Returns:
        Словарь прямых зависимостей {имя: версия}.
    """
    url = f"{registry_url.rstrip('/')}/{package_name}/{version}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise FetchError(f"Ошибка загрузки {package_name}: {exc}") from exc

    return data.get("dependencies", {})