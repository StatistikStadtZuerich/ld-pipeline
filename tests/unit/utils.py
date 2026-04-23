import difflib
import os
import re

import pytest


class TestUtils:
    @staticmethod
    def abs_path(rel_path):
        return os.path.join(os.path.dirname(__file__), rel_path)

    @staticmethod
    def assert_text_equals(expected, actual, msg="", normalize=True):
        def _normalize_string(string: str) -> str:
            if not normalize:
                return string
            string = string.replace("\r\n", "\n")  # Windows line endings
            string = string.replace("\r", "\n")  # alte Mac line endings
            string = string.strip("\ufeff")  # BOM
            string = re.sub(
                r"\n[ \t]+\n", "\n\n", string
            )  # Leerzeilen mit Whitespace → echte Leerzeile
            string = re.sub(r"\n{3,}", "\n\n", string)  # 3+ Leerzeilen → max. eine
            return string.strip()

        _expected = _normalize_string(expected)
        _actual = _normalize_string(actual)

        if _expected == _actual:
            return

        diffs = difflib.unified_diff(
            _expected.splitlines(keepends=True),
            _actual.splitlines(keepends=True),
            fromfile="expected",
            tofile="actual",
            n=2,  # Zeilen Kontext
            lineterm="\n",
        )
        diff = "".join(diffs)
        pytest.fail(f"{msg}\n{diff}")
