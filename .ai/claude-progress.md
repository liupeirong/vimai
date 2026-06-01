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
