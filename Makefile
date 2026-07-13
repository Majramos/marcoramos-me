.RECIPEPREFIX := $() $()

.PHONY: ping lint style test verify build

ping:
    ping -c 3 marcoramos.me

lint:
    ruff check .

style:
    mypy scripts tests

test:
    uv run pytest

verify: lint style test

build:
    python scripts/build.py
