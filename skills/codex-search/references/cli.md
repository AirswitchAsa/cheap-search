# cheap-search codex — CLI reference

Use `cheap-search codex --help` and `codex exec --help` for the authoritative lists.

## `cheap-search codex "<query>"`

cheap-search shells out to `codex exec "<query>"` and streams its stdout. There are no cheap-search-side knobs. Everything after `--` is forwarded to `codex` verbatim.

```bash
cheap-search codex "<query>"
cheap-search codex "<query>" -- --skip-git-repo-check
cheap-search codex "<query>" -- -m gpt-5-codex
cheap-search codex "<query>" -- -c model="gpt-5-codex" --skip-git-repo-check
```

## Common forwarded codex flags

| Flag | Purpose |
|---|---|
| `--skip-git-repo-check` | Required when cwd is not a trusted git repo. |
| `-m, --model MODEL` | Override the model codex uses. |
| `-c key=value` | Override any codex config entry (TOML). |
| `-i, --image FILE` | Attach images to the prompt. |
| `--enable FEATURE` | Toggle a codex feature flag. |

## Configuration

Authentication is codex's responsibility — `codex login` once per machine. cheap-search does not touch codex credentials.

## Exit codes

- `0` codex completed successfully
- `2` `codex` binary not on PATH
- `3` codex exited non-zero; its stderr is already on the terminal
