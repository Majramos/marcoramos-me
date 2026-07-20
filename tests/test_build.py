from pathlib import Path

from scripts.build import build_site


def test_build_creates_index() -> None:
    build_site()
    index_file = Path("build/index.html")
    assert index_file.exists()


def test_build_copies_css() -> None:
    build_site()
    css_file = Path("build/css/style.css")
    assert css_file.exists()


def test_rendered_html_contains_title() -> None:
    build_site()
    html = Path("build/index.html").read_text(encoding="utf-8")
    assert "<title>Marco Ramos</title>" in html
