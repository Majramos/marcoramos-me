from __future__ import annotations

import json
import shutil

from jinja2 import Environment, FileSystemLoader, select_autoescape

from scripts.constants import SRC, BUILD


def build_site() -> None:
    data = json.loads((SRC / "data" / "site.json").read_text(encoding="utf-8"))

    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(SRC / "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )

    html = env.get_template("index.html").render(**data)
    (BUILD / "index.html").write_text(html, encoding="utf-8")

    shutil.copytree(SRC / "static", BUILD, dirs_exist_ok=True)


if __name__ == "__main__":
    build_site()
