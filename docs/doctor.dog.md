# Behavior: Doctor

## Condition

- The `@User` or `@Agent` wants to validate that `cheap-search` and its providers are correctly configured on the local machine.

## Description

The `@User` runs `cheap-search doctor`. The `#CLI` collects a `&ProviderStatus` for each known provider (Grok, Codex) by consulting `#ApiKeyResolver` (for Grok) and `#CodexInvoker` (for Codex binary presence), then prints a structured summary. Each check includes a remediation hint so callers know how to fix any failure.

## Outcome

- Exits 0 if every provider check passes.
- Exits 1 if any provider is misconfigured, so CI and agent self-diagnostic loops can branch on the exit code.
- `--output text` (default) prints a tabular summary with green/red status per provider.
- `--output json` prints a list of `&ProviderStatus` for agent consumption.

## Notes

- `doctor` never makes a network call; it only inspects local state. A green Grok status means a key is reachable, not that the xAI API is up.
- Designed to be the first command an `@Agent` runs when troubleshooting a failed search.
