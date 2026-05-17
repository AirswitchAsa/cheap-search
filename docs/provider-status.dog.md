# Data: ProviderStatus

## Description

Diagnostic record describing the configuration state of a single provider. Returned by `!ShowGrokApiKeyStatus` and aggregated by `!Doctor`. Produced by `#ApiKeyResolver` for Grok and by `#CodexInvoker` for Codex.

## Fields

- provider: provider name (`grok` or `codex`)
- ok: boolean indicating whether the provider is usable as currently configured
- source: where the credential or binary was found (`env`, `config`, `path`, or `none`)
- shadowed_by: optional source name that overrides `source` (e.g. `env` shadows `config` for Grok)
- masked_value: masked tail of the credential, or absolute path for `codex`; never the full secret
- remediation: short human-readable string suggesting how to fix a failing check

## Notes

- `remediation` is always populated so `!Doctor` output is self-explanatory without external docs.
- `masked_value` for Grok shows the last four characters prefixed with bullets (e.g. `xai-••••••••abcd`); for Codex it is the resolved `PATH` entry.
- A successful Grok status with `source = env` and `shadowed_by` set means the user has *both* configured and the env value is winning.
