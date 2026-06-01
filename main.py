import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from vimai import add_numbers


def main() -> None:
    print("hello world")
    print(add_numbers(2, 3))


if __name__ == "__main__":
    main()
