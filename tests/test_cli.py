from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from cheap_search.config_store import ConfigStore
from cheap_search.main import app


runner = CliRunner()


class TestRoot:
    def test_version_flag(self) -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "cheap-search" in result.stdout

    def test_no_args_shows_help(self) -> None:
        result = runner.invoke(app, [])
        assert result.exit_code != 0  # Typer exits 2 when no_args_is_help
        assert "Usage" in (result.stdout + result.stderr)


class TestProviders:
    def test_text_lists_both(self) -> None:
        result = runner.invoke(app, ["providers"])
        assert result.exit_code == 0
        assert "grok" in result.stdout
        assert "codex" in result.stdout

    def test_json_output(self) -> None:
        result = runner.invoke(app, ["providers", "--output", "json"])
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        names = [p["name"] for p in payload["providers"]]
        assert names == ["grok", "codex"]


class TestGrokApikey:
    def test_status_missing(self, isolated_config: Path) -> None:  # noqa: ARG002 - fixture for env scoping
        result = runner.invoke(app, ["grok", "apikey", "status"])
        assert result.exit_code == 0
        assert "not configured" in result.stdout

    def test_status_json_missing(self, isolated_config: Path) -> None:  # noqa: ARG002
        result = runner.invoke(app, ["grok", "apikey", "status", "--output", "json"])
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload["ok"] is False
        assert payload["source"] == "none"

    def test_status_env(
        self,
        isolated_config: Path,  # noqa: ARG002
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("XAI_API_KEY", "xai-fromenvtest1234")
        result = runner.invoke(app, ["grok", "apikey", "status"])
        assert result.exit_code == 0
        assert "env" in result.stdout
        assert "1234" in result.stdout

    def test_status_env_shadows_config(
        self,
        isolated_config: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ConfigStore(path=isolated_config).set_grok_api_key("xai-fromconfig1234")
        monkeypatch.setenv("XAI_API_KEY", "xai-fromenvtest1234")
        result = runner.invoke(app, ["grok", "apikey", "status"])
        assert result.exit_code == 0
        assert "shadowed" in result.stdout.lower()

    def test_set_rejects_positional_key(self, isolated_config: Path) -> None:  # noqa: ARG002
        result = runner.invoke(app, ["grok", "apikey", "set", "xai-leak-prone"])
        assert result.exit_code == 1
        assert "shell history" in result.stderr

    def test_set_via_stdin_dash(self, isolated_config: Path) -> None:
        result = runner.invoke(app, ["grok", "apikey", "set", "-"], input="xai-piped-key\n")
        assert result.exit_code == 0
        assert "saved" in result.stdout
        assert ConfigStore(path=isolated_config).get_grok_api_key() == "xai-piped-key"

    def test_set_rejects_empty(self, isolated_config: Path) -> None:  # noqa: ARG002
        result = runner.invoke(app, ["grok", "apikey", "set", "-"], input="\n")
        assert result.exit_code == 1
        assert "empty" in result.stderr

    def test_set_via_prompt_hidden(self, isolated_config: Path) -> None:
        # Typer's prompt(hide_input=True) reads via getpass; CliRunner emulates
        # this by consuming the `input` stream regardless of TTY status.
        result = runner.invoke(app, ["grok", "apikey", "set"], input="xai-prompted-key\n")
        assert result.exit_code == 0
        assert ConfigStore(path=isolated_config).get_grok_api_key() == "xai-prompted-key"

    def test_unset_idempotent(self, isolated_config: Path) -> None:  # noqa: ARG002
        result = runner.invoke(app, ["grok", "apikey", "unset"])
        assert result.exit_code == 0
        assert "removed" in result.stdout

    def test_unset_after_set(self, isolated_config: Path) -> None:
        ConfigStore(path=isolated_config).set_grok_api_key("xai-temp")
        result = runner.invoke(app, ["grok", "apikey", "unset"])
        assert result.exit_code == 0
        assert ConfigStore(path=isolated_config).get_grok_api_key() is None

    def test_unset_warns_when_env_still_set(
        self,
        isolated_config: Path,  # noqa: ARG002
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("XAI_API_KEY", "xai-still-here")
        result = runner.invoke(app, ["grok", "apikey", "unset"])
        assert result.exit_code == 0
        assert "XAI_API_KEY" in result.stdout


class TestGrokSearchUnit:
    """CLI-side validation that should not need the network."""

    def test_missing_key_exits_2(self, isolated_config: Path) -> None:  # noqa: ARG002
        result = runner.invoke(app, ["grok", "web", "anything"])
        assert result.exit_code == 2
        assert "XAI_API_KEY" in result.stderr

    def test_web_mutually_exclusive_domain_flags(
        self,
        isolated_config: Path,  # noqa: ARG002
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("XAI_API_KEY", "xai-anything")
        result = runner.invoke(
            app,
            [
                "grok",
                "web",
                "q",
                "--allowed-domain",
                "a.com",
                "--excluded-domain",
                "b.com",
            ],
        )
        assert result.exit_code == 1
        assert "cannot be combined" in result.stderr

    def test_x_mutually_exclusive_handle_flags(
        self,
        isolated_config: Path,  # noqa: ARG002
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("XAI_API_KEY", "xai-anything")
        result = runner.invoke(
            app,
            ["grok", "x", "q", "--handle", "a", "--exclude-handle", "b"],
        )
        assert result.exit_code == 1
        assert "cannot be combined" in result.stderr

    def test_x_invalid_date_format(
        self,
        isolated_config: Path,  # noqa: ARG002
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("XAI_API_KEY", "xai-anything")
        result = runner.invoke(app, ["grok", "x", "q", "--from", "not-a-date"])
        assert result.exit_code == 1
        assert "YYYY-MM-DD" in result.stderr


class TestDoctor:
    def test_exits_nonzero_when_grok_missing(self, isolated_config: Path) -> None:  # noqa: ARG002
        result = runner.invoke(app, ["doctor"])
        # Codex live tests already passed, so codex is OK; grok is missing
        # because the isolated_config fixture clears XAI_API_KEY.
        assert result.exit_code != 0
        assert "grok" in result.stdout
        assert "codex" in result.stdout

    def test_json_output_is_list(self, isolated_config: Path) -> None:  # noqa: ARG002
        result = runner.invoke(app, ["doctor", "--output", "json"])
        payload = json.loads(result.stdout)
        names = {entry["provider"] for entry in payload}
        assert names == {"grok", "codex"}


class TestCodexCli:
    def test_missing_binary_exits_2(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("PATH", str(tmp_path))
        result = runner.invoke(app, ["codex", "hello"])
        assert result.exit_code == 2
        assert "not found" in result.stderr

    def test_propagates_provider_failure_exit(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        fake = tmp_path / "codex"
        fake.write_text("#!/bin/sh\nexit 7\n")
        fake.chmod(0o755)
        monkeypatch.setenv("PATH", str(tmp_path))
        result = runner.invoke(app, ["codex", "hello"])
        assert result.exit_code == 3


@pytest.mark.live
class TestGrokSearchLive:
    def test_web_text_output(self, live_grok_key: str) -> None:  # noqa: ARG002 - env-resident
        result = runner.invoke(app, ["grok", "web", "capital of France"])
        assert result.exit_code == 0
        assert "Paris" in result.stdout

    def test_web_json_output(self, live_grok_key: str) -> None:  # noqa: ARG002
        result = runner.invoke(app, ["grok", "web", "capital of France", "--output", "json"])
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload["tool_kind"] == "web"
        assert "Paris" in payload["answer"]

    def test_x_text_output(self, live_grok_key: str) -> None:  # noqa: ARG002
        result = runner.invoke(app, ["grok", "x", "xAI news"])
        assert result.exit_code == 0
        assert result.stdout


@pytest.mark.live
class TestCodexCliLive:
    def test_passes_through_skip_flag(self, live_codex: str) -> None:  # noqa: ARG002 - fixture for skip
        # Use a real subprocess via Typer's CliRunner; codex output streams to
        # this process's stdout fileno, which CliRunner captures via a pipe.
        completed = subprocess.run(
            [
                "uv",
                "run",
                "cheap-search",
                "codex",
                "Reply with the single word: pong",
                "--",
                "--skip-git-repo-check",
            ],
            cwd=Path(__file__).resolve().parent.parent,
            capture_output=True,
            text=True,
            timeout=180,
        )
        assert completed.returncode == 0
        combined = (completed.stdout + completed.stderr).lower()
        assert "pong" in combined
