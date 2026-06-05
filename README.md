# vimai

A Vim plugin that lets you query an LLM inline, directly from inside Vim.

---

## For Users

### Prerequisites

- Vim (any recent version)
- Python 3.13 or later — verify with `python --version`
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — Python package manager
- An Azure OpenAI resource with a deployed model
- Azure CLI for authentication — install from [aka.ms/installazurecli](https://aka.ms/installazurecli)

### Step 1 — Install the plugin

vimai can be installed by cloning the repository yourself or by using a standard
Vim plugin manager.

#### Option A: manual clone

```sh
git clone https://github.com/liupeirong/vimai.git ~/vimai
cd ~/vimai
```

On Windows, clone to a path without spaces, for example `C:\tools\vimai`.

#### Option B: vim-plug

```vim
Plug 'liupeirong/vimai', { 'do': 'uv sync' }
```

Then run `:PlugInstall`.

#### Option C: Vundle

```vim
Plugin 'liupeirong/vimai'
```

Then run `:PluginInstall`, `cd` into the installed plugin checkout, and run
`uv sync`.

#### Option D: lazy.nvim

```lua
{
  "liupeirong/vimai",
  build = "uv sync",
}
```

#### Option E: release archive

Download a release archive from GitHub, extract it to a path without spaces, then
run `uv sync` in the extracted directory.

### Step 2 — Install Python dependencies

```sh
uv sync
```

This creates a `.venv` folder inside the repo with all required packages.

### Step 3 — Register the plugin with Vim

If you installed with vim-plug, Vundle, or lazy.nvim, your plugin manager handles
`runtimepath` for you. For a manual clone or release archive, add this line to
your `~/.vimrc`. Use the **exact absolute path** where you installed vimai:

```vim
" Linux / macOS
set runtimepath+=~/vimai

" Windows — use the real path, not a variable
set runtimepath+=C:/tools/vimai
```

> **Tip:** After editing `.vimrc`, restart Vim completely (don't just `:source ~/.vimrc`).
> Verify the plugin loaded by running `:command AI` — you should see the `AI` command listed.
> If it shows `Not an editor command: AI`, the path in `runtimepath` is wrong or the file doesn't
> exist at that path. Check with `:echo globpath(&rtp, 'plugin/vimai.vim')` — it should print
> a non-empty path.

### Step 4 — Set environment variables

vimai needs to know which Azure AI Foundry endpoint and deployment to call.
Set these in your shell **before** launching Vim:

```sh
# Linux / macOS
export AZURE_OPENAI_ENDPOINT="https://<your-resource>.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT="<your-deployment-name>"

# Windows (cmd)
set AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
set AZURE_OPENAI_DEPLOYMENT=<your-deployment-name>

# Windows (PowerShell)
$env:AZURE_OPENAI_ENDPOINT = "https://<your-resource>.openai.azure.com/"
$env:AZURE_OPENAI_DEPLOYMENT = "<your-deployment-name>"
```

vimai automatically appends `/openai/v1/` to the endpoint to use the
[Azure AI Foundry unified inference API](https://learn.microsoft.com/en-us/azure/ai-foundry/),
which supports OpenAI, Llama, DeepSeek, Mistral, and Phi deployments
through a single interface.

You can store these in a `.env` file. vimai automatically reads `.env` from the
current working directory or from the plugin checkout root:

```dotenv
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=<your-deployment-name>
```

LangSmith tracing is optional. If you have a LangSmith subscription, add
`LANGSMITH_API_KEY` to your environment or `.env`; vimai enables tracing
automatically when the key is present. If `LANGSMITH_PROJECT` is not set,
traces are recorded under the `vimai` project.

### Step 5 — Confirm Python resolution

The plugin calls `main.py` under the hood. After `uv sync`, vimai automatically
uses the Python executable from the plugin checkout's `.venv`:

| Environment | Auto-detected Python |
| --- | --- |
| Windows | `<vimai>\.venv\Scripts\python.exe` |
| Linux / macOS | `<vimai>/.venv/bin/python` |

If you need to use a different Python, set one of these before the plugin loads:

```vim
" In vimrc
let g:vimai_python = '/absolute/path/to/python'
```

```sh
# Or in the shell before launching Vim
export VIMAI_PYTHON=/absolute/path/to/python
```

You can still activate `.venv` manually if you prefer, but it is no longer
required when the checkout-local `.venv` exists.

To override the Python entry script location, set `VIMAI_SCRIPT` to the absolute
path of `main.py`.

```sh
export VIMAI_SCRIPT=/absolute/path/to/vimai/main.py
```

### Step 6 — Authenticate with Azure

```sh
az login
```

No API key is needed. vimai uses [DefaultAzureCredential](https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview) (Entra ID / Azure CLI login).

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
from the plugin checkout root. If you prefer to load it manually before
activating the venv and opening Vim, use:

```sh
# Linux / macOS (bash/zsh)
set -a && source .env && set +a

# Windows (cmd)
for /f "usebackq tokens=1,* delims==" %i in (.env) do set %i=%j

# Windows (PowerShell)
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim())
    }
}
```

> ⚠️ Add `.env` to `.gitignore` to avoid committing secrets.

### Troubleshooting

| Symptom | Likely cause | Fix |
| ------- | ------------ | --- |
| `Not an editor command: AI` | Plugin not loaded | Check `runtimepath` path is correct; restart Vim |
| `Not an editor command: AI` | `.vimrc` change not applied | Restart Vim — don't just `:source .vimrc` |
| `python: command not found` | No checkout `.venv` and no Python on `PATH` | Run `uv sync` in the plugin checkout or set `g:vimai_python` / `VIMAI_PYTHON` |
| `ModuleNotFoundError: langchain_openai` | Dependencies missing from selected Python | Run `uv sync` in the plugin checkout or point `g:vimai_python` / `VIMAI_PYTHON` at the right environment |
| `vimai config error: Missing required environment variable(s)` | Env vars not set | Set `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_DEPLOYMENT` before launching Vim |
| `DefaultAzureCredential: no credentials` | Not logged in | Run `az login` |
| Can't find session file | Unsure of exact path | Run `:AISession` in Vim; file is in `%TEMP%` on Windows or `/tmp` on Linux/macOS |
| Unicode characters (e.g. `'`) shown as `~@~Y` | Vim version that doesn't support `readfile()` with UTF-8 | Ensure Vim is compiled with `+multi_byte` (`vim --version \| grep multi_byte`); use Vim ≥ 8.0 |

### Configuration reference

| Environment variable        | Required | Default              | Description                          |
| --------------------------- | -------- | -------------------- | ------------------------------------ |
| `AZURE_OPENAI_ENDPOINT`     | Yes      | —                    | Azure AI Foundry resource base URL (e.g. `https://<name>.openai.azure.com/`) |
| `AZURE_OPENAI_DEPLOYMENT`   | Yes      | —                    | Model deployment name                |
| `LANGSMITH_API_KEY`         | No       | —                    | Enables LangSmith tracing when set   |
| `LANGSMITH_PROJECT`         | No       | `vimai`              | LangSmith project that receives traces |
| `VIMAI_EXTERNAL_AGENTS_DIR` | No       | —                    | Parent directory containing external `<name>/run-agent` wrappers |
| `VIMAI_PYTHON`              | No       | checkout `.venv`, then `python` | Python executable used by the Vim plugin |
| `VIMAI_SCRIPT`              | No       | `<vimai>/main.py`    | Override path to the Python entry script |

---

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

Requires `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`, and an active Azure login.
Set `LANGSMITH_API_KEY` to include LangSmith traces during the e2e run.

### Linting

```sh
uv run ruff format .
uv run ruff check .
```
