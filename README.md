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

### Step 1 — Get the code

```sh
git clone https://github.com/liupeirong/vimai.git ~/vimai
cd ~/vimai
```

On Windows, clone to a path without spaces, for example `C:\tools\vimai`.

### Step 2 — Install Python dependencies

```sh
uv sync
```

This creates a `.venv` folder inside the repo with all required packages.

### Step 3 — Register the plugin with Vim

Add this line to your `~/.vimrc`. Use the **exact absolute path** where you cloned the repo:

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

You can store these in a `.env` file and load them each session (see [Loading a .env file](#loading-a-env-file)).

### Step 5 — Activate the Python virtual environment

The plugin calls `python main.py` under the hood.
That `python` must be the one with vimai's packages installed — i.e., the `.venv` created in Step 2.

**Activate the venv in the same terminal before you launch Vim:**

```sh
# Linux / macOS
source ~/vimai/.venv/bin/activate

# Windows (cmd)
C:\tools\vimai\.venv\Scripts\activate.bat

# Windows (PowerShell)
C:\tools\vimai\.venv\Scripts\Activate.ps1

# Windows (Git Bash)
source C:/tools/vimai/.venv/Scripts/activate
```

Then launch Vim from that same terminal. You should see `(.venv)` in your prompt.

> **Windows note:** If you launch Vim from Git Bash, make sure to activate the venv in Git Bash
> (not cmd or PowerShell) before running `vim`, so the activated `python` is the one the plugin
> will call.

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
lines as you need, then press `<leader>s` from that buffer to submit. The prompt buffer
is wiped after submission, and the response appears in the same read-only response split.

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

If you store your environment variables in a `.env` file, load them before activating the venv
and opening Vim:

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
| `python: command not found` | Venv not activated | Activate `.venv` before launching Vim (Step 5) |
| `ModuleNotFoundError: langchain_openai` | Wrong Python in use | Activate `.venv` before launching Vim (Step 5) |
| `vimai config error: Missing required environment variable(s)` | Env vars not set | Set `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_DEPLOYMENT` before launching Vim |
| `DefaultAzureCredential: no credentials` | Not logged in | Run `az login` |
| Can't find session file | Unsure of exact path | Run `:AISession` in Vim; file is in `%TEMP%` on Windows or `/tmp` on Linux/macOS |
| Unicode characters (e.g. `'`) shown as `~@~Y` | Vim version that doesn't support `readfile()` with UTF-8 | Ensure Vim is compiled with `+multi_byte` (`vim --version \| grep multi_byte`); use Vim ≥ 8.0 |

### Configuration reference

| Environment variable        | Required | Default              | Description                          |
| --------------------------- | -------- | -------------------- | ------------------------------------ |
| `AZURE_OPENAI_ENDPOINT`     | Yes      | —                    | Azure AI Foundry resource base URL (e.g. `https://<name>.openai.azure.com/`) |
| `AZURE_OPENAI_DEPLOYMENT`   | Yes      | —                    | Model deployment name                |

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

### Linting

```sh
uv run ruff format .
uv run ruff check .
```
