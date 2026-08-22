from scripts.minifiers.protocol import StringMinimizer


class JavaScriptMinimizer(StringMinimizer):
    def minimize(self, content: str) -> str:
        return _minimize_javascript(content)


def _minimize_javascript(source: str) -> str:
    """Minify JavaScript by removing comments and unnecessary whitespace.

    This is a lightweight lexer-based minifier, not a full JavaScript parser.
    It preserves quoted strings, template literals, and regex literals.

    Args:
        source: JavaScript source code.

    Returns:
        Minified JavaScript source code.

    Raises:
        TypeError: If source is not a string.
        ValueError: If source contains an unterminated comment or string.
    """

    length = len(source)
    tokens: list[tuple[str, str]] = []
    i = 0

    keywords_allowing_regex = {
        "return",
        "throw",
        "case",
        "delete",
        "void",
        "typeof",
        "new",
        "in",
        "of",
        "yield",
        "await",
        "else",
        "do",
        "instanceof",
    }

    def previous_token() -> tuple[str, str] | None:
        return tokens[-1] if tokens else None

    def can_start_regex() -> bool:
        previous = previous_token()

        if previous is None:
            return True

        kind, value = previous

        if kind == "word" and value in keywords_allowing_regex:
            return True

        if kind == "punct":
            return value not in {")", "]", "}", "++", "--"}

        return False

    def read_quoted(start: int, quote: str) -> tuple[str, int]:
        cursor = start + 1

        while cursor < length:
            char = source[cursor]

            if char == "\\":
                cursor += 2
                continue

            if char == quote:
                return source[start : cursor + 1], cursor + 1

            if char in "\r\n" and quote != "`":
                raise ValueError("unterminated string literal")

            cursor += 1

        raise ValueError("unterminated string or template literal")

    def read_regex(start: int) -> tuple[str, int]:
        cursor = start + 1
        in_character_class = False

        while cursor < length:
            char = source[cursor]

            if char == "\\":
                cursor += 2
                continue

            if char == "[":
                in_character_class = True
            elif char == "]":
                in_character_class = False
            elif char == "/" and not in_character_class:
                cursor += 1

                while cursor < length and source[cursor].isalpha():
                    cursor += 1

                return source[start:cursor], cursor
            elif char in "\r\n":
                raise ValueError("unterminated regular expression literal")

            cursor += 1

        raise ValueError("unterminated regular expression literal")

    while i < length:
        char = source[i]
        next_char = source[i + 1] if i + 1 < length else ""

        # Remove whitespace. Token rendering later restores required spaces.
        if char.isspace():
            i += 1
            continue

        # Remove // comments.
        if char == "/" and next_char == "/":
            i += 2
            while i < length and source[i] not in "\r\n":
                i += 1
            continue

        # Remove /* ... */ comments.
        if char == "/" and next_char == "*":
            end = source.find("*/", i + 2)
            if end == -1:
                raise ValueError("unterminated block comment")
            i = end + 2
            continue

        # Preserve regular quoted strings and template literals.
        if char in {"'", '"', "`"}:
            value, i = read_quoted(i, char)
            tokens.append(("string", value))
            continue

        # Preserve regex literals, e.g. /hello\s+world/gi.
        if char == "/" and can_start_regex():
            value, i = read_regex(i)
            tokens.append(("regex", value))
            continue

        # JavaScript identifiers, keywords, and numeric literals.
        if char.isalnum() or char in {"_", "$"}:
            start = i
            i += 1

            while i < length and (source[i].isalnum() or source[i] in {"_", "$", "."}):
                i += 1

            tokens.append(("word", source[start:i]))
            continue

        # Keep multi-character operators together.
        three_char_operators = {
            "===",
            "!==",
            ">>>",
            "**=",
            "&&=",
            "||=",
            "??=",
            "<<=",
            ">>=",
            ">>>",
        }
        two_char_operators = {
            "==",
            "!=",
            "<=",
            ">=",
            "++",
            "--",
            "&&",
            "||",
            "??",
            "=>",
            "**",
            "<<",
            ">>",
            "+=",
            "-=",
            "*=",
            "/=",
            "%=",
            "&=",
            "|=",
            "^=",
            "?.",
            "??",
        }

        candidate = source[i : i + 3]
        if candidate in three_char_operators:
            tokens.append(("punct", candidate))
            i += 3
            continue

        candidate = source[i : i + 2]
        if candidate in two_char_operators:
            tokens.append(("punct", candidate))
            i += 2
            continue

        tokens.append(("punct", char))
        i += 1

    def needs_space(
        previous: tuple[str, str] | None,
        current: tuple[str, str],
    ) -> bool:
        if previous is None:
            return False

        previous_kind, previous_value = previous
        current_kind, current_value = current

        # `const value`, `return result`, `123 abc`, etc.
        if previous_kind == "word" and current_kind == "word":
            return True

        # Avoid creating ++, --, or accidental comment starts.
        combined = previous_value[-1:] + current_value[:1]
        if combined in {"++", "--", "//", "/*"}:
            return True

        # Avoid joining a keyword/identifier and a quoted literal.
        if previous_kind == "word" and current_kind in {"string", "regex"}:
            return True

        if previous_kind in {"string", "regex"} and current_kind == "word":
            return True

        return False

    result: list[str] = []
    previous: tuple[str, str] | None = None

    for token in tokens:
        if needs_space(previous, token):
            result.append(" ")

        result.append(token[1])
        previous = token

    return "".join(result)
