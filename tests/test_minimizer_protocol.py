from scripts.minifiers import (
    CSSMinimizer,
    HTMLMinimizer,
    JavaScriptMinimizer,
    StringMinimizer,
)


class UppercaseMinimizer:
    def minimize(self, content: str) -> str:
        return content.upper()


def test_string_minimizer_uses_structural_typing() -> None:
    minimizer: StringMinimizer = UppercaseMinimizer()

    assert minimizer.minimize("content") == "CONTENT"


def test_css_minimizer_implements_protocol() -> None:
    minimizer: StringMinimizer = CSSMinimizer()

    assert minimizer.minimize("body { color: red; }") == "body{color:red}"


def test_html_minimizer_implements_protocol() -> None:
    minimizer: StringMinimizer = HTMLMinimizer()

    assert minimizer.minimize("<p>  text </p>") == "<p> text </p>"


def test_javascript_minimizer_implements_protocol() -> None:
    minimizer: StringMinimizer = JavaScriptMinimizer()

    assert minimizer.minimize("const value = 1;") == "const value=1;"
