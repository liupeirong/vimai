import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vimai import add_numbers


def test_add_numbers_returns_sum() -> None:
    assert add_numbers(2, 3) == 5
