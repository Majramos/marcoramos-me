import json
from pathlib import Path

import pytest

from scripts.data import JsonValue, load_data


def write_json(path: Path, payload: JsonValue) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class TestDiscovery:
    def test_empty_directory_returns_empty_dict(self, tmp_path: Path) -> None:
        assert load_data(tmp_path) == {}

    def test_nonexistent_directory_returns_empty_dict(self, tmp_path: Path) -> None:
        assert load_data(tmp_path / "nope") == {}

    def test_single_file_at_top_level(self, tmp_path: Path) -> None:
        write_json(tmp_path / "config.json", {"debug": True})
        assert load_data(tmp_path) == {"config": {"debug": True}}

    def test_files_in_nested_subdirectories(self, tmp_path: Path) -> None:
        write_json(tmp_path / "a" / "one.json", 1)
        write_json(tmp_path / "a" / "b" / "two.json", 2)
        assert load_data(tmp_path) == {"one": 1, "two": 2}

    def test_non_json_files_are_ignored(self, tmp_path: Path) -> None:
        write_json(tmp_path / "data.json", [1, 2])
        (tmp_path / "notes.txt").write_text("not json", encoding="utf-8")
        (tmp_path / "data.json.bak").write_text("{}", encoding="utf-8")
        assert load_data(tmp_path) == {"data": [1, 2]}

    def test_duplicate_stems_last_glob_match_wins(self, tmp_path: Path) -> None:
        # Documents current behaviour: same stem in two dirs collides in the
        # result dict. pathlib's glob order is not guaranteed to be sorted,
        # so we only assert the key maps to one of the two payloads.
        write_json(tmp_path / "top" / "dup.json", "from_top")
        write_json(tmp_path / "nested" / "deeper" / "dup.json", "from_nested")
        result = load_data(tmp_path)
        assert set(result) == {"dup"}
        assert result["dup"] in {"from_top", "from_nested"}


class TestValueTypes:
    @pytest.mark.parametrize(
        "payload",
        [
            None,
            True,
            False,
            42,
            3.14,
            "hello",
            [],
            [1, "two", None, [3]],
            {},
            {"nested": {"list": [1, 2, {"deep": True}]}},
        ],
    )
    def test_top_level_json_value_types_round_trip(
        self, tmp_path: Path, payload: JsonValue
    ) -> None:
        write_json(tmp_path / "value.json", payload)
        assert load_data(tmp_path) == {"value": payload}

    def test_multiple_files_preserve_values(self, tmp_path: Path) -> None:
        write_json(tmp_path / "numbers.json", [1, 2, 3])
        write_json(tmp_path / "settings.json", {"theme": "dark", "level": 7})
        write_json(tmp_path / "empty_object.json", {})
        assert load_data(tmp_path) == {
            "numbers": [1, 2, 3],
            "settings": {"theme": "dark", "level": 7},
            "empty_object": {},
        }


class TestErrors:
    def test_invalid_json_raises_decode_error(self, tmp_path: Path) -> None:
        (tmp_path / "broken.json").write_text("{not valid json", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            load_data(tmp_path)

    def test_invalid_utf8_raises_unicode_decode_error(self, tmp_path: Path) -> None:
        (tmp_path / "binary.json").write_bytes(b"\xff\xfe\x00")
        with pytest.raises(UnicodeDecodeError):
            load_data(tmp_path)
