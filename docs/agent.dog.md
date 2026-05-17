# Actor: Agent

## Description

A coding agent (e.g. Claude Code) that invokes `cheap-search` on the `@User`'s behalf after the `@User` has explicitly requested a specific provider. The `@Agent` discovers the CLI through one of the bundled skills (`grok-search` or `codex-search`) and shells out to the binary.

## Notes

- The `@Agent` must not pick a provider on its own; provider selection is driven by the `@User`'s wording or the skill that was activated.
- The `@Agent` consumes structured JSON output (`--output json`) when reasoning over results.
- The `@Agent` never receives or handles an API key; credentials are resolved by `#ApiKeyResolver` from environment or local config.
