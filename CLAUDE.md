# CLAUDE.md

You are working in a repository designed for long-running implementation work.
Prioritize reliable completion, continuity across sessions, and explicit
verification over speed.

## Before You Begin Implementing Features

1. Run `pwd` and confirm you are in the expected repository root.
2. Read `.ai/claude-progress.md`.
3. Read `.ai/feature-list.md`.
4. Review recent commits with `git log --oneline -5`.
5. Install or sync dependencies with `uv sync`.
6. Check if tests are already broken with `pytest`.

Then select exactly the highest priority unfinished feature and
work only on that feature until you either verify it or document
why it is blocked.

## Rules

- One active feature at a time.
- Do not claim completion without runnable evidence.
- Do not rewrite the feature list to hide unfinished work.
- Do not remove or weaken tests just to make the task look complete.
- Use repository artifacts as the system of record.

## Completion Gate

A feature can move to `passing` only after the required verification succeeds
and the result is recorded in the `evidence` field of `.ai/feature-list.md`.

## Before You Stop

1. Update progress log in `.ai/claude-progress.md` by recording:
    - current feature state,
    - new decisions made,
    - what is verified, unverified, or broken
    - any unresolved risk
2. Check `.ai/clean-state-checklist.md` to leave the repo in a clean state for the next session.
3. Commit once the repository is clean and safe to resume using the commit format in `.github/instructions/general-review.instructions.md`.
