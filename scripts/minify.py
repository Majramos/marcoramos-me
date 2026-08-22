from pathlib import Path

from scripts.minifiers.protocol import StringMinimizer


def minify_file(
    input_path: Path,
    minimizer: StringMinimizer,
    override: bool = False,
) -> None:
    """
    Minimize a file on disk.

    Args:
        input_path: Path to the source file.
        minimizer: Minifier that processes the file content.
        override: If True, replace the source file.
    """
    source = input_path.read_text(encoding="utf-8")
    minified = minimizer.minimize(source)

    output_path = input_path
    if not override:
        output_path = input_path.with_name(f"{input_path.stem}.min{input_path.suffix}")

    _ = output_path.write_text(minified, encoding="utf-8")
