from __future__ import annotations

import json
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
DIST = ROOT / "dist"


def build_site() -> None:
    data = json.loads((SRC / "data" / "site.json").read_text(encoding="utf-8"))

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(SRC / "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )

    html = env.get_template("index.html").render(**data)
    (DIST / "index.html").write_text(html, encoding="utf-8")

    shutil.copytree(SRC / "static", DIST, dirs_exist_ok=True)


if __name__ == "__main__":
    build_site()
