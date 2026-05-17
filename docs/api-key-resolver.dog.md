# Component: ApiKeyResolver

## Description

Resolves the xAI API key for the current invocation by consulting the environment first and falling back to `#ConfigStore`. Used by `!GrokWebSearch`, `!GrokXSearch`, `!ShowGrokApiKeyStatus`, and `!Doctor`. Produces a `&ProviderStatus` so callers can report on the resolution outcome without re-implementing the precedence logic.

## State

- env_value: contents of `XAI_API_KEY` if set
- file_value: `[grok].api_key` from `&Config` if present
- active_source: `env`, `config`, or `none` after resolution
- masked_tail: last four characters of the resolved key, used for display

## Events

- key_resolved
- key_missing

## Notes

- The env variable wins when both sources are present. This matches `gh` and `aws` behavior and lets CI override per-job without touching the file.
- The full key never leaves this component except as a return value to the `#GrokClient`; `&ProviderStatus` only carries the masked tail.
- If neither source is set, the resolver returns a `&ProviderStatus` with `active_source = none` rather than raising; the calling behavior decides whether that is fatal.
