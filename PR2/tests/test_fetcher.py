"""Модульные тесты модуля получения зависимостей."""

import unittest
import urllib.error
from unittest.mock import MagicMock, patch

from src.fetcher import FetchError, fetch_package_data


class TestFetcher(unittest.TestCase):
    """Тесты для функции fetch_package_data."""

    @patch("urllib.request.urlopen")
    def test_fetch_success(self, mock_urlopen: MagicMock) -> None:
        """Проверяет успешное извлечение зависимостей."""
        mock_response = MagicMock()
        mock_response.read.return_value = (
            b'{"dependencies": {"accepts": "~1.3.8"}}'
        )
        mock_urlopen.return_value.__enter__.return_value = mock_response

        deps = fetch_package_data("http://reg.com", "express", "4.19.2")
        self.assertEqual(deps, {"accepts": "~1.3.8"})

    @patch("urllib.request.urlopen")
    def test_fetch_network_error(self, mock_urlopen: MagicMock) -> None:
        """Проверяет обработку сетевой ошибки."""
        mock_urlopen.side_effect = urllib.error.URLError("Network error")

        with self.assertRaises(FetchError):
            fetch_package_data("http://reg.com", "pkg", "1.0.0")


if __name__ == "__main__":
    unittest.main()