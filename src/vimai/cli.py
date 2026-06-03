"""CLI entry point called by Vim via :! shell integration (F01, F03, F04).

Usage:
    python main.py '<prompt>'
    python main.py --session /tmp/vimai-session-....tmp '<prompt>'
    python main.py /clear --session /tmp/vimai-session-....tmp
    python main.py /purge --session /tmp/vimai-session-....tmp
    python main.py /help

Prints the LLM response (or command output) to stdout.
Exits 0 on success, 1 on any error.
"""

import argparse
import sys
from pathlib import Path

from .chain import invoke_chain, invoke_chain_with_history
from .commands import handle_command
from .config import ConfigError, load_config


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="vimai", add_help=False)
    parser.add_argument("prompt", nargs="?", default=None)
    parser.add_argument("--session", default=None, help="Path to session JSON file")
    return parser.parse_args()


def main() -> None:
    """Parse arguments, dispatch slash commands or invoke the LLM, and print output."""
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    args = _parse_args()

    if not args.prompt or not args.prompt.strip():
        print("Usage: vimai '<prompt>'", file=sys.stderr)
        sys.exit(1)

    prompt = args.prompt.strip()
    session_path = Path(args.session) if args.session else None

    # Dispatch slash commands before making any LLM call.
    cmd_output = handle_command(prompt, session_path)
    if cmd_output is not None:
        print(cmd_output)
        sys.exit(0)

    try:
        config = load_config()
        if session_path:
            response = invoke_chain_with_history(config, session_path, prompt)
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
