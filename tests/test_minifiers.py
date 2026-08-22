import pytest

from scripts.minifiers import CSSMinimizer, JavaScriptMinimizer
from scripts.minify import minify_file


css_minimizer = CSSMinimizer()
javascript_minimizer = JavaScriptMinimizer()


class TestJavaScriptMinimizer:
    def test_removes_comments_and_whitespace(self):
        javascript = "// header\nconst value = 1; /* inline */ return value;"

        assert javascript_minimizer.minimize(javascript) == (
            "const value=1;return value;"
        )

    def test_preserves_strings_and_template_literals(self):
        javascript = r"""const text = "// not a comment /* still text */"; const template = `line // still text`; const quote = 'it\'s';"""

        assert javascript_minimizer.minimize(javascript) == (
            r"""const text="// not a comment /* still text */";const template=`line // still text`;const quote='it\'s';"""
        )

    def test_preserves_regular_expression_character_classes_and_flags(self):
        javascript = r"const pattern = /hello\s+[a/]world/gi;"

        assert javascript_minimizer.minimize(javascript) == (
            r"const pattern=/hello\s+[a/]world/gi;"
        )

    def test_recognizes_regex_at_the_start(self):
        assert javascript_minimizer.minimize("/pattern/gi.test(value);") == (
            "/pattern/gi.test(value);"
        )

    def test_recognizes_regex_after_keyword(self):
        javascript = "function match(value) { return /test/.test(value); }"

        assert javascript_minimizer.minimize(javascript) == (
            "function match(value){return /test/.test(value);}"
        )

    def test_keeps_division_as_an_operator(self):
        javascript = "const result = value / 2;"

        assert javascript_minimizer.minimize(javascript) == "const result=value/2;"

    def test_rejects_newlines_in_string_literals(self):
        with pytest.raises(ValueError, match="unterminated string literal"):
            javascript_minimizer.minimize("const value = 'first\nsecond';")

    def test_rejects_newlines_in_regular_expression_literals(self):
        with pytest.raises(ValueError, match="unterminated regular expression literal"):
            javascript_minimizer.minimize("const value = /first\nsecond/;")

    def test_keeps_multi_character_operators_together(self):
        javascript = "const result = a === b && c !== d ?? e; value >>= 1;"

        assert javascript_minimizer.minimize(javascript) == (
            "const result=a===b&&c!==d??e;value>>=1;"
        )

    def test_preserves_required_token_spaces(self):
        javascript = "const value = 123 abc; const text = label 'value';"

        assert javascript_minimizer.minimize(javascript) == (
            "const value=123 abc;const text=label 'value';"
        )

    def test_preserves_space_between_literal_and_word(self):
        javascript = "const text = 'value' label; const pattern = /value/ label;"

        assert javascript_minimizer.minimize(javascript) == (
            "const text='value' label;const pattern=/value/ label;"
        )

    def test_prevents_accidental_operator_and_comment_tokens(self):
        javascript = "a + ++b; c - --d; e / /pattern/; f * /value/;"

        assert javascript_minimizer.minimize(javascript) == (
            "a+ ++b;c- --d;e/ /pattern/;f*/value/;"
        )

    @pytest.mark.parametrize(
        ("javascript", "message"),
        [
            ("const value = /* missing", "unterminated block comment"),
            ("const value = 'missing", "unterminated string or template literal"),
            ("const value = `missing", "unterminated string or template literal"),
            ("const value = /missing", "unterminated regular expression literal"),
        ],
    )
    def test_rejects_unterminated_literals_and_comments(self, javascript, message):
        with pytest.raises(ValueError, match=message):
            javascript_minimizer.minimize(javascript)


class TestCommentRemoval:
    def test_removes_single_line_comment(self):
        css = "/* comment */body{color:red}"
        assert css_minimizer.minimize(css) == "body{color:red}"

    def test_removes_multi_line_comment(self):
        css = "/* line 1\nline 2 */body{color:red}"
        assert css_minimizer.minimize(css) == "body{color:red}"

    def test_removes_comment_at_end(self):
        css = "body{color:red}/* trailing */"
        assert css_minimizer.minimize(css) == "body{color:red}"

    def test_removes_multiple_comments(self):
        css = "/* a */body{color:red}/* b */p{margin:0}"
        assert css_minimizer.minimize(css) == "body{color:red}p{margin:0}"

    def test_removes_comment_inside_rule(self):
        css = "body{/* inline */color:red}"
        assert css_minimizer.minimize(css) == "body{color:red}"

    def test_only_comment_returns_empty(self):
        assert css_minimizer.minimize("/* just a comment */") == ""


class TestWhitespace:
    def test_removes_space_around_braces(self):
        assert css_minimizer.minimize("body { color:red }") == "body{color:red}"

    def test_removes_space_around_colons(self):
        assert css_minimizer.minimize("body{color : red}") == "body{color:red}"

    def test_removes_space_around_semicolons(self):
        assert (
            css_minimizer.minimize("body{color:red ; margin:0}")
            == "body{color:red;margin:0}"
        )

    def test_removes_space_around_commas(self):
        css = "body{font-family:Arial , sans-serif}"
        assert css_minimizer.minimize(css) == "body{font-family:Arial,sans-serif}"

    def test_removes_space_around_child_selector(self):
        assert css_minimizer.minimize("div > p{color:red}") == "div>p{color:red}"

    def test_collapses_multiple_spaces(self):
        assert css_minimizer.minimize("body{    color:    red}") == "body{color:red}"

    def test_collapses_newlines_and_tabs(self):
        css = "body{\n\tcolor:red;\n\tmargin:0\n}"
        assert css_minimizer.minimize(css) == "body{color:red;margin:0}"

    def test_preserves_space_inside_values(self):
        assert css_minimizer.minimize("body{margin:0 auto}") == "body{margin:0 auto}"

    def test_preserves_space_in_font_shorthand(self):
        css = "body{font:16px/1.5 Arial, sans-serif}"
        assert css_minimizer.minimize(css) == "body{font:16px/1.5 Arial,sans-serif}"

    def test_strips_leading_trailing_whitespace(self):
        assert css_minimizer.minimize("  body{color:red}  ") == "body{color:red}"


class TestTrailingSemicolons:
    def test_removes_trailing_semicolon_before_brace(self):
        assert css_minimizer.minimize("body{color:red;}") == "body{color:red}"

    def test_keeps_internal_semicolons(self):
        assert (
            css_minimizer.minimize("body{color:red;margin:0}")
            == "body{color:red;margin:0}"
        )

    def test_removes_multiple_trailing_semicolons(self):
        assert css_minimizer.minimize("body{color:red;;}") == "body{color:red}"

    def test_trailing_semicolon_with_whitespace(self):
        assert css_minimizer.minimize("body{color:red ; }") == "body{color:red}"


class TestEdgeCases:
    def test_empty_string(self):
        assert css_minimizer.minimize("") == ""

    def test_only_whitespace(self):
        assert css_minimizer.minimize("   \n\t  ") == ""

    def test_already_minified(self):
        css = "body{color:red}"
        assert css_minimizer.minimize(css) == "body{color:red}"

    def test_no_whitespace_to_remove(self):
        assert css_minimizer.minimize("a{b:c}") == "a{b:c}"

    def test_media_query(self):
        css = "@media (max-width: 600px) { body { color: red; } }"
        assert (
            css_minimizer.minimize(css) == "@media (max-width:600px){body{color:red}}"
        )

    def test_multiple_selectors(self):
        css = "h1, h2, h3 { color: blue; }"
        assert css_minimizer.minimize(css) == "h1,h2,h3{color:blue}"

    def test_nested_rules(self):
        css = ".parent { color: red; } .child { margin: 0; }"
        assert css_minimizer.minimize(css) == ".parent{color:red}.child{margin:0}"

    def test_preserves_hex_colors(self):
        css = "body{color:#333333;background:#fff}"
        assert css_minimizer.minimize(css) == "body{color:#333333;background:#fff}"

    def test_preserves_important(self):
        css = "body{color:red !important}"
        assert css_minimizer.minimize(css) == "body{color:red !important}"

    def test_complex_stylesheet(self):
        css = """
            /* Reset */
            * { margin: 0; padding: 0; box-sizing: border-box; }

            body {
                font-family: Arial, sans-serif;
                background-color: #ffffff;
            }

            @media (max-width: 768px) {
                body { font-size: 14px; }
            }
        """
        expected = (
            "*{margin:0;padding:0;box-sizing:border-box}"
            "body{font-family:Arial,sans-serif;background-color:#ffffff}"
            "@media (max-width:768px){body{font-size:14px}}"
        )
        assert css_minimizer.minimize(css) == expected


class TestMinifyFile:
    def test_writes_to_minified_path(self, tmp_path):
        src = tmp_path / "input.css"
        src.write_text("body { color: red; }")

        minify_file(src, css_minimizer)

        assert src.with_name("input.min.css").read_text() == "body{color:red}"

    def test_override_replaces_source_file(self, tmp_path):
        src = tmp_path / "styles.css"
        src.write_text("body { color: red; }")

        minify_file(src, css_minimizer, override=True)

        assert src.read_text() == "body{color:red}"

    def test_adds_min_suffix_without_extension(self, tmp_path):
        src = tmp_path / "styles"
        src.write_text("body { color: red; }")

        minify_file(src, css_minimizer)

        expected_path = tmp_path / "styles.min"
        assert expected_path.exists()
        assert expected_path.read_text() == "body{color:red}"

    def test_preserves_utf8_content(self, tmp_path):
        src = tmp_path / "input.css"
        src.write_text("body{content:'café — naïve'}", encoding="utf-8")
        minify_file(src, css_minimizer)

        assert "café" in src.with_name("input.min.css").read_text(encoding="utf-8")

    def test_empty_file(self, tmp_path):
        src = tmp_path / "empty.css"
        src.write_text("")

        minify_file(src, css_minimizer)

        assert src.with_name("empty.min.css").read_text() == ""

    def test_file_with_only_comments(self, tmp_path):
        src = tmp_path / "comments.css"
        src.write_text("/* nothing here */\n/* really */")

        minify_file(src, css_minimizer)

        assert src.with_name("comments.min.css").read_text() == ""

    def test_overwrites_existing_output(self, tmp_path):
        src = tmp_path / "input.css"
        src.write_text("body{color:red}")
        src.with_name("input.min.css").write_text("OLD CONTENT")

        minify_file(src, css_minimizer)

        assert src.with_name("input.min.css").read_text() == "body{color:red}"

    def test_large_real_world_css(self, tmp_path):
        src = tmp_path / "big.css"
        src.write_text("""
            /* Reset */
            * { margin: 0; padding: 0; box-sizing: border-box; }

            /* Body */
            body {
                font-family: Arial, sans-serif;
                background-color: #ffffff;
                color: #333333;
            }

            @media (max-width: 768px) {
                body { font-size: 14px; }
            }
        """)
        minify_file(src, css_minimizer)

        expected = (
            "*{margin:0;padding:0;box-sizing:border-box}"
            "body{font-family:Arial,sans-serif;background-color:#ffffff;color:#333333}"
            "@media (max-width:768px){body{font-size:14px}}"
        )
        assert src.with_name("big.min.css").read_text() == expected
