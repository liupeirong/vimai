"""CLI entry point called by Vim via :! shell integration (F01, F03, F04).

Usage:
    python main.py '<prompt>'
    python main.py --session /tmp/vimai-session-....tmp '<prompt>'
    python main.py --command clear --session /tmp/vimai-session-....tmp
    python main.py --command purge --session /tmp/vimai-session-....tmp
    python main.py --command help

    The Vim plugin passes slash commands via --command <name> (without the
    leading /) to avoid MSYS2/Git Bash converting '/word' positional args
    to Windows file paths.

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
    parser.add_argument(
        "--prompt-file",
        default=None,
        help="Path to a UTF-8 file containing the prompt text.",
    )
    parser.add_argument(
        "--command",
        default=None,
        help="Slash command name without leading / (e.g. 'clear', 'purge', 'help'). "
        "Used by the Vim plugin to avoid MSYS2/Git Bash path conversion of /word args.",
    )
    return parser.parse_args()


def _resolve_prompt(args: argparse.Namespace) -> str | None:
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8")
    return args.prompt


def main() -> None:
    """Parse arguments, dispatch slash commands or invoke the LLM, and print output."""
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    args = _parse_args()

    session_path = Path(args.session) if args.session else None

    # --command flag: Vim plugin strips the leading '/' and passes just the name
    # (e.g. 'clear') to avoid MSYS2/Git Bash converting '/clear' to a Windows
    # path when it appears as a positional shell argument.
    if args.command:
        cmd_output = handle_command("/" + args.command.lstrip("/"), session_path)
        print(cmd_output)
        sys.exit(0)

    try:
        raw_prompt = _resolve_prompt(args)
    except Exception as exc:  # noqa: BLE001
        print(f"vimai error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not raw_prompt or not raw_prompt.strip():
        print("Usage: vimai '<prompt>'", file=sys.stderr)
        sys.exit(1)

    prompt = raw_prompt.strip()

    # Also handle slash commands in the positional arg for direct CLI use on
    # Linux/macOS where MSYS2 path conversion is not a concern.
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
