"""Offline tests for the optional public TypeSafe advisor.

`unittest discover -s tests` imports this directory as top-level package
``advisor``. Extend that path to the production package so discovery does not
shadow the code under test.
"""

from pathlib import Path


_SOURCE_PACKAGE = Path(__file__).resolve().parents[2] / "advisor"
if str(_SOURCE_PACKAGE) not in __path__:
    __path__.append(str(_SOURCE_PACKAGE))
