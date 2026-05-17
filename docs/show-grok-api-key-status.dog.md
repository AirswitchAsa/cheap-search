# Behavior: ShowGrokApiKeyStatus

## Condition

- The `@User` (or `@Agent`) wants to know whether an xAI API key is currently configured and where it is coming from.

## Description

The `@User` runs `cheap-search grok apikey status`. The `#CLI` invokes `#ApiKeyResolver` to determine the active key source and prints a `&ProviderStatus` describing it: env var, `&Config` file, both, or neither. The actual key is never printed in full — only the last four characters appear, prefixed with bullets (e.g. `xai-••••••••abcd`).

## Outcome

- Always exits 0; this is a diagnostic, not a check.
- `--output text` (default) prints a human-readable status line.
- `--output json` prints `&ProviderStatus` as a single JSON object suitable for agent consumption.

## Notes

- When both the env var and `&Config` are set, the message must call out that the env var is "active" and the file is "shadowed" — env wins per `#ApiKeyResolver`.
- The masked tail lets the `@User` confirm which key is loaded without leaking it to history or screen recordings.
