from __future__ import annotations

import asyncio
import shutil
import sys

from cheap_search.models import ProviderStatus


CODEX_BINARY = "codex"


class CodexMissingError(RuntimeError):
    pass


class CodexInvoker:
    def find_binary(self) -> str | None:
        return shutil.which(CODEX_BINARY)

    def status(self) -> ProviderStatus:
        binary = self.find_binary()
        if binary:
            return ProviderStatus(
                provider="codex",
                ok=True,
                source="path",
                masked_value=binary,
                remediation="",
            )
        return ProviderStatus(
            provider="codex",
            ok=False,
            source="none",
            remediation=(
                "Install the `codex` CLI and ensure it is on PATH "
                "(see https://github.com/openai/codex)."
            ),
        )

    async def run(
        self,
        query: str,
        forwarded: list[str] | None = None,
        *,
        stdout: int | None = None,
        stderr: int | None = None,
    ) -> int:
        binary = self.find_binary()
        if not binary:
            raise CodexMissingError(
                "`codex` not found on PATH. Install it from https://github.com/openai/codex"
            )
        args = [binary, "exec", query]
        if forwarded:
            args.extend(forwarded)
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=stdout if stdout is not None else _safe_fileno(sys.stdout),
            stderr=stderr if stderr is not None else _safe_fileno(sys.stderr),
        )
        return await proc.wait()


def _safe_fileno(stream: object) -> int | None:
    """Return the OS fd backing the stream, or None when there isn't one.

    CliRunner replaces sys.stdout/sys.stderr with in-memory buffers that
    raise UnsupportedOperation on fileno(); falling back to None makes
    asyncio inherit the parent's fds instead.
    """
    try:
        return stream.fileno()  # type: ignore[attr-defined]
    except (AttributeError, OSError, ValueError):
        return None
