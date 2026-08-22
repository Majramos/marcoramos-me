from pathlib import Path
from typing import Final


ROOT: Final[Path] = Path(__file__).resolve().parent.parent

SRC: Final[Path] = ROOT / "src"

PAGES: Final[Path] = SRC / "pages"

TEMPLATES: Final[Path] = SRC / "templates"

DATA: Final[Path] = SRC / "data"

STATIC: Final[Path] = SRC / "static"

BUILD: Final[Path] = ROOT / "build"


for dir in [DATA, PAGES, TEMPLATES, STATIC]:
    if not dir.exists():
        raise FileNotFoundError(f"Expected dir not found: {dir}")
