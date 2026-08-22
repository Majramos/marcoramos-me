import re


from scripts.minifiers.protocol import StringMinimizer


class CSSMinimizer(StringMinimizer):
    def minimize(self, content: str) -> str:
        """Minimize a CSS source string.

        Steps:
          1. Strip /* ... */ comments
          2. Remove whitespace around CSS punctuation
          3. Collapse remaining whitespace runs to a single space
          4. Remove trailing semicolons before closing braces
          5. Trim leading/trailing whitespace
        """
        result = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
        result = re.sub(r"\s*([{}:;,>])\s*", r"\1", result)
        result = re.sub(r"\s+", " ", result)
        result = re.sub(r";+}", "}", result)
        return result.strip()
