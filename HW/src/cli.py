"""Интерфейс командной строки для транслятора конфигурационного языка."""

import json
import sys

from .errors import ConfigError
from .parser import parse_config

EXIT_SUCCESS = 0
EXIT_ERROR = 1
JSON_INDENT = 2


def translate(text: str) -> str:
    """Преобразует текст конфигурации в отформатированную JSON-строку."""
    parsed = parse_config(text)
    return json.dumps(parsed, indent=JSON_INDENT, ensure_ascii=False)


def main() -> int:
    """Читает конфигурацию из stdin и выводит JSON в stdout."""
    source_text = sys.stdin.read().lstrip("\ufeff")
    try:
        output_json = translate(source_text)
    except ConfigError as exc:
        sys.stderr.write(f"Ошибка: {exc}\n")
        return EXIT_ERROR

    sys.stdout.write(f"{output_json}\n")
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())