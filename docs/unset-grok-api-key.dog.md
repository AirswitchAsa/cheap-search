# Behavior: UnsetGrokApiKey

## Condition

- The `@User` wants to remove the locally persisted xAI API key from `&Config`.

## Description

The `@User` runs `cheap-search grok apikey unset`. The `#CLI` asks `#ConfigStore` to delete the `[grok].api_key` entry from `&Config` while leaving all unrelated keys intact. If the resulting file is empty, `#ConfigStore` deletes it.

## Outcome

- On success, prints `xAI API key removed` and exits 0, regardless of whether a key was actually present (idempotent).
- If `&Config` exists but cannot be written, exits 3 with the underlying OS error.

## Notes

- This does not unset the `XAI_API_KEY` environment variable; the `@User` is told to also `unset XAI_API_KEY` in their shell if they want to fully revoke local access.
- Idempotent on purpose so scripts can call it unconditionally.
