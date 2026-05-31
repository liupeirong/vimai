---
applyTo: "**"
---

# General Code Review Guidelines

## Git Conventions

- Commits must follow Conventional Commits: `type(scope): description`
- PR descriptions must explain what changed and why

## Cross-Cutting Concerns

- No credentials, API keys, or secrets in source code
- YAML/TOML/JSON configs: validate syntax, check for hardcoded values
- Shell scripts: require `set -euo pipefail`, proper quoting, error handling
- Dockerfiles: no root user, efficient layer ordering, minimal image size
- Documentation changes: verify links, heading structure, grammar

## Project Context

- Tech stack: Python 3.13, PyTorch, LeRobot, Azure ML SDK v2, MLflow
- Package manager: uv (not pip)
- Bilingual team: English (primary), Japanese
