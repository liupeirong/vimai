# Clean State Checklist

Run this checklist before committing and at the end of each session.

## Build

- [ ] `ruff format .` completes successfully
- [ ] `ruff checking .` passes with no type error
- [ ] `pytest .` passes with no type error

## Runtime

- [ ] Application starts without errors (`python main.py`)
- [ ] Structured log output appears in console at startup

## Repository

- [ ] No unintended files in git status
- [ ] No sensitive data (.env, credentials) staged
- [ ] `CLAUDE.md`, `docs/ARCHITECTURE.md`, and this checklist still match the files that actually exist in this repo
