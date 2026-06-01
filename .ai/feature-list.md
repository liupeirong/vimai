# VIM.AI feature list

> Note: Work with the user to record features in the features field of this TypeScript interface:
enum status_legend {
    not_started, // Work has not begun
    in_progress, // The feature is the current active task
    blocked, // Work cannot continue until a documented blocker is resolved
    passing // Required verification has passed and evidence is recorded
},
interface feature_list {
  last_updated: string, // YYYY-MM-DD HH-mm
  feature: {
    id: string; // ex. "vi-plugin-001",
    priority: number; // 1, 2, 3 - from high to low
    area: string; // ex. "vim plugin", "llm integration", "memory management"
    title: string;
    user_visible_behavior: string; // what can the user do?
    status: status_legend;
    verification: string[]; // what needs to be true to call the feature complete
    evidence: string[]; // what's validated
    notes: string; // anything to note about this feature
  }[]
}

```json
{
  "last_updated": "2026-06-01 10:04",
  "feature": [
    {
      "id": "infra-001",
      "priority": 1,
      "area": "engineering harness",
      "title": "AI autonomous work harness",
      "user_visible_behavior": "An AI agent can pick up the repo cold, understand what to build next, implement one feature at a time, verify it, and leave the repo in a clean resumable state without human intervention between sessions.",
      "status": "passing",
      "verification": [
        "CLAUDE.md exists with startup checklist, rules, completion gate, and shutdown procedure",
        "feature-list.md exists with schema and at least one recorded feature",
        "claude-progress.md exists with session log schema including current_feature anchor",
        "clean-state-checklist.md exists covering build, runtime, and repository hygiene",
        "docs/ARCHITECTURE.md exists with section headings as placeholders",
        "All filenames referenced in CLAUDE.md resolve to actual files",
        "Commit format instruction references a real file (.github/instructions/general-review.instructions.md)"
      ],
      "evidence": [
        "Human+AI review on 2026-06-01: all cross-references verified correct",
        "Typo in ruff check command fixed, filename mismatch fixed, feature selection rule clarified",
        "current_feature anchor added to progress log schema",
        "Completion gate explicitly references evidence field in feature-list.md"
      ],
      "notes": "ARCHITECTURE.md section headings are intentional placeholders; content will be filled collaboratively before feature implementation begins."
    }
  ]
}
```
