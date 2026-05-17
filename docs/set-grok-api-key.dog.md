# Behavior: SetGrokApiKey

## Condition

- The `@User` wants to persist an xAI API key on the local machine so future `!GrokWebSearch` and `!GrokXSearch` invocations succeed without setting `XAI_API_KEY` each session.

## Description

The `@User` runs `cheap-search grok apikey set`. The `#CLI` prompts for the key on stdin with input echo disabled (via `typer.prompt(hide_input=True)`), then asks `#ConfigStore` to persist the key into `&Config` at `[grok].api_key`. When stdin is not a TTY, the form `cheap-search grok apikey set -` reads the key as a single line from stdin so callers can pipe (`pbpaste | cheap-search grok apikey set -`).

The key is never accepted as a positional argument or `--api-key` flag, to avoid leaks via shell history and `ps aux`.

## Outcome

- On success, writes `&Config` atomically (temp file + `os.replace`) with file mode `0600` and directory mode `0700`, prints `xAI API key saved to <path>`, and exits 0.
- If the user provides an empty key, exits 1 with a usage error and does not modify `&Config`.
- If the config file cannot be written (permissions, full disk), exits 3 with the underlying OS error.

## Notes

- The key itself is never echoed back to the terminal or written to logs.
- Existing unrelated keys in `&Config` are preserved; only `[grok].api_key` is mutated.
- See `#ApiKeyResolver` for the env-wins precedence rule that applies at lookup time.
