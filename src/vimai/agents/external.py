"""Run non-interactive external agent command wrappers."""

from pathlib import Path
import subprocess
import tempfile

from .loader import normalize_agent_name


class ExternalAgentError(Exception):
    """Raised when an external agent wrapper cannot be run successfully."""


def invoke_external_agent(
    external_agents_dir: Path | str, agent_name: str, prompt: str
) -> str:
    """Run an external agent wrapper and return captured stdout/stderr.

    The wrapper contract is:
        <external_agents_dir>/<agent_name>/run-agent --prompt-file <tempfile>

    The prompt is always written to a UTF-8 temporary file so multiline content
    is not embedded in shell arguments.
    """
    normalized_name = normalize_agent_name(agent_name)
    wrapper = Path(external_agents_dir).expanduser() / normalized_name / "run-agent"
    if not wrapper.is_file():
        raise ExternalAgentError(
            f"No prompt-only agent found for @{normalized_name}, and no external "
            f"run-agent wrapper found at {wrapper}."
        )

    prompt_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            delete=False,
            prefix=f"vimai-{normalized_name}-",
            suffix=".prompt.txt",
        ) as prompt_file:
            prompt_file.write(prompt)
            prompt_path = Path(prompt_file.name)

        result = subprocess.run(
            [str(wrapper), "--prompt-file", str(prompt_path)],
            capture_output=True,
            check=False,
            encoding="utf-8",
            text=True,
        )
    except OSError as exc:
        raise ExternalAgentError(
            f"Failed to run external agent @{normalized_name} at {wrapper}: {exc}"
        ) from exc
    finally:
        if prompt_path is not None:
            prompt_path.unlink(missing_ok=True)

    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "no output"
        raise ExternalAgentError(
            f"External agent @{normalized_name} exited with code "
            f"{result.returncode}: {detail}"
        )

    return _combine_output(result.stdout, result.stderr)


def _combine_output(stdout: str, stderr: str) -> str:
    parts = [stream.rstrip("\n") for stream in (stdout, stderr) if stream]
    return "\n".join(parts)
