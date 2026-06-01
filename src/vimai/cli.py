"""CLI entry point called by Vim via :! shell integration (F01).

Usage:
    python main.py '<prompt>'

Prints the LLM response to stdout (Vim displays it like :!ls output).
Exits 0 on success, 1 on any error.
"""

import sys

from .config import ConfigError, load_config
from .chain import invoke_chain


def main() -> None:
    """Parse arguments, invoke the LLM, and print the response."""
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print("Usage: vimai '<prompt>'", file=sys.stderr)
        sys.exit(1)

    prompt = sys.argv[1].strip()

    try:
        config = load_config()
        response = invoke_chain(config, prompt)
        print(response)
        sys.exit(0)
    except ConfigError as exc:
        print(f"vimai config error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        print(f"vimai error: {exc}", file=sys.stderr)
        sys.exit(1)
