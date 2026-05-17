# Component: ConfigStore

## Description

Reads and writes the persistent `&Config` TOML file at `$XDG_CONFIG_HOME/cheap-search/config.toml` (default `~/.config/cheap-search/config.toml`). Used by `!SetGrokApiKey`, `!UnsetGrokApiKey`, and indirectly by `#ApiKeyResolver`. Writes are atomic (write-to-temp then `os.replace`) so a crash mid-write cannot corrupt the file.

## State

- config_path: resolved absolute path to `config.toml`
- config_dir: parent directory of `config_path`, created with mode `0700` if missing
- file_mode: `0600`, enforced on every write

## Events

- config_loaded
- config_written
- config_deleted

## Notes

- The file mode and directory mode are enforced on every write, not just creation; if the user later relaxes them, the next write tightens them again.
- An empty `&Config` (no keys remaining after an unset) is deleted rather than left as an empty TOML file.
- Unrelated keys are preserved on partial updates; only the targeted section is mutated.
