# Data: Config

## Description

The persistent on-disk configuration managed by `#ConfigStore`. Stored as TOML at `$XDG_CONFIG_HOME/cheap-search/config.toml` with file mode `0600`.

## Fields

- grok.api_key: optional xAI API key string written by `!SetGrokApiKey`

## Notes

- The schema is intentionally flat in v0; new providers add their own top-level table (e.g. `[exa]`) rather than nesting under a shared `[providers]` table.
- The file is deleted by `#ConfigStore` when it ends up empty after an `!UnsetGrokApiKey`, so the absence of the file is the canonical "nothing configured" state.
- Hand-editing the file is supported but the `apikey` subcommands are preferred because they enforce the correct file mode.
