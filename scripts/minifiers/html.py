import re

from scripts.minifiers.protocol import StringMinimizer


_RAW_TEXT_TAGS = {"pre", "textarea", "script", "style"}

_COMMENT_RE = re.compile(r"<!--(?!\[if)[\s\S]*?-->", re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]+>")
_TAG_NAME_RE = re.compile(r"^<\s*/?\s*([a-zA-Z0-9:-]+)")


class HTMLMinimizer(StringMinimizer):
    def minimize(self, content: str) -> str:
        """Minimize an HTML string without changing its meaningful text content.

        Removes ordinary HTML comments and collapses whitespace outside of
        pre, textarea, script, and style elements.

        Conditional comments such as <!--[if IE]> ... <![endif]--> are retained.
        """
        html = _COMMENT_RE.sub("", content)

        output: list[str] = []
        position = 0
        raw_tag: str | None = None

        for match in _TAG_RE.finditer(html):
            text = html[position : match.start()]
            tag = match.group(0)

            if raw_tag is None:
                text = re.sub(r"\s+", " ", text)
                if text:
                    output.append(text)

            else:
                output.append(text)

            output.append(tag)

            tag_name_match = _TAG_NAME_RE.match(tag)
            if tag_name_match:
                tag_name = tag_name_match.group(1).lower()
                is_closing_tag = tag.lstrip().startswith("</")

                if is_closing_tag and tag_name == raw_tag:
                    raw_tag = None
                elif not is_closing_tag and tag_name in _RAW_TEXT_TAGS:
                    raw_tag = tag_name

            position = match.end()

        remaining = html[position:]
        if raw_tag is None:
            remaining = re.sub(r"\s+", " ", remaining)

        output.append(remaining)

        minimized = "".join(output)
        minimized = re.sub(r">\s+<", "><", minimized)

        return minimized.strip()
