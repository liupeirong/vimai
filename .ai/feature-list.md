# VIM.AI feature list

> Note: Work with the user to record features in the features field of this TypeScript interface:
enum status_legend {
    not_started, // Work has not begun
    in_progress, // The feature is the current active task
    blocked, // Work cannot continue until a documented blocker is resolved
    passing // Required verification has passed and evidence is recorded
},
interface feature_list {
  last_updated: string, // YYYY-MM-DD HH-mm
  feature: {
    id: string; // ex. "vi-plugin-001",
    priority: number; // 1, 2, 3 - from high to low
    area: string; // ex. "vim plugin", "llm integration", "memory management"
    title: string;
    user_visible_behavior: string; // what can the user do?
    status: status_legend;
    verification: string[]; // what needs to be true to call the feature complete
    evidence: string[]; // what's validated
    notes: string; // anything to note about this feature
  }[]
}

```json
{
  "last_updated": "2026-06-04 06:26",
  "feature": [
    {
      "id": "infra-001",
      "priority": 1,
      "area": "engineering harness",
      "title": "AI autonomous work harness",
      "user_visible_behavior": "An AI agent can pick up the repo cold, understand what to build next, implement one feature at a time, verify it, and leave the repo in a clean resumable state without human intervention between sessions.",
      "status": "passing",
      "verification": [
        "CLAUDE.md exists with startup checklist, rules, completion gate, and shutdown procedure",
        "feature-list.md exists with schema and at least one recorded feature",
        "claude-progress.md exists with session log schema including current_feature anchor",
        "clean-state-checklist.md exists covering build, runtime, and repository hygiene",
        "docs/ARCHITECTURE.md exists with section headings as placeholders",
        "All filenames referenced in CLAUDE.md resolve to actual files",
        "Commit format instruction references a real file (.github/instructions/general-review.instructions.md)"
      ],
      "evidence": [
        "Human+AI review on 2026-06-01: all cross-references verified correct",
        "Typo in ruff check command fixed, filename mismatch fixed, feature selection rule clarified",
        "current_feature anchor added to progress log schema",
        "Completion gate explicitly references evidence field in feature-list.md"
      ],
      "notes": "ARCHITECTURE.md section headings are intentional placeholders; content will be filled collaboratively before feature implementation begins."
    },
    {
      "id": "F01",
      "priority": 1,
      "area": "vim plugin",
      "title": "Inline LLM query via :AI command",
      "user_visible_behavior": "User runs ':AI <prompt>' in Vim. Response appears in a vertical split scratch buffer; cursor returns to the original window. Close with :q.",
      "status": "passing",
      "verification": [
        "':AI hello' opens a vertical split showing the LLM response",
        "Split buffer is read-only, unlisted, wiped on close",
        "Cursor returns to the original window after split opens",
        "cabbrev maps ':ai' to ':AI'",
        "main.py exits 0 on success, 1 on error"
      ],
      "evidence": [
        "src/vimai/chain.py: invoke_chain(config, prompt) -> str using AzureChatOpenAI + HumanMessage",
        "src/vimai/cli.py: main() parses argv[1], calls load_config()+invoke_chain(), prints response, exits 0/1",
        "main.py: updated to delegate to cli.main()",
        "plugin/vimai.vim: s:RunAI uses system() to capture output; opens vnew scratch buffer with setline(); setlocal nomodifiable; wincmd p returns focus",
        "tests/test_chain.py: 5 unit tests with mocked build_llm (returns str, sends HumanMessage, propagates exceptions, coerces content)",
        "tests/test_cli.py: 6 unit tests covering exit codes, stdout output, config errors, LLM errors, no-args, blank prompt",
        "pytest: 28/28 passed; ruff format + check: clean"
      ],
      "notes": "Response displayed in vertical split scratch buffer (buftype=nofile, bufhidden=hide). User closes with :q. Session history in F03. No Python changes required for this display update."
    },
    {
      "id": "F02",
      "priority": 2,
      "area": "vim plugin",
      "title": "Multi-line prompt via scratch buffer",
      "user_visible_behavior": "User opens a scratch buffer, types multi-line prompt, presses <leader>s to submit.",
      "status": "passing",
      "verification": [
        "Scratch buffer opens via a keymap",
        "<leader>s in scratch buffer submits content and displays response",
        "Buffer is wiped after submission"
      ],
      "evidence": [
        "plugin/vimai.vim: <leader>ai opens [AI Prompt] scratch buffer via :AIPrompt / <Plug>(vimai-prompt)",
        "plugin/vimai.vim: prompt buffer has buffer-local normal/insert <leader>s mapping to submit multiline content",
        "plugin/vimai.vim: prompt buffer is closed and wiped after submission; response is shown in [AI Response]",
        "src/vimai/cli.py: --prompt-file reads UTF-8 multiline prompts so Vim does not pass embedded newlines through shell arguments",
        "tests/test_cli.py: 2 prompt-file unit tests",
        "tests/vimai.vader: 3 F02 tests for prompt buffer open, submit, wipe, newline preservation, response display, and cursor return",
        "uv run ruff format . && uv run ruff check . && uv run pytest: 81/81 passed",
        "Direct Vim smoke test via sourced plugin and stdin-driven ex commands wrote 'ok': prompt buffer opens, buffer-local <leader>s exists, multiline content is preserved, prompt buffer is wiped, response buffer displays prompt/response, and cursor returns"
      ],
      "notes": "Buffer-local <leader>s mapping does not leak to other buffers. <leader>ai is installed only when no existing mapping targets <Plug>(vimai-prompt). Full Vader suite still requires vader.vim installation."
    },
    {
      "id": "F03",
      "priority": 1,
      "area": "memory management",
      "title": "Session management",
      "user_visible_behavior": "Conversation history is persisted per session in a JSON tmp file. History is sent to LLM on each turn.",
      "status": "passing",
      "verification": [
        "Session file created on first prompt: vimai-session-yyyy-mm-dd-hh-mm-<pid>.tmp in Vim tmpdir",
        "Each entry: {role, content, timestamp}",
        "History passed to LLM on subsequent prompts in same session",
        "Session file saved on Vim exit if non-empty"
      ],
      "evidence": [
        "src/vimai/session.py: SessionEntry dataclass, new_session_path(), load_session(), save_session()",
        "src/vimai/chain.py: invoke_chain_with_history() builds messages from history, persists both turns after LLM call",
        "src/vimai/cli.py: --session flag routes to invoke_chain_with_history; no-session path unchanged (F01 backward-compat)",
        "plugin/vimai.vim: generates vimai-session-YYYY-MM-DD-HH-MM-<pid>.tmp at startup via strftime+getpid(), passes --session to python on every :AI call",
        "tests/test_session.py: 13 unit tests covering path format, load/save roundtrip, missing file, str/Path acceptance",
        "tests/test_chain.py: 6 new tests for invoke_chain_with_history (empty session, history prepended, accumulation, save, propagate exception)",
        "tests/test_cli.py: 3 new tests for --session flag routing and Path coercion",
        "pytest: 50/50 passed; ruff format + check: clean"
      ],
      "notes": "File stored in $TMPDIR or system tmp. PID in name avoids multi-instance collisions. Written after every turn so session survives Vim exit without a separate flush."
    },
    {
      "id": "F04",
      "priority": 2,
      "area": "vim plugin",
      "title": "Session control: /clear, /purge, /help",
      "user_visible_behavior": "':AI /clear' ends session. ':AI /purge' deletes all session files. ':AI /help' lists commands.",
      "status": "passing",
      "verification": [
        "':AI /clear' closes active session and prints confirmation",
        "':AI /purge' deletes all vimai-session-*.tmp files and prints count",
        "':AI /help' prints all commands with descriptions",
        "Unknown /command prints error referencing /help"
      ],
      "evidence": [
        "src/vimai/commands.py: handle_command(), cmd_clear() (no file deletion), cmd_purge(), cmd_help() + HELP_TEXT",
        "src/vimai/cli.py: handle_command() dispatched before LLM call; --command flag avoids MSYS2/Git Bash positional-arg path conversion",
        "plugin/vimai.vim: s:RunAI uses tempname()+readfile() for UTF-8-safe output; s:ClearScratchBuffer() wipes scratch buffer on /clear; s:session_file reset to new path after /clear",
        "tests/test_commands.py: 15 unit tests covering all handlers and edge cases",
        "tests/test_cli.py: TestCliSlashCommands (5) + TestCliCommandFlag (5) verifying routing, file preservation on /clear, file deletion on /purge",
        "tests/vimai.vader: 3 vader test cases for /clear scratch buffer behaviour",
        "pytest: 77/77 passed; ruff format + check: clean"
      ],
      "notes": "Slash-prefix subcommand pattern keeps :AI as the single Vim command. /clear closes session (resets path, preserves file). /purge deletes files. --command flag used by Vim plugin to avoid MSYS2 path conversion."
    },
    {
      "id": "F05",
      "priority": 1,
      "area": "llm integration",
      "title": "Azure OpenAI + Entra ID authentication",
      "user_visible_behavior": "Plugin connects to Azure OpenAI using Entra ID. No API key required.",
      "status": "passing",
      "verification": [
        "Auth uses DefaultAzureCredential (az login, managed identity, etc.)",
        "Required env vars: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT",
        "Optional: AZURE_OPENAI_API_VERSION",
        "Missing required vars produce a clear error message",
        "No secrets in source code"
      ],
      "evidence": [
        "src/vimai/config.py: Config dataclass + ConfigError + load_config() implemented",
        "src/vimai/llm.py: build_llm() uses sync DefaultAzureCredential + get_bearer_token_provider; ChatOpenAI with base_url set to {endpoint}/openai/v1/ for Azure AI Foundry unified inference API",
        "tests/test_config.py: 11 unit tests covering all env var cases, whitespace, defaults",
        "tests/test_llm.py: 7 unit tests with mocked credentials — assert ChatOpenAI type, correct base_url/model, cognitive scope, trailing-slash normalisation",
        "pytest: 79/79 passed; ruff format + check: clean"
      ],
      "notes": "Uses ChatOpenAI (not AzureChatOpenAI) per LangChain recommendation for Azure AI Foundry openai/v1 API. AZURE_OPENAI_API_VERSION is no longer required; endpoint + deployment are the only required vars."
    },
    {
      "id": "F06",
      "priority": 3,
      "area": "observability",
      "title": "LangSmith tracing (optional)",
      "user_visible_behavior": "When LANGCHAIN_TRACING_V2 and LANGSMITH_API_KEY are set, calls are traced in LangSmith.",
      "status": "not_started",
      "verification": [
        "Traces appear in LangSmith when vars are set",
        "Plugin works normally when vars are absent"
      ],
      "evidence": [],
      "notes": "LangSmith tracing is automatic via LangChain when env vars are present."
    },
    {
      "id": "F07",
      "priority": 2,
      "area": "agents",
      "title": "Generic agent loader from system prompt file",
      "user_visible_behavior": "Agents are defined as plain Markdown system prompt files in ~/.vimai/agents/<name>.md. The plugin ships a built-in vi.md. Users can author their own or copy definitions from Claude, Copilot, Codex, etc.",
      "status": "not_started",
      "verification": [
        "Agent loader reads ~/.vimai/agents/<name>.md as system prompt",
        "Built-in vi.md ships with the plugin (Vim expert system prompt)",
        "If ~/.vimai/agents/<name>.md exists it overrides the built-in",
        "Missing agent file produces a clear error: 'No agent found for @<name>. Create ~/.vimai/agents/<name>.md'",
        "Agent loader unit-testable with mocked LLM and temp file fixtures"
      ],
      "evidence": [],
      "notes": "No hardcoded agent logic in Python. The Claude/Copilot/Codex reuse story is: copy their .instructions.md or SKILL.md into ~/.vimai/agents/. Future milestone will formalize that import flow."
    },
    {
      "id": "F08",
      "priority": 2,
      "area": "vim plugin",
      "title": "Route prompt to named agent via :AI @<name>",
      "user_visible_behavior": "':AI @vi <prompt>' loads the vi agent and answers inline. ':AI @git <prompt>' loads a git agent, etc. Stateless single-turn, does not modify the current session.",
      "status": "not_started",
      "verification": [
        "':AI @vi <prompt>' loads vi.md system prompt and returns response",
        "':AI @<name> <prompt>' works for any agent file in ~/.vimai/agents/",
        "Response shown in command window",
        "Active session is not modified",
        "':AI @<name>' with no prompt prints usage hint"
      ],
      "evidence": [],
      "notes": "Single-turn stateless. @<name> pattern is the extension point for future agent ecosystem integration."
    },
    {
      "id": "F09",
      "priority": 1,
      "area": "engineering",
      "title": "Unit and integration test suite",
      "user_visible_behavior": "Developer can run 'pytest' and verify all logic without Azure credentials.",
      "status": "not_started",
      "verification": [
        "Unit tests cover: config validation, session CRUD, /clear /purge /help, @vi routing, error handling",
        "pytest-mock used to mock LangChain and Azure credentials",
        "E2E tests marked @pytest.mark.e2e, skipped unless RUN_E2E=1",
        "'pytest' passes with no credentials"
      ],
      "evidence": [],
      "notes": "Tests written alongside each feature."
    },
    {
      "id": "F10",
      "priority": 3,
      "area": "distribution",
      "title": "Package and distribute the plugin",
      "user_visible_behavior": "Users can install vimai via standard Vim plugin managers (vim-plug, Vundle, lazy.nvim, etc.) or download a release archive.",
      "status": "not_started",
      "verification": [],
      "evidence": [],
      "notes": "Details TBD. Deferred to end of development."
    }
  ]
}
```
