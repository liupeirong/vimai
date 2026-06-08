## Framework

- Use langchain, langgraph, langsmith for generative AI programming
- Use Entra ID for authentication

## Module Layout

```
src/vimai/
  __init__.py
  config.py         # Env var loading + validation (F05)
  llm.py            # ChatOpenAI setup with DefaultAzureCredential (F05)
  session.py        # Session file lifecycle - create, append, close, purge (F03)
  chain.py          # LangChain chain invocation with session history (F01)
  commands.py       # /clear, /purge, /help subcommand handlers (F04)
  cli.py            # CLI entry point called by Vim via :! shell (F01)
  agents/
    __init__.py
    loader.py       # Loads ~/.vimai/agents/<name>.md as system prompt (F07)
    external.py     # Runs <VIMAI_EXTERNAL_AGENTS_DIR>/<name>/run-agent wrappers (F09)
  builtin_agents/
    vi.md           # Bundled Vim expert system prompt (F07)

~/.vimai/agents/
  <name>.md         # User-defined agents; overrides bundled agents by name

<VIMAI_EXTERNAL_AGENTS_DIR>/
  <name>/
    run-agent       # External non-interactive agent wrapper; accepts --prompt-file
    run-agent.bat   # Windows alternative

plugin/
  vimai.vim         # Vim plugin: :AI command, cabbrev, scratch buffer, autocommand (F01,F02,F04,F08)

doc/
  vimai.txt         # Vim help documentation for packaged installs (F10)

main.py             # Thin wrapper: calls cli.main()
tests/
  test_config.py
  test_session.py
  test_chain.py
  test_commands.py
  test_agents.py
  e2e/
    test_e2e.py     # Gated behind RUN_E2E=1
```

## Key Abstractions

- **Config** (`config.py`): Dataclass holding all env var values. Raises `ConfigError` with clear message if required vars are missing.
- **Session** (`session.py`): Manages one active JSON tmp file per Vim PID. Entries are `{role, content, timestamp}`. Exposes `get_or_create()`, `append()`, `clear()`, `purge_all()`.
- **Chain** (`chain.py`): Wraps LangChain `ChatOpenAI`. Accepts a list of session messages + new prompt, returns response string.
- **CLI** (`cli.py`): Parses `sys.argv`, dispatches to chain or subcommands, prints to stdout (Vim reads this as `:!` output).
- **Agent loader** (`agents/loader.py`): Loads `~/.vimai/agents/<name>.md` first, then falls back to bundled prompts such as `builtin_agents/vi.md`. Agent calls are stateless single-turn.
- **External agent runner** (`agents/external.py`): Runs non-interactive `<VIMAI_EXTERNAL_AGENTS_DIR>/<name>/run-agent` wrappers with `--prompt-file <tempfile>` when no prompt-only agent exists. On Windows, `run-agent.bat` and `run-agent.cmd` are also accepted. External calls time out after 120 seconds.
- **Vim launcher** (`plugin/vimai.vim`): Resolves `main.py` relative to the installed plugin checkout, prefers the checkout-local `.venv` Python created by `uv sync`, and allows `g:vimai_python`, `VIMAI_PYTHON`, or `VIMAI_SCRIPT` overrides for custom installs.

## Data Flow

```
User types: :AI <prompt>
  → Vim runs: python main.py "<prompt>"
  → cli.py: parse args → load config → load session history → invoke chain
  → chain.py: build message list → call AzureChatOpenAI → return response
  → session.py: append prompt+response to session JSON file
  → cli.py: print response to stdout
  → Vim: displays stdout in command window (same as :!ls)

User types: :AI @vi <prompt>
  → F08/F09: Vim/CLI routing detects @vi
  → prompt-only agent lookup checks ~/.vimai/agents/vi.md, then bundled vi.md
  → if found: invoke_loaded_agent(config, agent, prompt)
  → if missing: run <VIMAI_EXTERNAL_AGENTS_DIR>/vi/run-agent --prompt-file <tempfile>
  → no session file modified

User types: :AI /clear
  → cli.py: detect /clear → session.clear() → print confirmation
```
