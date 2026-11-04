"""Модуль для получения зависимостей пакетов из npm-репозитория."""

import json
import urllib.error
import urllib.request


class FetchError(Exception):
    """Исключение при ошибках получения данных пакета."""


def _fetch_test_data(repo_path: str, pkg_name: str) -> dict[str, str]:
    """Получает зависимости из локального тестового файла."""
    try:
        with open(repo_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        pkg_data = data.get(pkg_name, {})
        return pkg_data.get("dependencies", {})
    except (OSError, json.JSONDecodeError) as exc:
        raise FetchError(f"Ошибка чтения файла {repo_path}: {exc}") from exc


def fetch_package_data(
    repository: str, package_name: str, version: str, test_mode: bool
) -> dict[str, str]:
    """Получает прямые зависимости пакета."""
    if test_mode:
        return _fetch_test_data(repository, package_name)

    url = f"{repository.rstrip('/')}/{package_name}/{version}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise FetchError(f"Ошибка загрузки {package_name}: {exc}") from exc

    return data.get("dependencies", {})
