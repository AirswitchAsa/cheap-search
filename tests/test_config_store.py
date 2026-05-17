from __future__ import annotations

import os
import stat
from pathlib import Path

from cheap_search.config_store import ConfigStore


def _store(path: Path) -> ConfigStore:
    return ConfigStore(path=path)


class TestConfigStore:
    def test_load_returns_empty_when_missing(self, tmp_path: Path) -> None:
        store = _store(tmp_path / "missing.toml")
        assert store.load() == {}
        assert store.get_grok_api_key() is None

    def test_set_creates_file_with_0600_perms(self, tmp_path: Path) -> None:
        path = tmp_path / "cs" / "config.toml"
        store = _store(path)
        store.set_grok_api_key("xai-secret")

        assert path.read_text().strip().startswith("[grok]")
        assert store.get_grok_api_key() == "xai-secret"

        mode = stat.S_IMODE(path.stat().st_mode)
        assert mode == 0o600
        dir_mode = stat.S_IMODE(path.parent.stat().st_mode)
        assert dir_mode == 0o700

    def test_set_preserves_unrelated_sections(self, tmp_path: Path) -> None:
        path = tmp_path / "config.toml"
        path.write_text('[other]\nfoo = "bar"\n')
        store = _store(path)
        store.set_grok_api_key("xai-secret")

        reloaded = store.load()
        assert reloaded["other"] == {"foo": "bar"}
        assert reloaded["grok"]["api_key"] == "xai-secret"

    def test_unset_idempotent_when_missing(self, tmp_path: Path) -> None:
        store = _store(tmp_path / "missing.toml")
        store.unset_grok_api_key()  # no raise

    def test_unset_removes_only_target_key(self, tmp_path: Path) -> None:
        path = tmp_path / "config.toml"
        path.write_text('[grok]\napi_key = "xai-secret"\nother = "kept"\n')
        store = _store(path)
        store.unset_grok_api_key()

        reloaded = store.load()
        assert reloaded == {"grok": {"other": "kept"}}
        assert path.exists()

    def test_unset_deletes_empty_file(self, tmp_path: Path) -> None:
        path = tmp_path / "config.toml"
        store = _store(path)
        store.set_grok_api_key("xai-secret")
        store.unset_grok_api_key()

        assert not path.exists()

    def test_set_overwrites_existing_value(self, tmp_path: Path) -> None:
        path = tmp_path / "config.toml"
        store = _store(path)
        store.set_grok_api_key("first")
        store.set_grok_api_key("second")
        assert store.get_grok_api_key() == "second"

    def test_set_escapes_special_chars_in_key(self, tmp_path: Path) -> None:
        path = tmp_path / "config.toml"
        store = _store(path)
        store.set_grok_api_key('xai-"quoted"\\back')
        assert store.get_grok_api_key() == 'xai-"quoted"\\back'

    def test_write_is_atomic_no_temp_left_behind(self, tmp_path: Path) -> None:
        path = tmp_path / "config.toml"
        store = _store(path)
        store.set_grok_api_key("xai-secret")
        leftovers = [p for p in path.parent.iterdir() if p.name.endswith(".tmp")]
        assert leftovers == []


class TestDefaultConfigPath:
    def test_respects_xdg_config_home(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        from cheap_search.config_store import default_config_path

        assert default_config_path() == tmp_path / "cheap-search" / "config.toml"

    def test_falls_back_to_home_config(self, monkeypatch, tmp_path: Path) -> None:
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        monkeypatch.setenv("HOME", str(tmp_path))
        from cheap_search.config_store import default_config_path

        expected = Path(os.environ["HOME"]) / ".config" / "cheap-search" / "config.toml"
        assert default_config_path() == expected
