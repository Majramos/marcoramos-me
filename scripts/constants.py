from pathlib import Path
from typing import Final

ROOT: Final[Path] = Path(__file__).resolve().parent.parent

SRC: Final[Path] = ROOT / "src"

BUILD: Final[Path] = ROOT / "build"
