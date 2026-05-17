---
name: grok-search
description: Use ONLY when the user explicitly says "grok", "xAI", or asks for "X" / "Twitter" search. Wraps `cheap-search grok web|x`. For a generic web search request ("look up X", "find an article about Y"), use Claude's built-in WebSearch instead — not this skill.
metadata:
  short-description: xAI/Grok web + X search via cheap-search
---

# grok-search

Run xAI/Grok-backed web or X search through `cheap-search grok`.

## When to fire

Only on explicit provider or source mention:
- "grok …"
- "xai …"
- "search X / Twitter for …"

Anything else: use Claude's WebSearch (web) or answer directly. This skill is not a default search router.

## Bootstrap

```bash
scripts/ensure-cheap-search.sh
```

Resolves the bundled binary, falling back to `uvx --from cheap-search cheap-search`.

## Commands

```bash
cheap-search grok web "<query>" -o json
cheap-search grok x   "<query>" -o json
cheap-search grok x   "<query>" --from 2026-01-01 --to 2026-05-17 -o json
cheap-search grok x   "<query>" --handle xai -o json
```

Always pass `-o json` so you can read `answer` and `citations`. Switch to `-o text` only when piping directly to the user.

See `references/cli.md` for the full flag matrix (model, reasoning effort, domain filters, image/video understanding).

## Configuration

The CLI reads `XAI_API_KEY` from env. On exit `2`, tell the user to `export XAI_API_KEY=…` or run `cheap-search grok apikey set`. Never type a key into a command yourself.

## Exit codes

- `0` success
- `1` usage error
- `2` missing API key — surface remediation
- `3` provider failure — surface stderr to the user
