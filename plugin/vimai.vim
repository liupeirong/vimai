" vimai.vim - Vim plugin for inline LLM queries (F01, F02, F03, F04, F08)
"
" Usage:
"   :AI <prompt>     Send a prompt to the LLM; response opens in a vertical split
"   :AI @vi <prompt> Send a stateless prompt to a named agent
"   <leader>ai       Open a scratch buffer for a multi-line prompt
"   <leader>s        Submit from the multi-line prompt buffer
"   :ai <prompt>     Alias (cabbrev) for :AI
"
" Requirements:
"   Run `uv sync` in the plugin checkout. vimai uses .venv automatically when
"   present; set g:vimai_python or VIMAI_PYTHON to override the Python path.
"   OPENAI_BASE_URL and OPENAI_MODEL must be set.

if exists('g:loaded_vimai')
  finish
endif
let g:loaded_vimai = 1

" Allow :ai as a command-line abbreviation for :AI so users can type lowercase.
cabbrev ai AI

" Resolve the path to main.py relative to this plugin file so the plugin
" works regardless of the user's working directory.
let s:plugin_dir = expand('<sfile>:p:h:h')

function! s:ResolveMainScript() abort
  if exists('$VIMAI_SCRIPT') && $VIMAI_SCRIPT !=# ''
    return expand($VIMAI_SCRIPT)
  endif
  return s:plugin_dir . '/main.py'
endfunction

function! s:ResolvePythonCommand() abort
  if exists('g:vimai_python') && !empty(g:vimai_python)
    return g:vimai_python
  endif
  if exists('$VIMAI_PYTHON') && $VIMAI_PYTHON !=# ''
    return expand($VIMAI_PYTHON)
  endif

  if has('win32') || has('win64') || has('win32unix')
    let l:venv_python = s:plugin_dir . '/.venv/Scripts/python.exe'
  else
    let l:venv_python = s:plugin_dir . '/.venv/bin/python'
  endif
  if filereadable(l:venv_python)
    return l:venv_python
  endif

  return 'python'
endfunction

let s:main_script = s:ResolveMainScript()
let s:python_cmd = s:ResolvePythonCommand()

" Generate a session file path for this Vim process directly in the system
" temp directory — $TEMP on Windows, $TMPDIR (or /tmp) on Linux/macOS.
" Avoids fnamemodify(tempname()) which adds an unpredictable random subdirectory.
if has('win32') || has('win64') || has('win32unix')
  let s:tmpdir = expand('$TEMP')
else
  let s:tmpdir = len($TMPDIR) > 0 ? expand('$TMPDIR') : '/tmp'
endif
let s:session_file = s:tmpdir .
      \ '/vimai-session-' . strftime('%Y-%m-%d-%H-%M') .
      \ '-' . getpid() . '.tmp'

" :AI <prompt>  – run prompt through vimai and display response inline.
command! -nargs=+ AI call s:RunAI(<q-args>)

" :AIPrompt  – open a scratch buffer for composing a multi-line prompt.
command! AIPrompt call s:OpenPromptBuffer()

" :AISession  – show the session file path for this Vim process (for debugging).
command! AISession echo 'Session file: ' . s:session_file

nnoremap <silent> <Plug>(vimai-prompt) :<C-U>AIPrompt<CR>
if !hasmapto('<Plug>(vimai-prompt)', 'n')
  nmap <leader>ai <Plug>(vimai-prompt)
endif

" Buffer number of the AI response scratch buffer; -1 means not yet created.
let s:ai_bufnum = -1

" Buffer number of the multi-line prompt scratch buffer; -1 means not open.
let s:prompt_bufnum = -1
let s:prompt_return_winid = 0

" Core display logic — separated from system() so it can be driven by tests.
function! s:ShowInScratchBuffer(prompt, lines) abort
  let l:orig_winid = win_getid()
  let l:prompt_lines = split(a:prompt, "\n", 1)
  let l:display_prompt = ['> ' . l:prompt_lines[0]]
  for l:line in l:prompt_lines[1:]
    call add(l:display_prompt, '  ' . l:line)
  endfor
  let l:entry = l:display_prompt + [''] + a:lines

  if s:ai_bufnum != -1 && bufexists(s:ai_bufnum)
    " Buffer exists — bring it into view if its window was closed.
    if bufwinnr(s:ai_bufnum) == -1
      execute 'vertical sbuffer ' . s:ai_bufnum
    else
      execute bufwinnr(s:ai_bufnum) . 'wincmd w'
    endif
    setlocal modifiable
    call append(line('$'), ['', repeat('-', 40), ''] + l:entry)
    setlocal nomodifiable
    normal! G
  else
    " First call this session — open a vertical split scratch buffer on the right.
    let l:save_splitright = &splitright
    set splitright
    vnew
    let &splitright = l:save_splitright
    setlocal buftype=nofile bufhidden=hide nobuflisted noswapfile
    silent file [AI\ Response]
    let s:ai_bufnum = bufnr('%')
    call setline(1, l:entry)
    setlocal nomodifiable
  endif

  " Return to the original editing window using its stable ID.
  call win_gotoid(l:orig_winid)
endfunction

function! s:OpenPromptBuffer() abort
  let s:prompt_return_winid = win_getid()

  if s:prompt_bufnum != -1 && bufexists(s:prompt_bufnum)
    if bufwinnr(s:prompt_bufnum) == -1
      execute 'vertical sbuffer ' . s:prompt_bufnum
    else
      execute bufwinnr(s:prompt_bufnum) . 'wincmd w'
    endif
  else
    let l:save_splitright = &splitright
    set splitright
    vnew
    let &splitright = l:save_splitright
    setlocal buftype=nofile bufhidden=wipe nobuflisted noswapfile
    silent file [AI\ Prompt]
    let s:prompt_bufnum = bufnr('%')
  endif

  setlocal modifiable
  nnoremap <silent> <buffer> <leader>s :<C-U>call <SID>SubmitPromptBuffer()<CR>
  echo 'Type a prompt, leave Insert mode, then press <leader>s to submit.'
endfunction

function! s:SubmitPromptBuffer() abort
  call s:SubmitPromptBufferWithRunner(function('s:RunAI'))
endfunction

function! s:SubmitPromptBufferWithRunner(runner) abort
  let l:prompt = join(getline(1, '$'), "\n")
  if empty(trim(l:prompt))
    echoerr 'vimai prompt is empty'
    return
  endif

  let l:prompt_bufnum = bufnr('%')
  let l:return_winid = s:prompt_return_winid
  close!
  if bufexists(l:prompt_bufnum)
    execute 'bwipeout! ' . l:prompt_bufnum
  endif
  let s:prompt_bufnum = -1

  if l:return_winid != 0
    call win_gotoid(l:return_winid)
  endif
  call a:runner(l:prompt)
endfunction

function! s:RunAI(prompt) abort
  " Slash commands (/clear, /purge, /help) are passed via --command <name>
  " rather than as a positional argument. This avoids MSYS2/Git Bash path
  " conversion, which silently rewrites positional args starting with '/'
  " to Windows file paths, causing them to reach the LLM as normal prompts.
  let l:subcmd = matchstr(a:prompt, '^\s*/\zs\w\+\ze\s*$')
  let l:is_agent_prompt = s:IsAgentPrompt(a:prompt)
  let l:promptfile = ''
  if l:subcmd !=# ''
    let l:cmd = shellescape(s:python_cmd) . ' ' . shellescape(s:main_script) .
          \ ' --command ' . shellescape(l:subcmd) .
          \ ' --session ' . shellescape(s:session_file)
  elseif a:prompt =~# "\n"
    let l:promptfile = tempname()
    call writefile(split(a:prompt, "\n", 1), l:promptfile)
    let l:cmd = shellescape(s:python_cmd) . ' ' . shellescape(s:main_script)
    if !l:is_agent_prompt
      let l:cmd .= ' --session ' . shellescape(s:session_file)
    endif
    let l:cmd .= ' --prompt-file ' . shellescape(l:promptfile)
  else
    let l:cmd = shellescape(s:python_cmd) . ' ' . shellescape(s:main_script)
    if !l:is_agent_prompt
      let l:cmd .= ' --session ' . shellescape(s:session_file)
    endif
    let l:cmd .= ' ' . shellescape(a:prompt)
  endif

  " Write to a temp file and read with readfile() instead of capturing
  " system() output directly. system() passes bytes through the shell's code
  " page on Windows cmd.exe, mangling UTF-8 multi-byte sequences (e.g.
  " U+2019 → '~@~Y'). readfile() reads raw bytes and sidesteps that pipeline.
  let l:tmpfile = tempname()
  call system(l:cmd . ' > ' . shellescape(l:tmpfile) . ' 2>&1')
  let l:lines = readfile(l:tmpfile)
  call delete(l:tmpfile)
  if l:promptfile !=# ''
    call delete(l:promptfile)
  endif

  " Strip carriage returns from Windows line endings.
  call map(l:lines, 'substitute(v:val, "\\r", "", "g")')

  " /clear: wipe scratch buffer for visual feedback and reset s:session_file
  " so the next prompt starts a fresh session. The old session file is kept
  " on disk (/purge is responsible for deletion).
  if l:subcmd ==# 'clear'
    call s:ClearScratchBuffer(l:lines)
    let s:session_file = s:tmpdir .
          \ '/vimai-session-' . strftime('%Y-%m-%d-%H-%M') .
          \ '-' . getpid() . '.tmp'
  else
    call s:ShowInScratchBuffer(a:prompt, l:lines)
  endif
endfunction

function! s:IsAgentPrompt(prompt) abort
  return a:prompt =~# '^\s*@'
endfunction

" Replace the scratch buffer contents with msg_lines and mark it read-only.
" Opens the buffer in a split if it exists but is hidden; creates it otherwise.
function! s:ClearScratchBuffer(msg_lines) abort
  let l:orig_winid = win_getid()

  if s:ai_bufnum != -1 && bufexists(s:ai_bufnum)
    if bufwinnr(s:ai_bufnum) == -1
      execute 'vertical sbuffer ' . s:ai_bufnum
    else
      execute bufwinnr(s:ai_bufnum) . 'wincmd w'
    endif
    setlocal modifiable
    silent %delete _
    call setline(1, a:msg_lines)
    setlocal nomodifiable
    normal! gg
  else
    " No scratch buffer yet — open one to show the confirmation.
    let l:save_splitright = &splitright
    set splitright
    vnew
    let &splitright = l:save_splitright
    setlocal buftype=nofile bufhidden=hide nobuflisted noswapfile
    silent file [AI\ Response]
    let s:ai_bufnum = bufnr('%')
    call setline(1, a:msg_lines)
    setlocal nomodifiable
  endif

  call win_gotoid(l:orig_winid)
endfunction

" ── Test helpers (public) ────────────────────────────────────────────────────
" These are intentionally public so vader tests can drive the display logic
" directly without needing a live Python/Azure connection.

" Drive the scratch buffer with a fixed response — used by vader tests.
function! VimaiTestShow(prompt, response) abort
  call s:ShowInScratchBuffer(a:prompt, split(a:response, "\n"))
endfunction

" Simulate a /clear command — used by vader tests.
function! VimaiTestClear(msg) abort
  call s:ClearScratchBuffer([a:msg])
endfunction

" Wipe the scratch buffer and reset state — call between vader test cases.
function! VimaiTestReset() abort
  if s:ai_bufnum != -1 && bufexists(s:ai_bufnum)
    execute 'bwipeout! ' . s:ai_bufnum
  endif
  let s:ai_bufnum = -1
  if s:prompt_bufnum != -1 && bufexists(s:prompt_bufnum)
    execute 'bwipeout! ' . s:prompt_bufnum
  endif
  let s:prompt_bufnum = -1
  let s:prompt_return_winid = 0
  let s:test_submitted_prompt = ''
endfunction

" Return the current scratch buffer number — used by vader assertions.
function! VimaiTestBufnum() abort
  return s:ai_bufnum
endfunction

function! VimaiTestOpenPrompt() abort
  call s:OpenPromptBuffer()
endfunction

function! VimaiTestSubmitPrompt() abort
  call s:SubmitPromptBufferWithRunner(function('s:TestPromptRunner'))
endfunction

function! s:TestPromptRunner(prompt) abort
  let s:test_submitted_prompt = a:prompt
  call s:ShowInScratchBuffer(a:prompt, ['test response'])
endfunction

function! VimaiTestSubmittedPrompt() abort
  return s:test_submitted_prompt
endfunction

function! VimaiTestIsAgentPrompt(prompt) abort
  return s:IsAgentPrompt(a:prompt)
endfunction

function! VimaiTestPythonCommand() abort
  return s:python_cmd
endfunction

function! VimaiTestMainScript() abort
  return s:main_script
endfunction
