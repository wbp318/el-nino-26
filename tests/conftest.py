"""Make the `src/` modules importable as top-level modules in tests.

The pipeline scripts live in `src/` and are run as scripts, not installed as a
package, so the test suite puts `src/` on `sys.path` here (auto-loaded by pytest).
"""
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
