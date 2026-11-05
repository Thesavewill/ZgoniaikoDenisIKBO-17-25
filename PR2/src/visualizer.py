"""Модуль генерации кода Graphviz и рендеринга SVG-изображения."""

import subprocess


def generate_dot_source(graph: dict[str, list[str]]) -> str:
    """Генерирует текстовое представление графа на языке DOT."""
    lines = [
        "digraph G {",
        '  rankdir="TB";',
        '  splines="ortho";',
        '  nodesep=0.15;',
        '  ranksep=0.8;',
        '  node [shape="box", style="rounded", fontname="Helvetica"];',
        '  node [height=0.3];'
    ]

    for node, edges in graph.items():
        if not edges:
            lines.append(f'  "{node}";')
        else:
            for edge in edges:
                lines.append(f'  "{node}" -> "{edge}";')
    lines.append("}")
    return "\n".join(lines)


def render_svg(dot_source: str, output_path: str) -> None:
    """Рендерит DOT-код в SVG-файл с помощью утилиты dot."""
    try:
        subprocess.run(
            ["dot", "-Tsvg", "-o", output_path],
            input=dot_source.encode("utf-8"),
            check=True,
            capture_output=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Утилита 'dot' не найдена. Установите graphviz."
        ) from exc
    except subprocess.CalledProcessError as exc:
        err = exc.stderr.decode("utf-8")
        raise RuntimeError(f"Ошибка рендеринга Graphviz: {err}") from exc
    