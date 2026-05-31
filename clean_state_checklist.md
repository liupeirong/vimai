# Clean State Checklist

Run this checklist before committing and at the end of each session.

## Build

- [ ] `ruff format .` completes successfully
- [ ] `ruff checking .` passes with no type error
- [ ] `pytest .` passes with no type error

## Architecture

- [ ] `bash scripts/check-architecture.sh` passes with no violations

## Runtime

- [ ] Application starts without errors (`python ...`)
- [ ] Structured log output appears in console at startup
- [ ] Q&A returns answers with citations (check logs for ASK_QUESTION event)

## Data Integrity

- [ ] Q&A history persists across restarts
- [ ] Document metadata is consistent with actual files

## Repository

- [ ] No unintended files in git status
- [ ] No sensitive data (.env, credentials) staged
- [ ] Final summary records current state, verification run, and any unresolved risk
- [ ] `CLAUDE.md`, `docs/ARCHITECTURE.md`, and this checklist still match the files that actually exist in this repo