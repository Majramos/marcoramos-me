from typing import Protocol


class StringMinimizer(Protocol):
    def minimize(self, content: str) -> str:
        """Return a minimized version of string content."""
