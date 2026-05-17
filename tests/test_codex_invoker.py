from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

import pytest

from cheap_search.codex_invoker import CodexInvoker, CodexMissingError


class TestCodexInvokerOffline:
    def test_status_missing_when_not_on_path(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("PATH", str(tmp_path))
        invoker = CodexInvoker()
        status = invoker.status()
        assert not status.ok
        assert status.source == "none"
        assert "codex" in status.remediation.lower()

    def test_status_ok_when_on_path(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        fake = tmp_path / "codex"
        fake.write_text("#!/bin/sh\nexit 0\n")
        fake.chmod(0o755)
        monkeypatch.setenv("PATH", str(tmp_path))
        invoker = CodexInvoker()
        status = invoker.status()
        assert status.ok
        assert status.source == "path"
        assert status.masked_value == str(fake)

    async def test_run_raises_when_missing(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("PATH", str(tmp_path))
        invoker = CodexInvoker()
        with pytest.raises(CodexMissingError, match="not found"):
            await invoker.run("hello")

    async def test_run_propagates_subprocess_exit_code(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        # Fake codex that accepts `exec <prompt>` and exits non-zero.
        fake = tmp_path / "codex"
        fake.write_text("#!/bin/sh\nexit 42\n")
        fake.chmod(0o755)
        monkeypatch.setenv("PATH", str(tmp_path))
        invoker = CodexInvoker()
        exit_code = await invoker.run(
            "hello",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        assert exit_code == 42

    async def test_run_forwards_extra_args(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        out = tmp_path / "out.txt"
        fake = tmp_path / "codex"
        fake.write_text(f'#!/bin/sh\nprintf "%s\\n" "$@" > {out}\n')
        fake.chmod(0o755)
        monkeypatch.setenv("PATH", str(tmp_path))
        invoker = CodexInvoker()
        await invoker.run(
            "the-prompt",
            forwarded=["--model", "fake-model"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        captured = out.read_text().splitlines()
        assert captured == ["exec", "the-prompt", "--model", "fake-model"]


@pytest.mark.live
class TestCodexInvokerLive:
    async def test_run_real_codex(self, live_codex: str, tmp_path: Path) -> None:  # noqa: ARG002 - fixture for skip
        out = tmp_path / "stdout.log"
        err = tmp_path / "stderr.log"
        with out.open("wb") as o, err.open("wb") as e:
            invoker = CodexInvoker()
            exit_code = await asyncio.wait_for(
                invoker.run(
                    "Reply with the single word: pong",
                    forwarded=["--skip-git-repo-check"],
                    stdout=o.fileno(),
                    stderr=e.fileno(),
                ),
                timeout=120,
            )
        assert exit_code == 0
        combined = (out.read_text() + err.read_text()).lower()
        assert "pong" in combined
