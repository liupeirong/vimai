---
applyTo: "**/*.py"
---

# Python Code Review Guidelines

Use this file for Python-specific review focus only.

Canonical style and design rules live in docs/standards/python-standards.md.

When reviewing changed Python files, prioritize in this order:

1. Correctness and regression risk.
2. Missing or weak tests for behavior changes.
3. Reliability and security issues.
4. Type-safety and public API clarity.

Required validation checks:

- Python version alignment with project settings (3.13).
- Ruff lint and formatting must pass.
- Public APIs should be type-annotated per project config.
- New or changed behavior should have corresponding pytest coverage.

Review output expectations:

- Findings first, ordered by severity.
- Include concrete file references and actionable fixes.
- If no issues are found, explicitly state that and note any residual test gaps.
