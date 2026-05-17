# Component: CodexInvoker

## Description

Spawns the local `codex` binary as a subprocess and streams its stdout to the caller. Uses `shutil.which("codex")` for binary detection and `asyncio.create_subprocess_exec` for invocation so that `!CodexSearch` can stream output in real time without holding the GIL on a blocking read.

## State

- binary_path: resolved absolute path to `codex`, or `None` if not found
- query: the user-supplied query string
- forwarded_args: arbitrary trailing arguments passed after `--`
- exit_code: the subprocess's exit code, propagated by the `#CLI`

## Events

- codex_missing
- codex_started
- codex_exited

## Notes

- Does not parse codex output; it is streamed verbatim. JSON normalization is explicitly out of scope for v0.
- Does not touch codex authentication; `codex login` is the user's responsibility.
- The forwarded-args mechanism lets new codex flags work immediately without a `cheap-search` release.
