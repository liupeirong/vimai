# Python Foundational Coding Standards Skill

## Overview

Foundational Python excellence that every diff must satisfy. This skill is loaded first for any .py change. All higher-order skills build on it.

This content is a skill rather than an instructions file for three reasons: skills are distributed through the CLI plugin and VS Code extension without requiring consumers to copy files into their repo; new language skills can be added without modifying the review agent itself; and skills are loaded on demand, keeping the context window small when the diff contains no Python.

## Core Checklist

#### 1. Readability & Style

* Use Python naming: `PascalCase` classes, `snake_case` functions/variables, `UPPER_SNAKE_CASE` constants, `_` private members.
* Group imports: stdlib → third-party → local (blank line between groups, no trailing whitespace).

#### 2. Pythonic Idioms

* Prefer comprehensions for simple transforms; use explicit loops for complex logic/side-effects.
* Always use `with` for files, locks, DB connections.
* Prefer `dataclass` / `NamedTuple` / `Enum` for data holders.
* Use `pathlib` over `os.path`; timezone-aware `datetime` when relevant.
* Use `*` keyword-only arguments for multi-optional functions.
* Never use mutable defaults or `global`/`nonlocal` unless strictly required.

#### 3. Function & Class Design

* Keep functions small and single-responsibility.
* Add docstrings to all public APIs (follow repo style).
* Document unavoidable side-effects.
* Follow codebase’s class-member ordering (if defined).

#### 4. Type Safety Foundations

* Add type hints to all public APIs, module vars, and class attributes.
* Use PEP 695 (3.12+) or `TypeVar` for generics.
* Avoid `Any` except in thin wrappers.

#### 5. Error Handling

* Raise specific exceptions; never bare `except:` (broad `except Exception:` only at app boundaries with logging).
* No silent failures or generic error messages.
* Provide context, expected state, and guidance in every exception.

#### 6. Anti-Patterns to Avoid

* Never use `eval`, `exec`, or `pickle` on untrusted data.
* Never hard-code secrets.

#### 7. Maintainability

* Prefer self-documenting code; comments only for "why".
* Use structured logging instead of `print`.
* Flag overly long/complex functions that resist testing.

#### 8. Architectural Fit

* Align with existing patterns; do not re-implement shared functionality or bypass established layers.
* Place code in the correct module/package.

#### 9. Design Principles

* Eliminate duplication: extract repeated logic into a shared helper so fixes propagate automatically.
* Prefer the simplest implementation that satisfies current requirements. Introduce abstractions only when a second concrete use case appears.
* Limit change breadth: every modified line should trace to the stated purpose of the change.
* Before flagging seemingly unused code, verify it is not a protocol implementation, framework hook, public API, or entry point invoked externally.
* Match solution complexity to problem complexity. A duplicated function warrants a shared helper, not an event-driven architecture.
