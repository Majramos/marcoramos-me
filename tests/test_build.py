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


def test_build_minifies_html() -> None:
    build_site()
    html = Path("build/index.html").read_text(encoding="utf-8")
    assert "</head><body" in html


def test_build_minifies_css() -> None:
    build_site()
    css = Path("build/css/style.css").read_text(encoding="utf-8")
    assert "\n" not in css
    assert "body{" in css


def test_build_minifies_javascript() -> None:
    build_site()
    javascript = Path("build/js/script.js").read_text(encoding="utf-8")
    assert "\n" not in javascript
