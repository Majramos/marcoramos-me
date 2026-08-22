from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import TypeAlias

from jinja2 import Environment, FileSystemLoader, select_autoescape

from scripts.constants import PAGES, TEMPLATES, DATA, BUILD, STATIC
from scripts.minify import minify_file
from scripts.minifiers import CSSMinimizer, HTMLMinimizer, JavaScriptMinimizer


JsonValue: TypeAlias = (
    None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
)


def _reset_build_dir(build_dir: Path) -> None:
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)


def _load_data(data_dir: Path) -> dict[str, JsonValue]:
    data: dict[str, JsonValue] = {}

    for file in data_dir.glob("**/*.json"):
        data[file.stem] = json.loads(file.read_text(encoding="utf-8"))

    return data


def _load_environment(templates_path: list[Path]) -> Environment:
    return Environment(
        loader=FileSystemLoader(templates_path),
        autoescape=select_autoescape(["html", "xml"]),
    )


def _find_pages(pages_dir: Path) -> list[str]:
    return [p.name for p in pages_dir.glob("**/*.html")]


def _build_page(page: str, *, env: Environment, data: dict[str, JsonValue]) -> None:
    html = env.get_template(page).render(**data)
    _ = (BUILD / page).write_text(html, encoding="utf-8")


def _minify_build_files(build_dir: Path) -> None:
    minifiers = {
        ".css": CSSMinimizer(),
        ".html": HTMLMinimizer(),
        ".js": JavaScriptMinimizer(),
    }

    for file in build_dir.rglob("*"):
        if file.is_file() and file.suffix in minifiers:
            minify_file(file, minifiers[file.suffix], override=True)


def build_site() -> None:
    data = _load_data(DATA)

    _reset_build_dir(BUILD)

    env = _load_environment([PAGES, TEMPLATES])

    for page in _find_pages(PAGES):
        _build_page(page, env=env, data=data)

    _ = shutil.copytree(STATIC, BUILD, dirs_exist_ok=True)
    _minify_build_files(BUILD)


if __name__ == "__main__":
    build_site()
