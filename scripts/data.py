import json
from pathlib import Path
from typing import TypeAlias


JsonValue: TypeAlias = (
    None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
)


def load_data(data_dir: Path) -> dict[str, JsonValue]:
    data: dict[str, JsonValue] = {}

    for file in data_dir.glob("**/*.json"):
        data[file.stem] = json.loads(file.read_text(encoding="utf-8"))

    return data
