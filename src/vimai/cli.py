"""CLI entry point called by Vim via :! shell integration (F01, F03).

Usage:
    python main.py '<prompt>'
    python main.py --session /tmp/vimai-session-....tmp '<prompt>'

Prints the LLM response to stdout (Vim displays it like :!ls output).
Exits 0 on success, 1 on any error.
"""

import argparse
import sys
from pathlib import Path

from .config import ConfigError, load_config
from .chain import invoke_chain, invoke_chain_with_history


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="vimai", add_help=False)
    parser.add_argument("prompt", nargs="?", default=None)
    parser.add_argument("--session", default=None, help="Path to session JSON file")
    return parser.parse_args()


def main() -> None:
    """Parse arguments, invoke the LLM, and print the response."""
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    args = _parse_args()

    if not args.prompt or not args.prompt.strip():
        print("Usage: vimai '<prompt>'", file=sys.stderr)
        sys.exit(1)

    prompt = args.prompt.strip()

    try:
        config = load_config()
        if args.session:
            response = invoke_chain_with_history(config, Path(args.session), prompt)
        else:
            response = invoke_chain(config, prompt)
        print(response)
        sys.exit(0)
    except ConfigError as exc:
        print(f"vimai config error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        print(f"vimai error: {exc}", file=sys.stderr)
        sys.exit(1)
