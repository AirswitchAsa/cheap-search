# Behavior: CodexSearch

## Condition

- The `@User` (or `@Agent` on their behalf) wants to ground a query through the local `codex` CLI.
- The `codex` executable exists on `PATH` as detected by `#CodexInvoker`.

## Description

The `@User` runs `cheap-search codex "<query>"`. The `#CLI` delegates to `#CodexInvoker`, which spawns the local `codex` binary as a subprocess and streams its stdout to the caller. The CLI performs no post-processing beyond exit-code translation.

A `--` separator forwards arbitrary trailing flags to the underlying `codex` invocation so callers can pass provider-native options (e.g. `--model`, `--cd`) without `cheap-search` mirroring every flag.

## Outcome

- On success, streams `codex` stdout to the caller's stdout and propagates `codex`'s exit code as 0.
- If `codex` is not on `PATH`, exits 2 with installation guidance.
- If `codex` exits non-zero, `#CodexInvoker` propagates exit code 3 and forwards `codex`'s stderr unchanged.

## Notes

- Output is streamed, not buffered, because `codex` runs can be long; agents see progress in real time.
- `cheap-search` does not handle codex authentication; `codex login` is the user's responsibility.
- No JSON post-processing in v0; whatever `codex` prints is what callers receive.
