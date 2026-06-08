# vimai

A vi plugin that lets you query an LLM inline, directly from inside vi.

---

## For Users

### Prerequisites

- Python 3.13 or later
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- An OpenAI compatible endpoint

### Step 1 — Install the plugin

```sh
git clone https://github.com/liupeirong/vimai.git /path/to/vimai
cd /path/to/vimai
```

### Step 2 — Install Python dependencies

```sh
uv sync
```

### Step 3 — Register the plugin with Vim

Add this line to your `~/.vimrc`. Use the **exact absolute path** where you installed vimai:

```vim
set runtimepath+=/path/to/vimai
```

### Step 4 — Set environment variables

vimai needs to know which OpenAI compatible endpoint to call.
Set these in your shell **before** launching Vim:

```sh
export OPENAI_BASE_URL="https://<your-resource>.openai.azure.com/openai/v1"
export OPENAI_MODEL="<your-deployment-name>"
export OPENAI_API_KEY="" # optional; omit for Entra ID Auth
export LANGSMITH_API_KEY="" # optional; set if you want to enable tracing
export LANGSMITH_PROJECT="" # optional; default = "vimai"
```

### Step 5 — Confirm Python resolution

The plugin calls `main.py` under the hood. After `uv sync`, vimai automatically
uses the Python executable from the plugin checkout's `.venv`.

If you need to use a different Python, set one of these before the plugin loads:

```vim
" In vimrc
let g:vimai_python = '/absolute/path/to/python'
```

### Step 6 — Optional; Authenticate if you use Entra ID to access the LLM

```sh
az login
```

### Using vimai

Once Vim is open, run:

```vim
:AI What does the % register hold in Vim?
```

The response opens in a **vertical split** on the right side of your screen as a read-only buffer.
Your cursor returns to your original window automatically. Close the response pane with `:q` when done.

You can also type `:ai` in lowercase — it is aliased to `:AI`:

```vim
:ai Explain the difference between :s and :S in a substitution command
```

For longer prompts, press `<leader>ai` to open a scratch prompt buffer, type as many
lines as you need, leave Insert mode with `Esc`, then press `<leader>s` from that buffer
to submit. The prompt buffer is wiped after submission, and the response appears in the
same read-only response split.

### Agent prompt files

Agent definitions are plain Markdown system prompts. vimai looks for user-defined
agents in `~/.vimai/agents/<name>.md`; a user file overrides a bundled agent with
the same name. The plugin includes a built-in `vi.md` Vim expert prompt.

```sh
mkdir -p ~/.vimai/agents
cat > ~/.vimai/agents/git.md <<'EOF'
You are a Git expert. Give concise, safe commands and explain risky operations.
EOF
```

Route a prompt to an agent by starting `:AI` with `@<name>`:

```vim
:AI @vi Explain :global with an example
:AI @git How do I undo the last commit but keep the changes?
```

Agent calls are stateless single-turn requests. They use the selected agent's
system prompt and do not read from or write to your current conversation history.

### External agent runners

If no prompt file exists for `@<name>`, vimai can run an external non-interactive
agent wrapper instead. Set `VIMAI_EXTERNAL_AGENTS_DIR` to a directory containing
one subdirectory per external agent:

```dotenv
VIMAI_EXTERNAL_AGENTS_DIR=/path/to/external-agents
```

Each external agent must provide a `run-agent` wrapper. On Windows,
`run-agent.bat` and `run-agent.cmd` are also supported:

```text
/path/to/external-agents/
  git/
    run-agent
    run-agent.bat  # Windows alternative
```

vimai invokes the wrapper as:

```sh
/path/to/external-agents/git/run-agent --prompt-file <tempfile>
```

The prompt is written to a UTF-8 temporary file, so multiline prompts are safe.
The wrapper should write its final answer to stdout; stdout and stderr are shown
in the existing `[AI Response]` scratch buffer. Non-zero exits and wrappers that
run longer than 120 seconds are displayed as clear vimai errors. Prompt-only
agents still take priority, so
`~/.vimai/agents/git.md` or a bundled `git.md` would be used before the external
`git/run-agent` wrapper.

### Conversation history

vimai automatically maintains conversation history for the current Vim session.
Every prompt you send and every response you receive are saved to a temporary JSON file
in your system temp directory:

| Environment | Session file location |
| --- | --- |
| Windows (any shell) | `%TEMP%\vimai-session-YYYY-MM-DD-HH-MM-<pid>.tmp` |
| Linux / macOS | `/tmp/vimai-session-YYYY-MM-DD-HH-MM-<pid>.tmp` |

Run `:AISession` inside Vim to confirm the exact path:

```vim
:AISession
```

History is sent to the LLM on every subsequent turn, so you can ask follow-up questions naturally:

```vim
:AI What is a Vim macro?
:AI How do I record one?
:AI Can I run it 10 times at once?
```

The session file is written after every turn, so your history is preserved even if Vim exits
unexpectedly. A new session file is created each time you open Vim.

### Session commands

Use slash commands to manage your session without making an LLM call:

| Command | What it does |
| --- | --- |
| `:AI /clear` | Close the current session and wipe the scratch buffer; session file is kept on disk |
| `:AI /purge` | Delete **all** `vimai-session-*.tmp` files from your temp directory |
| `:AI /help` | List all available commands |

```vim
:AI /clear
" → Session cleared.

:AI /purge
" → Purged 3 session files.

:AI /help
" → vimai commands:
"     /clear   Close the current session and clear the scratch buffer
"     /purge   Delete all vimai session files from the system temp directory
"     /help    Show this help message
"     <prompt> Send a prompt to the LLM
```

### Loading a .env file

vimai automatically loads a `.env` file from your current working directory or
from the plugin checkout root.

## For Developers

### Tech stack

- Python 3.13, [uv](https://docs.astral.sh/uv/), [LangChain](https://python.langchain.com/), Azure OpenAI
- Tests: `pytest` + `pytest-mock` (no real Azure calls needed for unit tests)
- Linting: `ruff`

### Setup

```sh
git clone https://github.com/liupeirong/vimai.git
cd vimai
uv sync
```

### Running tests

```sh
uv run pytest
```

No Azure credentials are needed — all Azure and LangChain calls are mocked.

### Vim plugin tests

The VimScript buffer/window management is tested with [vader.vim](https://github.com/junegunn/vader.vim).

Install vader.vim (once):

```sh
git clone https://github.com/junegunn/vader.vim ~/.vim/pack/plugins/start/vader.vim
```

Run the tests (replace `~/vimai` with your clone path):

```sh
vim -u NONE -N \
  +"set runtimepath+=~/.vim/pack/plugins/start/vader.vim,~/vimai" \
  +"runtime plugin/vader.vim" \
  +"runtime plugin/vimai.vim" \
  +"Vader tests/vimai.vader"
```

Or from inside Vim with vader.vim installed:

```vim
:Vader tests/vimai.vader
```

### End-to-end tests

```sh
RUN_E2E=1 uv run pytest -m e2e
```

### Linting

```sh
uv run ruff format .
uv run ruff check .
```
