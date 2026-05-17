from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from dotenv import load_dotenv


_REPO_ROOT = Path(__file__).resolve().parent.parent


def pytest_configure(config: pytest.Config) -> None:
    load_dotenv(_REPO_ROOT / ".env", override=False)


@pytest.fixture
def isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point ConfigStore at a per-test XDG dir and drop XAI_API_KEY from env."""
    xdg = tmp_path / "xdg"
    xdg.mkdir()
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg))
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    return xdg / "cheap-search" / "config.toml"


class _Redacted(str):
    """A str subclass whose repr never exposes the underlying value.

    Pytest prints fixture argument values in tracebacks (-v mode); wrapping
    the API key in this type ensures the actual secret never appears in
    test output, logs, or CI artifacts.
    """

    __slots__ = ()

    def __repr__(self) -> str:
        return "<redacted-secret>"


@pytest.fixture
def live_grok_key() -> Iterator[str]:
    """Yield a real xAI key from the environment, or skip the test.

    The returned string redacts its repr so it cannot leak into pytest output.
    """
    key = os.environ.get("XAI_API_KEY")
    if not key:
        pytest.skip("XAI_API_KEY not set; live Grok tests require a real key")
    yield _Redacted(key)


@pytest.fixture
def live_codex() -> Iterator[str]:
    """Yield the resolved codex binary path, or skip the test."""
    import shutil

    binary = shutil.which("codex")
    if not binary:
        pytest.skip("`codex` not on PATH; live Codex tests require the CLI installed")
    yield binary
