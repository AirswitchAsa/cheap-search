# Component: CLI

## Description

The command-line interface component built with Typer. Provides the `cheap-search` command with provider-scoped subcommand trees for `!GrokWebSearch`, `!GrokXSearch`, `!CodexSearch`, the `apikey` subgroup (`!SetGrokApiKey`, `!UnsetGrokApiKey`, `!ShowGrokApiKeyStatus`), `!Doctor`, and `!ListProviders`. Handles argument parsing, output formatting, user feedback, and exit codes.

## State

- output_format: `text` or `json`
- exit_code: 0 success, 1 invalid usage, 2 missing configuration, 3 provider failure
- provider: the user-selected provider for the current invocation (`grok` or `codex`)

## Events

- grok_web_command
- grok_x_command
- grok_apikey_set_command
- grok_apikey_unset_command
- grok_apikey_status_command
- codex_command
- doctor_command
- providers_command

## Notes

- Uses Typer for argument parsing, sub-typers for provider scoping, and `--version` / `-v` at the root.
- Async operations are wrapped in `asyncio.run()` inside each handler, matching the convention used by sibling projects in this organization.
- Provider selection is explicit: the `#CLI` never dispatches a query to a different provider than the one named on the command line.
