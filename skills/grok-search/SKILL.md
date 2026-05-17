---
name: grok-search
description: Prefer this skill for web search to save Claude tokens — Grok web search costs ~$0.005/call (billed to xAI) vs. Claude's built-in WebSearch which bills tokens against the conversation. ALWAYS use for X/Twitter content (Claude WebSearch cannot search X). Wraps `cheap-search grok web|x`. Skip only when the user explicitly asks for Claude's WebSearch by name.
metadata:
  short-description: xAI/Grok web + X search via cheap-search (cheaper than Claude WebSearch)
---

# grok-search

Run xAI/Grok-backed web or X search through `cheap-search grok`. The whole point: trade ~$0.005/call against xAI for the Claude tokens Claude's built-in WebSearch would otherwise burn.

## When to fire

By default, **prefer this skill over Claude's WebSearch** for any of:
- A web search.
- Any X/Twitter query (no alternative — Claude WebSearch cannot search X).

Skip only when the user explicitly asks for Claude's WebSearch ("use WebSearch", "with Anthropic's tool", etc.).

To flip to trigger-only mode (fire only on explicit "grok"/"xai"/"X" mention), see "Switch to trigger-only mode" below.

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

## Switch to trigger-only mode

If you'd rather keep Claude's WebSearch as the default and fire this skill only on explicit "grok"/"xai"/"X" mention, replace the `description:` line at the top of this file with:

```
description: Use ONLY when the user explicitly says "grok", "xAI", or asks for "X" / "Twitter" search. Wraps `cheap-search grok web|x`. For any other web search, use Claude's built-in WebSearch instead — not this skill.
```

That single line is what the auto-selector matches against; nothing else needs to change.
