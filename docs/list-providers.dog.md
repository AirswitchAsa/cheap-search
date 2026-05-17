# Behavior: ListProviders

## Condition

- The `@User` or `@Agent` wants to discover which providers `cheap-search` supports without reading the help text.

## Description

The `@User` runs `cheap-search providers`. The `#CLI` prints the static list of providers wired into this binary (`grok`, `codex` in v0). Each entry includes the provider name, the subcommand prefix, and a one-line description.

## Outcome

- Always exits 0.
- `--output text` prints one line per provider.
- `--output json` prints `{"providers": [{"name": "...", "command": "...", "description": "..."}, ...]}`.

## Notes

- This is a discoverability aid, not a capability negotiation. Adding a provider requires shipping a new `cheap-search` release.
- Kept intentionally cheap so agents can call it without cost concerns.
