import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


@pytest.mark.e2e
def test_main_invokes_cli(tmp_path: Path) -> None:
    """Smoke-test: main.py delegates to cli.main() (E2E, skipped without RUN_E2E=1)."""
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve().parents[1] / "main.py"), "hello"],
        capture_output=True,
        text=True,
    )
    # Without credentials this will exit 1, but the error must come from vimai
    assert "vimai" in result.stderr.lower() or result.returncode == 0
