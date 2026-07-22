from scripts.css_minifier import minify_css, minify_file


class TestCommentRemoval:
    def test_removes_single_line_comment(self):
        css = "/* comment */body{color:red}"
        assert minify_css(css) == "body{color:red}"

    def test_removes_multi_line_comment(self):
        css = "/* line 1\nline 2 */body{color:red}"
        assert minify_css(css) == "body{color:red}"

    def test_removes_comment_at_end(self):
        css = "body{color:red}/* trailing */"
        assert minify_css(css) == "body{color:red}"

    def test_removes_multiple_comments(self):
        css = "/* a */body{color:red}/* b */p{margin:0}"
        assert minify_css(css) == "body{color:red}p{margin:0}"

    def test_removes_comment_inside_rule(self):
        css = "body{/* inline */color:red}"
        assert minify_css(css) == "body{color:red}"

    def test_only_comment_returns_empty(self):
        assert minify_css("/* just a comment */") == ""


class TestWhitespace:
    def test_removes_space_around_braces(self):
        assert minify_css("body { color:red }") == "body{color:red}"

    def test_removes_space_around_colons(self):
        assert minify_css("body{color : red}") == "body{color:red}"

    def test_removes_space_around_semicolons(self):
        assert minify_css("body{color:red ; margin:0}") == "body{color:red;margin:0}"

    def test_removes_space_around_commas(self):
        css = "body{font-family:Arial , sans-serif}"
        assert minify_css(css) == "body{font-family:Arial,sans-serif}"

    def test_removes_space_around_child_selector(self):
        assert minify_css("div > p{color:red}") == "div>p{color:red}"

    def test_collapses_multiple_spaces(self):
        assert minify_css("body{    color:    red}") == "body{color:red}"

    def test_collapses_newlines_and_tabs(self):
        css = "body{\n\tcolor:red;\n\tmargin:0\n}"
        assert minify_css(css) == "body{color:red;margin:0}"

    def test_preserves_space_inside_values(self):
        assert minify_css("body{margin:0 auto}") == "body{margin:0 auto}"

    def test_preserves_space_in_font_shorthand(self):
        css = "body{font:16px/1.5 Arial, sans-serif}"
        assert minify_css(css) == "body{font:16px/1.5 Arial,sans-serif}"

    def test_strips_leading_trailing_whitespace(self):
        assert minify_css("  body{color:red}  ") == "body{color:red}"


class TestTrailingSemicolons:
    def test_removes_trailing_semicolon_before_brace(self):
        assert minify_css("body{color:red;}") == "body{color:red}"

    def test_keeps_internal_semicolons(self):
        assert minify_css("body{color:red;margin:0}") == "body{color:red;margin:0}"

    def test_removes_multiple_trailing_semicolons(self):
        assert minify_css("body{color:red;;}") == "body{color:red}"

    def test_trailing_semicolon_with_whitespace(self):
        assert minify_css("body{color:red ; }") == "body{color:red}"


class TestEdgeCases:
    def test_empty_string(self):
        assert minify_css("") == ""

    def test_only_whitespace(self):
        assert minify_css("   \n\t  ") == ""

    def test_already_minified(self):
        css = "body{color:red}"
        assert minify_css(css) == "body{color:red}"

    def test_no_whitespace_to_remove(self):
        assert minify_css("a{b:c}") == "a{b:c}"

    def test_media_query(self):
        css = "@media (max-width: 600px) { body { color: red; } }"
        assert minify_css(css) == "@media (max-width:600px){body{color:red}}"

    def test_multiple_selectors(self):
        css = "h1, h2, h3 { color: blue; }"
        assert minify_css(css) == "h1,h2,h3{color:blue}"

    def test_nested_rules(self):
        css = ".parent { color: red; } .child { margin: 0; }"
        assert minify_css(css) == ".parent{color:red}.child{margin:0}"

    def test_preserves_hex_colors(self):
        css = "body{color:#333333;background:#fff}"
        assert minify_css(css) == "body{color:#333333;background:#fff}"

    def test_preserves_important(self):
        css = "body{color:red !important}"
        assert minify_css(css) == "body{color:red !important}"

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
        assert minify_css(css) == expected


class TestMinifyFile:
    def test_writes_to_custom_output_path(self, tmp_path):
        src = tmp_path / "input.css"
        src.write_text("body { color: red; }")
        dst = tmp_path / "output.css"

        result = minify_file(str(src), str(dst))

        assert result == "body{color:red}"
        assert dst.read_text() == "body{color:red}"

    def test_default_output_path_creates_min_suffix(self, tmp_path):
        src = tmp_path / "styles.css"
        src.write_text("body { color: red; }")

        result = minify_file(str(src))

        expected_path = tmp_path / "styles.min.css"
        assert expected_path.exists()
        assert expected_path.read_text() == "body{color:red}"
        assert result == "body{color:red}"

    def test_default_output_path_no_extension(self, tmp_path):
        src = tmp_path / "styles"
        src.write_text("body { color: red; }")

        result = minify_file(str(src))

        expected_path = tmp_path / "styles.min.css"
        assert expected_path.exists()
        assert result == "body{color:red}"

    def test_returns_minified_string(self, tmp_path):
        src = tmp_path / "input.css"
        src.write_text("div > p { margin: 0 auto; }")

        result = minify_file(str(src), str(tmp_path / "out.css"))

        assert isinstance(result, str)
        assert result == "div>p{margin:0 auto}"

    def test_preserves_utf8_content(self, tmp_path):
        src = tmp_path / "input.css"
        src.write_text("body{content:'café — naïve'}", encoding="utf-8")
        dst = tmp_path / "out.css"

        result = minify_file(str(src), str(dst))

        assert "café" in result
        assert dst.read_text(encoding="utf-8") == result

    def test_empty_file(self, tmp_path):
        src = tmp_path / "empty.css"
        src.write_text("")

        result = minify_file(str(src), str(tmp_path / "out.css"))

        assert result == ""

    def test_file_with_only_comments(self, tmp_path):
        src = tmp_path / "comments.css"
        src.write_text("/* nothing here */\n/* really */")

        result = minify_file(str(src), str(tmp_path / "out.css"))

        assert result == ""

    def test_overwrites_existing_output(self, tmp_path):
        src = tmp_path / "input.css"
        src.write_text("body{color:red}")
        dst = tmp_path / "out.css"
        dst.write_text("OLD CONTENT")

        result = minify_file(str(src), str(dst))

        assert result == "body{color:red}"
        assert dst.read_text() == "body{color:red}"

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
        dst = tmp_path / "big.min.css"

        result = minify_file(str(src), str(dst))

        expected = (
            "*{margin:0;padding:0;box-sizing:border-box}"
            "body{font-family:Arial,sans-serif;background-color:#ffffff;color:#333333}"
            "@media (max-width:768px){body{font-size:14px}}"
        )
        assert result == expected
        assert dst.read_text() == expected
