import re


def minify_css(source: str) -> str:
    """
    Minify a CSS source string.

    Steps:
      1. Strip /* ... */ comments
      2. Remove whitespace around braces, colons, semicolons, commas, >
      3. Collapse remaining whitespace runs to a single space
      4. Remove trailing semicolons before closing braces
      5. Trim leading/trailing whitespace
    """
    result = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    result = re.sub(r"\s*([{}:;,>])\s*", r"\1", result)
    result = re.sub(r"\s+", " ", result)
    result = re.sub(r";+}", "}", result)
    return result.strip()


def minify_file(input_path: str, output_path: str | None = None) -> str:
    """
    Minify a CSS file on disk.

    Args:
        input_path:  Path to the source .css file.
        output_path: Destination for the minified CSS.
                     If None, writes alongside the original with a
                     ``.min.css`` suffix.

    Returns:
        The minified CSS string.
    """
    with open(input_path, "r", encoding="utf-8") as f:
        source = f.read()

    minified = minify_css(source)

    if output_path is None:
        if "." in input_path:
            base, ext = input_path.rsplit(".", 1)
        else:
            base, ext = input_path, "css"
        output_path = f"{base}.min.{ext}"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(minified)

    return minified


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python css_minifier.py <input.css> [output.css]")
        sys.exit(1)

    out = minify_file(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(out)
