" vimai.vim - Vim plugin for inline LLM queries (F01)
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

" :AI <prompt>  – run prompt through vimai and display response inline.
command! -nargs=+ AI call s:RunAI(<q-args>)

function! s:RunAI(prompt) abort
  let l:cmd = 'python ' . shellescape(s:main_script) . ' ' . shellescape(a:prompt)
  execute '!' . l:cmd
endfunction
