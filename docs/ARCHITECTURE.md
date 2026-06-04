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
  builtin_agents/
    vi.md           # Bundled Vim expert system prompt (F07)

~/.vimai/agents/
  <name>.md         # User-defined agents; overrides bundled agents by name

plugin/
  vimai.vim         # Vim plugin: :AI command, cabbrev, scratch buffer, autocommand (F01,F02,F04,F08)

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
  → F08: Vim/CLI routing detects @vi → invoke_agent("vi", prompt)
  → no session file modified

User types: :AI /clear
  → cli.py: detect /clear → session.clear() → print confirmation
```

## Error Handling Conventions

- Missing required env vars → `ConfigError` with exact var name and setup hint, printed to stderr, exit code 1.
- Azure auth failure → caught at invocation, printed as human-readable message, exit code 1.
- LLM API error → caught, message printed, exit code 1. Session entry is NOT written on error.
- Unknown `/command` → print "Unknown command. Run :AI /help for available commands.", exit code 1.

## Testing Strategy

- Unit tests: mock `AzureChatOpenAI` and `DefaultAzureCredential` with `pytest-mock`. No network calls.
- Integration tests: run `python main.py` as subprocess, assert stdout. Still mocked credentials.
- E2E tests: call real Azure OpenAI. Marked `@pytest.mark.e2e`, skipped unless `RUN_E2E=1` env var is set.

## Observability

- Use OpenTelemetry for logs, metrics, and traces

## Security

> TBD - fill in before implementing
