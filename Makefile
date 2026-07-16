.RECIPEPREFIX := $() $()

.PHONY: install fmt lint style test verify build clean ping

install:
    uv sync

fmt:
    uv run ruff format .

lint:
    uv run ruff check .

style:
    uv run mypy src tests

test:
    uv run pytest

verify: lint style test

build:
    python scripts/build.py

clean:
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type d -name "*.pyc" -delete
    rm -rf .pytest_cache .ruff_cache .mypy_cache

ping:
    ping -c 3 marcoramos.me
