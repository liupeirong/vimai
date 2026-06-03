# Progress Log

> Append session logs conforming to this TypeScript schema:
interface session_log {
    datetime: string; // session start datetime YYYY-MM-DD HH-mm
    current_feature: string; // which feature is worked on in this session?
    what_was_done: string[]; // what's implemented, tested, bugs fixed etc
    decision: string[]; // what decisions were made, changed
    issues: string[]; // what issues were encountered, what's their status now
    benchmark_results?: Record<string, string>; // performance benchmark numbers if any, ex. {Query_What_is_the_architecture: "~250ms with 2 citations"}
    next_step: string;
}[]

```json
[
  {
    "datetime": "2026-06-03 13:56",
    "current_feature": "F04 (bug fixes)",
    "what_was_done": [
      "Fixed: slash commands (/help, /clear, /purge) were reaching the LLM as normal prompts on Windows Git Bash — MSYS2 converts positional args starting with '/' to Windows file paths before Python sees them",
      "plugin/vimai.vim: detect /word pattern in s:RunAI and pass '--command <name>' (no leading slash) to Python instead of a positional arg",
      "src/vimai/cli.py: added --command argparse flag; reconstructs '/<name>' and dispatches via handle_command(); positional /command path retained for Linux/macOS direct CLI use",
      "tests/test_cli.py: added TestCliCommandFlag (5 tests) for --command routing",
      "Fixed: Unicode characters (e.g. smart quotes U+2019) displayed as '~@~Y' in scratch buffer on Windows",
      "plugin/vimai.vim: replaced system() output capture with tempname()+readfile(); readfile() reads raw bytes bypassing cmd.exe OEM code-page conversion that system() pipe is subject to",
      "plugin/vimai.vim: /clear now calls s:ClearScratchBuffer() to wipe the scratch buffer content and show 'Session cleared.' as visual feedback",
      "tests/vimai.vader: 3 new vader test cases for clear behaviour (content wiped, cursor stays, works without prior buffer)",
      "Updated README.md troubleshooting table with Unicode garbling row",
      "Updated .ai/feature-list.md F04 evidence to reflect all fixes"
    ],
    "decision": [
      "--command flag is the canonical Vim→Python channel for slash commands; positional /cmd kept only for manual CLI use",
      "readfile() is unconditional (not Windows-only) — it is simpler and also more correct on Linux/macOS where a large response could overflow system() buffers"
    ],
    "issues": [],
    "next_step": "Implement next highest-priority not_started feature: F02 (Multi-line prompt via scratch buffer), F07 (Generic agent loader), or F08 (Route to named agent)."
  },
  {
    "datetime": "2026-06-03 13:05",
    "current_feature": "F04",
    "what_was_done": [
      "Created src/vimai/commands.py: handle_command(), cmd_clear(), cmd_purge(), cmd_help(), HELP_TEXT",
      "handle_command() returns None for non-slash prompts, dispatches /clear /purge /help, returns error string for unknown slash commands",
      "cmd_clear(session_path): deletes session file if it exists; returns confirmation or 'No active session' message",
      "cmd_purge(tmpdir?): globs vimai-session-*.tmp in session parent dir (or system tmpdir); deletes all; returns count with singular/plural",
      "cmd_help(): returns HELP_TEXT listing all three commands plus prompt usage",
      "Updated src/vimai/cli.py: call handle_command() before load_config()/invoke_chain(); slash commands exit 0 without touching LLM or Azure",
      "Created tests/test_commands.py: 17 unit tests covering all handlers and edge cases",
      "Updated tests/test_cli.py: added TestCliSlashCommands (5 tests) for CLI-level routing",
      "pytest: 73/73 passed; ruff format + check: clean"
    ],
    "decision": [
      "Slash commands implemented in Python (not Vim script) — keeps logic testable and platform-consistent",
      "handle_command() placed in cli.py dispatch flow before config load — avoids requiring Azure env vars for /help or /clear",
      "cmd_purge searches session file's parent directory (not getcwd) so it targets the same tmpdir the session was created in",
      "Unknown /commands return a user-facing message (exit 0) rather than exit 1 — consistent with /help UX; not an error"
    ],
    "issues": [],
    "next_step": "Implement next highest-priority not_started feature: F02 (Multi-line prompt via scratch buffer), F07 (Generic agent loader), or F08 (Route to named agent)."
  },
  {
    "datetime": "2026-06-02 14:09",
    "current_feature": "F01 (display UX improvements)",
    "what_was_done": [
      "Updated feature-list.md: F01 user_visible_behavior updated to describe vertical split; F01 notes cleaned up with alternatives discussed; F01 verification/evidence updated to reflect new implementation; added F10 (packaging, priority 3, not_started)",
      "plugin/vimai.vim: replaced execute '!' with system() + vnew vertical split scratch buffer (buftype=nofile, bufhidden=hide, nobuflisted, noswapfile)",
      "plugin/vimai.vim: fixed Windows ^M (\\r) artifacts with substitute(l:response, '\\r', '', 'g')",
      "plugin/vimai.vim: fixed multi-turn appending — introduced s:ai_bufnum script variable; was using bufnr('[AI Response]') which misinterprets brackets as regex character class and always returns -1",
      "plugin/vimai.vim: fixed cursor returning to wrong window — replaced winnr()/wincmd with win_getid()/win_gotoid() for stable window identity across splits",
      "plugin/vimai.vim: set splitright before vnew (restored after) so scratch buffer always opens on the right",
      "plugin/vimai.vim: refactored into s:ShowInScratchBuffer(prompt, lines) + three public test helpers (VimaiTestShow, VimaiTestReset, VimaiTestBufnum)",
      "src/vimai/cli.py: added sys.stdout.reconfigure(encoding='utf-8') and sys.stderr.reconfigure(encoding='utf-8') to fix Unicode encode errors on Windows (e.g. → U+2192)",
      "tests/test_cli.py: added test_prints_unicode_response_to_stdout",
      "tests/vimai.vader: 12 vader test cases covering first-open, cursor stability, buffer reuse, append, separator, read-only, reopen after close",
      "README.md: updated Using vimai section to describe vertical split UX; added Vim plugin tests section under For Developers",
      "CLAUDE.md: added README.md update step to Before You Stop checklist"
    ],
    "decision": [
      "bufhidden=hide (not wipe) so buffer survives window close and can be reopened with vertical sbuffer",
      "s:ai_bufnum stored as script variable — bufnr() with bracketed name is unreliable due to regex interpretation",
      "win_getid()/win_gotoid() used instead of winnr()/wincmd — window numbers shift when splits open",
      "set splitright saved/restored around vnew to avoid permanently changing user's Vim settings",
      "Display logic extracted to s:ShowInScratchBuffer so it can be tested without Python/Azure",
      "Test helpers (VimaiTestShow etc.) are public (no s: prefix) intentionally for vader access"
    ],
    "issues": [
      "vader.vim tests cannot be run in CI without a headless Vim setup — documented in README, left for developer to run manually"
    ],
    "next_step": "Implement next highest-priority not_started feature: F02 (Multi-line prompt via scratch buffer) or F04 (Session control: /clear, /purge, /help)."
  },
  {
    "datetime": "2026-06-02 11:42",
    "current_feature": "F03",
    "what_was_done": [
      "Created src/vimai/session.py: SessionEntry dataclass (role, content, timestamp), new_session_path(tmpdir?), load_session(path), save_session(path, entries)",
      "Updated src/vimai/chain.py: added invoke_chain_with_history(config, session_path, prompt) — loads history, builds [HumanMessage|AIMessage]* + new HumanMessage, calls LLM, saves both turns back",
      "Updated src/vimai/cli.py: switched to argparse, added --session flag; routes to invoke_chain_with_history when present, invoke_chain when absent (backward-compat with F01)",
      "Updated plugin/vimai.vim: generates s:session_file = vimai-session-YYYY-MM-DD-HH-MM-<pid>.tmp at plugin load using strftime+getpid(); passes --session <path> to every :AI call",
      "Created tests/test_session.py: 13 unit tests (path format, tmpdir default, file not created, load missing=[], save/load roundtrip, str path accept, overwrite, to_dict/from_dict)",
      "Added 6 new tests to tests/test_chain.py for invoke_chain_with_history",
      "Added 3 new tests to tests/test_cli.py for --session flag",
      "pytest: 50/50 passed; ruff format + check: clean"
    ],
    "decision": [
      "Session written after every turn (not on Vim exit) — file is already on disk if Vim exits unexpectedly",
      "argparse replaces manual sys.argv slicing in cli.py; existing tests unaffected because argparse reads sys.argv the same way",
      "invoke_chain_with_history imported alongside invoke_chain — both exported from chain.py, no new module needed",
      "Vim plugin uses strftime('%Y-%m-%d-%H-%M') + getpid() to produce structured session filename; Python new_session_path() uses same pattern for symmetry"
    ],
    "issues": [],
    "next_step": "Implement next highest-priority not_started feature: F02 (Multi-line prompt via scratch buffer, priority 2) or F07 (Generic agent loader, priority 2)."
  },
  {
    "datetime": "2026-06-01 15:10",
    "current_feature": "F01",
    "what_was_done": [
      "Created src/vimai/chain.py: invoke_chain(config, prompt) -> str; builds LLM via build_llm(), sends HumanMessage, returns response.content as str",
      "Created src/vimai/cli.py: main() parses sys.argv[1] as prompt, loads config, calls invoke_chain, prints to stdout; exits 0 success / 1 on ConfigError or any exception",
      "Updated main.py: now delegates entirely to vimai.cli.main() — removed placeholder add_numbers usage",
      "Created plugin/vimai.vim: :AI <prompt> command + cabbrev ai AI; resolves main.py path relative to plugin file using <sfile>",
      "Created tests/test_chain.py: 5 unit tests (returns str, sends HumanMessage with prompt text, uses config to build llm, propagates exception, coerces content to str)",
      "Created tests/test_cli.py: 6 unit tests (exits 0 + stdout on success, prints response, exits 1 on ConfigError, exits 1 on LLM error, exits 1 no args, exits 1 blank prompt)",
      "Updated test_main.py: replaced add_numbers smoke test with @pytest.mark.e2e subprocess integration test",
      "Registered pytest.mark.e2e in pyproject.toml [tool.pytest.ini_options]",
      "All 28 pytest tests pass; ruff format + check clean"
    ],
    "decision": [
      "Session history deferred to F03; F01 chain is intentionally single-turn for now",
      "cli.py catches all exceptions with broad except (BLE001 suppressed) to ensure exit code 1 on any error",
      "plugin/vimai.vim uses expand('<sfile>:p:h:h') to resolve the repo root regardless of Vim cwd",
      "test_main.py e2e test is tolerant: passes if vimai appears in stderr OR returncode == 0, so it works without real Azure credentials"
    ],
    "issues": [],
    "next_step": "Implement F03 (Session management) — adds per-session JSON history fed into the chain on subsequent turns."
  },
  {
    "datetime": "2026-06-01 14:42",
    "current_feature": "F05",
    "what_was_done": [
      "Created src/vimai/config.py: Config dataclass (endpoint, deployment, api_version), ConfigError exception, load_config() reading AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_DEPLOYMENT (required) and AZURE_OPENAI_API_VERSION (optional, defaults to 2024-05-01-preview)",
      "Created src/vimai/llm.py: build_llm(config) creates AzureChatOpenAI authenticated via DefaultAzureCredential + get_bearer_token_provider for scope https://cognitiveservices.azure.com/.default — no API key",
      "Created tests/test_config.py: 11 unit tests (all var combinations, whitespace stripping, error message content, default api_version)",
      "Created tests/test_llm.py: 5 unit tests with mocked DefaultAzureCredential and get_bearer_token_provider",
      "All 17 pytest tests pass; ruff format + check clean"
    ],
    "decision": [
      "api_version defaults to 2024-05-01-preview when env var is absent or whitespace-only",
      "Whitespace stripped from all env var values before validation to catch accidental padding",
      "llm.py isolates credential construction; tests patch at module level for clean mocking",
      "azure_deployment is stored as deployment_name on AzureChatOpenAI instance (langchain-openai internals)"
    ],
    "issues": [],
    "next_step": "Implement F01 (Inline LLM query via :AI command) — depends on F05 config + llm modules now in place."
  },
  {
    "datetime": "2026-06-01 13:45",
    "current_feature": "spec",
    "what_was_done": [
      "Defined 9 features (F01-F09) collaboratively with user and recorded in .ai/feature-list.md",
      "Filled in ARCHITECTURE.md: module layout, key abstractions, data flow, error handling, testing strategy",
      "Added langchain-openai, langgraph, langsmith, pytest-mock to pyproject.toml and ran uv sync",
      "Removed stray feature-list.json from repo root",
      "Revised F07/F08: replaced hardcoded Vi agent with generic file-based agent loader (~/.vimai/agents/<name>.md)",
      "Built-in vi.md ships with plugin; users can override or add agents by dropping Markdown files"
    ],
    "decision": [
      "User-defined Vim commands must start uppercase: canonical command is :AI, with cabbrev ai AI",
      "Multi-line prompts use a dedicated scratch buffer submitted with <leader>s (buffer-local mapping)",
      "Subcommands scoped under :AI using slash prefix: /clear, /purge, /help — keeps Vim command namespace clean",
      "Output always in :!-style command window, no split (responses expected to be short)",
      "Session files are JSON, named vimai-session-yyyy-mm-dd-hh-mm-<pid>.tmp in Vim tmpdir",
      ":AI @<name> is stateless single-turn and does not modify the active session",
      "Agent definitions are plain Markdown system prompt files, not Python classes — enables reuse from Claude/Copilot/Codex",
      "Configuration via environment variables only (no vim vars, no secrets in code)",
      "E2E tests gated behind RUN_E2E=1 env var"
    ],
    "issues": [],
    "next_step": "Start new session. Implement F05 (Azure OpenAI + Entra ID config) first as it is a dependency of all other features, then F01 (inline :AI query)."
  },
    "current_feature": "infra-001",
    "what_was_done": [
      "Reviewed all harness files (CLAUDE.md, feature-list.md, clean-state-checklist.md, claude-progress.md, docs/ARCHITECTURE.md)",
      "Identified and fixed filename mismatch (feature-list.json → feature-list.md in CLAUDE.md)",
      "Fixed typo: ruff checking → ruff check",
      "Clarified feature selection rule to 'highest priority'",
      "Added current_feature anchor to progress log schema",
      "Added Completion Gate evidence field reference in CLAUDE.md",
      "Improved checklist item #3 to be actionable",
      "Added ARCHITECTURE.md placeholder section headings",
      "Recorded infra-001 as passing in feature-list.md"
    ],
    "decision": [
      "ARCHITECTURE.md section headings left as placeholders intentionally; will be filled collaboratively in a follow-up session before feature implementation",
      "feature-list.md uses JSON embedded in Markdown (not a separate .json file) for human readability",
      "AI guard for empty feature list deferred — feature-list.md now has 'Work with the user' instruction as sufficient guard"
    ],
    "issues": [
      "ARCHITECTURE.md is still mostly empty — acceptable for now, must be filled before any implementation feature is started"
    ],
    "next_step": "Collaborate with user to fill docs/ARCHITECTURE.md and add first real implementation feature to feature-list.md"
  }
]
```
