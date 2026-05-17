# Behavior: GrokWebSearch

## Condition

- The `@User` (or `@Agent` on their behalf) wants to run a web search through xAI / Grok.
- A valid xAI API key is resolvable by `#ApiKeyResolver` (env var or `&Config`).

## Description

The `@User` runs `cheap-search grok web "<query>"`. The `#CLI` resolves the xAI API key via `#ApiKeyResolver`, constructs a `#GrokClient` agentic chat with the xAI `web_search` server-side tool, and prints the model's synthesized answer plus any citations as a `&SearchResponse`.

Optional knobs map 1:1 to the xAI SDK:
- `--model` (default `grok-4.3`)
- `--reasoning-effort {none,low,medium,high}`
- `--max-tokens`, `--temperature`
- `--allowed-domain` / `--excluded-domain` (repeatable; mutually exclusive; max 5 each)
- `--enable-image-understanding`

## Outcome

- On success, prints a `&SearchResponse` to stdout and exits 0.
- `--output text` (default) prints the model answer followed by a citations block.
- `--output json` prints `&SearchResponse` as a single JSON object.
- Missing API key exits 2 with a message naming both fix paths (env var or `!SetGrokApiKey`).
- Provider failure (network, xAI 4xx/5xx, gRPC error) exits 3 with the underlying error on stderr.

## Notes

- Tool calls billed at ~$0.005 each by xAI; Grok decides fan-out internally and the CLI does not cap it.
- The xAI Live Search API was deprecated 2026-01-12; `#GrokClient` uses the Agent Tools API only.
- Citations come back as part of the response if the tool fired; the CLI never strips them.
