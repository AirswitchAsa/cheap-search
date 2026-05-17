# Behavior: GrokXSearch

## Condition

- The `@User` (or `@Agent` on their behalf) wants to search X (formerly Twitter) posts through xAI / Grok.
- A valid xAI API key is resolvable by `#ApiKeyResolver`.

## Description

The `@User` runs `cheap-search grok x "<query>"`. The `#CLI` resolves the xAI API key via `#ApiKeyResolver`, constructs a `#GrokClient` agentic chat with the xAI `x_search` server-side tool, and prints the model's synthesized answer plus any citations as a `&SearchResponse`.

Optional knobs map 1:1 to the xAI SDK:
- `--model`, `--reasoning-effort`, `--max-tokens`, `--temperature` (same as `!GrokWebSearch`)
- `--from YYYY-MM-DD`, `--to YYYY-MM-DD` to scope the date window
- `--handle HANDLE` (repeatable) to whitelist X accounts
- `--exclude-handle HANDLE` (repeatable; mutually exclusive with `--handle`)
- `--enable-image-understanding`, `--enable-video-understanding`

## Outcome

- On success, prints a `&SearchResponse` to stdout and exits 0.
- `--output text|json` behaves identically to `!GrokWebSearch`.
- Missing API key exits 2; provider failure exits 3.
- Invalid date formats exit 1 with a usage error from Typer.

## Notes

- Date filters live on the `x_search` tool itself, not on a top-level search parameters object.
- Handle filters use the bare username (no leading `@`); the CLI strips a leading `@` for convenience.
- `--handle` and `--exclude-handle` cannot be combined; the CLI rejects this at parse time.
