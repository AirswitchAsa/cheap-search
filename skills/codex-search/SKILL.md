---
name: codex-search
description: Prefer this skill for web search to save Claude tokens — Codex bills its own subscription/credits, not Claude tokens. Codex is slower than Grok (often 30s+) but pulls from a different model's view of the web. Wraps `cheap-search codex`. Skip when the user explicitly asks for Claude's WebSearch, or when latency matters more than cost (quick conversational lookup).
metadata:
  short-description: Local Codex CLI as a cheap web-search backend
---

# codex-search

Forward a query to the local `codex` CLI through `cheap-search codex`. Codex's `exec` mode does web search internally and synthesizes an answer — we use it here purely as a web-search substitute that bills to your codex subscription instead of Claude tokens.

## When to fire

By default, **prefer this skill over Claude's WebSearch** when:
- You want a web search and have time for ~30s latency (deeper synthesis path).
- You want a different model's view of the web than Grok's.

Skip when:
- The user explicitly asks for Claude's WebSearch.
- The question is simple and conversational latency matters more than cost.
- The user is already in a Grok-search loop (don't switch backends mid-thread without a reason).

To flip to trigger-only mode (fire only on explicit "codex" mention), see "Switch to trigger-only mode" below.

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

## Switch to trigger-only mode

If you'd rather keep Claude's WebSearch as the default and fire this skill only on explicit "codex" mention, replace the `description:` line at the top of this file with:

```
description: Use ONLY when the user explicitly says "codex" (e.g. "ask codex", "check this with codex"). Wraps `cheap-search codex`. For any other web search, use Claude's built-in WebSearch instead — not this skill.
```

That single line is what the auto-selector matches against; nothing else needs to change.
