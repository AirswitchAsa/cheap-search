---
name: codex-search
description: Use ONLY when the user explicitly says "codex" (e.g. "ask codex", "check this with codex", "use codex to …"). Wraps `cheap-search codex`. For any other coding question, answer it yourself — this skill is not a shortcut to outsource general code help.
metadata:
  short-description: Local Codex CLI passthrough via cheap-search
---

# codex-search

Forward a query to the local `codex` CLI through `cheap-search codex`.

## When to fire

Only on explicit mention of codex:
- "ask codex …"
- "check with codex …"
- "use codex to …"

Anything else: answer it yourself. This skill is not a default for code help.

## Bootstrap

```bash
scripts/ensure-cheap-search.sh
```

## Command

```bash
cheap-search codex "<query>"
```

Trailing args after `--` pass through to `codex`:

```bash
cheap-search codex "<query>" -- --skip-git-repo-check
cheap-search codex "<query>" -- -m gpt-5-codex
```

`--skip-git-repo-check` is required when the working directory is not a trusted git repo.

## Configuration

Authentication is codex's own concern: run `codex login` if not already authenticated. `cheap-search` does not handle codex credentials.

## Exit codes

- `0` success
- `2` `codex` not on PATH — point the user at https://github.com/openai/codex
- `3` codex failed — its stderr is already on the user's terminal
