" vimai.vim - Vim plugin for inline LLM queries (F01, F03, F04)
"
" Usage:
"   :AI <prompt>   Send a prompt to the LLM; response opens in a vertical split
"   :ai <prompt>   Alias (cabbrev) for :AI
"
" Requirements:
"   python main.py must be on PATH or VIMAI_SCRIPT env var must point to it.
"   AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_DEPLOYMENT must be set.

if exists('g:loaded_vimai')
  finish
endif
let g:loaded_vimai = 1

" Allow :ai as a command-line abbreviation for :AI so users can type lowercase.
cabbrev ai AI

" Resolve the path to main.py relative to this plugin file so the plugin
" works regardless of the user's working directory.
let s:plugin_dir = expand('<sfile>:p:h:h')
let s:main_script = s:plugin_dir . '/main.py'

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

" :AISession  – show the session file path for this Vim process (for debugging).
command! AISession echo 'Session file: ' . s:session_file

" Buffer number of the AI response scratch buffer; -1 means not yet created.
let s:ai_bufnum = -1

" Core display logic — separated from system() so it can be driven by tests.
function! s:ShowInScratchBuffer(prompt, lines) abort
  let l:orig_winid = win_getid()
  let l:entry = ['> ' . a:prompt, ''] + a:lines

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

function! s:RunAI(prompt) abort
  " Slash commands (/clear, /purge, /help) are passed via --command <name>
  " rather than as a positional argument. This avoids MSYS2/Git Bash path
  " conversion, which silently rewrites positional args starting with '/'
  " to Windows file paths, causing them to reach the LLM as normal prompts.
  let l:subcmd = matchstr(a:prompt, '^\s*/\zs\w\+\ze\s*$')
  if l:subcmd !=# ''
    let l:cmd = 'python ' . shellescape(s:main_script) .
          \ ' --command ' . shellescape(l:subcmd) .
          \ ' --session ' . shellescape(s:session_file)
  else
    let l:cmd = 'python ' . shellescape(s:main_script) .
          \ ' --session ' . shellescape(s:session_file) .
          \ ' ' . shellescape(a:prompt)
  endif
  " On Windows with cmd.exe the OEM code page (e.g. CP437/CP1252) mangles
  " UTF-8 multi-byte sequences before Vim sees them. Force UTF-8 (chcp 65001)
  " so Python's output is passed through unchanged.
  " win32unix (Git Bash / MSYS2) uses a POSIX shell and handles UTF-8 natively.
  if (has('win32') || has('win64')) && !has('win32unix')
    let l:response = system('chcp 65001 >nul 2>&1 & ' . l:cmd)
  else
    let l:response = system(l:cmd)
  endif
  let l:response = substitute(l:response, '\r', '', 'g')

  " /clear also wipes the scratch buffer so the user gets a visual signal
  " that the conversation history is gone.
  if l:subcmd ==# 'clear'
    call s:ClearScratchBuffer(split(l:response, "\n"))
  else
    call s:ShowInScratchBuffer(a:prompt, split(l:response, "\n"))
  endif
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
endfunction

" Return the current scratch buffer number — used by vader assertions.
function! VimaiTestBufnum() abort
  return s:ai_bufnum
endfunction
