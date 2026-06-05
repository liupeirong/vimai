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
  "last_updated": "2026-06-05 07:03",
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
        "plugin/vimai.vim: prompt buffer has buffer-local normal-mode <leader>s mapping to submit multiline content",
        "plugin/vimai.vim: prompt buffer is closed and wiped after submission; response is shown in [AI Response]",
        "src/vimai/cli.py: --prompt-file reads UTF-8 multiline prompts so Vim does not pass embedded newlines through shell arguments",
        "tests/test_cli.py: 2 prompt-file unit tests",
        "tests/vimai.vader: 3 F02 tests for prompt buffer open, submit, wipe, newline preservation, response display, and cursor return",
        "uv run ruff format . && uv run ruff check . && uv run pytest: 81/81 passed",
        "Direct Vim smoke test via sourced plugin and stdin-driven ex commands wrote 'ok': prompt buffer opens, buffer-local <leader>s exists, multiline content is preserved, prompt buffer is wiped, response buffer displays prompt/response, and cursor returns"
      ],
      "notes": "Buffer-local <leader>s mapping does not leak to other buffers. Submission is normal-mode-only to avoid accidental sends while typing, especially when mapleader is Space. <leader>ai is installed only when no existing mapping targets <Plug>(vimai-prompt). Full Vader suite still requires vader.vim installation."
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
      "priority": 1,
      "area": "observability",
      "title": "LangSmith tracing when configured",
      "user_visible_behavior": "When users provide LANGSMITH_API_KEY directly or in .env, vimai enables LangSmith tracing automatically. Without a key, vimai continues to work normally without tracing.",
      "status": "passing",
      "verification": [
        ".env files are loaded with python-dotenv from the current working directory or plugin checkout root",
        "LANGSMITH_API_KEY is optional; missing values do not block LLM calls",
        "LangSmith tracing flags are enabled automatically before LLM calls when LANGSMITH_API_KEY is set",
        "LANGSMITH_PROJECT defaults to vimai when tracing is enabled and project is absent",
        "No LangSmith API key is stored in source code or the Config dataclass"
      ],
      "evidence": [
        "pyproject.toml and uv.lock: python-dotenv added as a runtime dependency",
        "src/vimai/config.py: load_config() uses python-dotenv to load .env files and enables LANGSMITH_TRACING/LANGCHAIN_TRACING_V2 only when LANGSMITH_API_KEY is present",
        "tests/test_config.py: F06 coverage for .env loading, tracing flag enablement with a key, no tracing when key is absent, and no key persisted on Config",
        "README.md: setup, .env, troubleshooting, config reference, and e2e docs updated to make LangSmith optional but automatic when configured",
        "uv run ruff format . && uv run ruff check . && uv run pytest: 102/102 passed"
      ],
      "notes": "LangSmith support is important observability, but it is subscription-gated. Users without LANGSMITH_API_KEY can still use vimai without traces. The API key belongs in the environment or .env; .env remains ignored by git."
    },
    {
      "id": "F07",
      "priority": 2,
      "area": "agents",
      "title": "Generic agent loader from system prompt file",
      "user_visible_behavior": "Agents are defined as plain Markdown system prompt files in ~/.vimai/agents/<name>.md. The plugin ships a built-in vi.md. Users can author their own or copy definitions from Claude, Copilot, Codex, etc.",
      "status": "passing",
      "verification": [
        "Agent loader reads ~/.vimai/agents/<name>.md as system prompt",
        "Built-in vi.md ships with the plugin (Vim expert system prompt)",
        "If ~/.vimai/agents/<name>.md exists it overrides the built-in",
        "Missing agent file produces a clear error: 'No agent found for @<name>. Create ~/.vimai/agents/<name>.md'",
        "Agent loader unit-testable with mocked LLM and temp file fixtures"
      ],
      "evidence": [
        "src/vimai/agents/loader.py: load_agent() normalizes @name, reads ~/.vimai/agents/<name>.md first, falls back to importlib.resources bundled prompts, and raises AgentNotFoundError with the required creation hint",
        "src/vimai/builtin_agents/vi.md: bundled Vim expert system prompt",
        "pyproject.toml: package-data includes vimai.builtin_agents/*.md so bundled prompt files ship in built wheels",
        "src/vimai/chain.py: invoke_agent() sends SystemMessage(agent.system_prompt) followed by HumanMessage(prompt) for stateless single-turn agent calls",
        "tests/test_agents.py: temp-file fixtures cover user agents, @name normalization, built-in vi fallback, user override, missing-agent error, and invalid names",
        "tests/test_chain.py: mocked LLM coverage for invoke_agent message order, config usage, and loader error propagation",
        "uv run pytest: 94/94 passed",
        "uv build wheel inspection: vimai/builtin_agents/vi.md present"
      ],
      "notes": "No hardcoded agent logic in Python. The Claude/Copilot/Codex reuse story is: copy their .instructions.md or SKILL.md into ~/.vimai/agents/. F08 will expose :AI @<name> routing through Vim/CLI."
    },
    {
      "id": "F08",
      "priority": 2,
      "area": "vim plugin",
      "title": "Route prompt to named agent via :AI @<name>",
      "user_visible_behavior": "':AI @vi <prompt>' loads the vi agent and answers inline. ':AI @git <prompt>' loads a git agent, etc. Stateless single-turn, does not modify the current session.",
      "status": "passing",
      "verification": [
        "':AI @vi <prompt>' loads vi.md system prompt and returns response",
        "':AI @<name> <prompt>' works for any agent file in ~/.vimai/agents/",
        "Response shown in command window",
        "Active session is not modified",
        "':AI @<name>' with no prompt prints usage hint"
      ],
      "evidence": [
        "src/vimai/cli.py: leading @<name> prompts route to invoke_agent(config, name, prompt) instead of invoke_chain()/invoke_chain_with_history()",
        "src/vimai/cli.py: @<name> without a body exits with usage hint: Usage: vimai '@<agent> <prompt>'",
        "plugin/vimai.vim: :AI @<name> prompts and multiline @<name> prompt-file submissions omit --session, so agent calls are stateless from Vim",
        "tests/test_cli.py: 4 F08 unit tests cover @vi routing, arbitrary @git routing with --session skipping history, prompt-file routing, and missing-body usage",
        "tests/vimai.vader: agent prompt detection coverage added for VimScript routing helper",
        "uv run ruff format . && uv run ruff check . && uv run pytest: 98/98 passed"
      ],
      "notes": "Single-turn stateless. @<name> pattern is the extension point for future agent ecosystem integration. Agent responses reuse the existing [AI Response] split display."
    },
    {
      "id": "F09",
      "priority": 2,
      "area": "agents",
      "title": "External agent command runner",
      "user_visible_behavior": "Users continue to run ':AI @<name> <prompt>'. vimai first checks the existing prompt-only agent locations for <name>.md. If no prompt-only agent exists, vimai looks in the external agents directory configured by VIMAI_EXTERNAL_AGENTS_DIR in .env and launches <external-agents-dir>/<name>/run-agent with the prompt passed through a temp prompt file. The external agent's stdout/stderr appears in the existing [AI Response] scratch buffer.",
      "status": "not_started",
      "verification": [
        "':AI @<name> <prompt>' remains the single user-facing syntax for prompt-only and external agents",
        "Existing prompt-only agent resolution has priority: ~/.vimai/agents/<name>.md first, then bundled agents such as vi.md",
        "If no prompt-only agent exists, vimai reads VIMAI_EXTERNAL_AGENTS_DIR from the normal .env/config loading path",
        "External agents are discovered as <VIMAI_EXTERNAL_AGENTS_DIR>/<name>/run-agent wrappers",
        "The run-agent wrapper receives the user prompt via '--prompt-file <tempfile>'",
        "External agent calls pass the prompt via a UTF-8 temp file instead of shell-embedding multiline content",
        "stdout and stderr from the external process are captured and displayed in the [AI Response] scratch buffer",
        "Non-zero external process exits produce a clear user-visible error",
        "External agent calls do not read from or write to vimai session history",
        "Unit tests cover prompt-agent precedence, .env config loading, wrapper discovery, prompt-file handling, output capture, non-zero exits, and stateless routing"
      ],
      "evidence": [],
      "notes": "External agents are non-interactive request/response CLIs for v1. The per-agent run-agent wrapper owns venv activation or direct venv Python invocation, so vimai does not guess Python paths, entrypoints, or arguments. Interactive or streaming agents may require Vim jobs/channels later; this feature should first support a simple process contract that writes the final answer to stdout."
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
