" vimai.vim - Vim plugin for inline LLM queries (F01, F03)
"
" Usage:
"   :AI <prompt>   Send a prompt to the LLM; response prints like :! output
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

function! s:RunAI(prompt) abort
  let l:cmd = 'python ' . shellescape(s:main_script) .
        \ ' --session ' . shellescape(s:session_file) .
        \ ' ' . shellescape(a:prompt)
  execute '!' . l:cmd
endfunction
