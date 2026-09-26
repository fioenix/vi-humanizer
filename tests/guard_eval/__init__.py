"""Tests for the guard evaluation harness.

`unittest discover -s tests` imports this directory as top-level package
``guard_eval``. Extend that package path to the production source directory so
the approved discovery command cannot shadow the code under test.
"""

from pathlib import Path


_SOURCE_PACKAGE = Path(__file__).resolve().parents[2] / "guard_eval"
if str(_SOURCE_PACKAGE) not in __path__:
    __path__.append(str(_SOURCE_PACKAGE))
