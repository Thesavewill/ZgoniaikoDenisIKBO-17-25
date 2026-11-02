"""Модуль для построения графа зависимостей пакетов."""

import re

from src.fetcher import FetchError, fetch_package_data


def _clean_version(version: str) -> str:
    """Очищает строку версии от спецсимволов npm."""
    match = re.search(r"(\d+\.\d+\.\d+)", version)
    return match.group(1) if match else "latest"


def build_dependency_graph(
    start_pkg: str,
    start_ver: str,
    repo: str,
    test_mode: bool,
    max_depth: int,
    filter_sub: str,
) -> dict[str, list[str]]:
    """Строит граф зависимостей с помощью итеративного DFS."""
    graph: dict[str, list[str]] = {}
    visited: set[str] = set()
    stack: list[tuple[str, str, int]] = [(start_pkg, start_ver, 1)]

    while stack:
        pkg_name, pkg_ver, depth = stack.pop()
        
        if pkg_name in visited:
            continue
            
        visited.add(pkg_name)
        graph[pkg_name] = []

        if depth >= max_depth:
            continue

        try:
            deps = fetch_package_data(repo, pkg_name, pkg_ver, test_mode)
        except FetchError:
            continue

        for dep_name, dep_ver in deps.items():
            if filter_sub and filter_sub in dep_name:
                continue
                
            graph[pkg_name].append(dep_name)
            clean_ver = _clean_version(dep_ver)
            stack.append((dep_name, clean_ver, depth + 1))

    return graph