from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_repo_file(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_plugin_prefers_checkout_venv_and_allows_python_override() -> None:
    plugin = read_repo_file("plugin/vimai.vim")

    assert "function! s:ResolvePythonCommand() abort" in plugin
    assert "g:vimai_python" in plugin
    assert "VIMAI_PYTHON" in plugin
    assert ".venv/Scripts/python.exe" in plugin
    assert ".venv/bin/python" in plugin
    assert "shellescape(s:python_cmd)" in plugin


def test_distribution_files_are_in_source_manifest() -> None:
    manifest = read_repo_file("MANIFEST.in")

    assert "include main.py" in manifest
    assert "recursive-include plugin *.vim" in manifest
    assert "recursive-include doc *.txt" in manifest


def test_console_script_entry_point_is_declared() -> None:
    pyproject = read_repo_file("pyproject.toml")

    assert "[project.scripts]" in pyproject
    assert 'vimai = "vimai.cli:main"' in pyproject
