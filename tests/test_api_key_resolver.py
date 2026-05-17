from __future__ import annotations

from pathlib import Path

import pytest

from cheap_search.api_key_resolver import ApiKeyResolver, mask_key
from cheap_search.config_store import ConfigStore


@pytest.fixture
def resolver_with_isolated_store(isolated_config: Path) -> ApiKeyResolver:
    return ApiKeyResolver(store=ConfigStore(path=isolated_config))


class TestMaskKey:
    def test_masks_long_key(self) -> None:
        assert mask_key("xai-abcdef1234567890wxyz") == "xai-••••••••wxyz"

    def test_masks_short_key(self) -> None:
        assert mask_key("abc") == "xai-••••••••abc"


class TestResolve:
    def test_returns_none_when_neither_set(self, resolver_with_isolated_store: ApiKeyResolver) -> None:
        assert resolver_with_isolated_store.resolve() is None

    def test_env_wins(
        self,
        isolated_config: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        store = ConfigStore(path=isolated_config)
        store.set_grok_api_key("from-file")
        monkeypatch.setenv("XAI_API_KEY", "from-env")
        resolver = ApiKeyResolver(store=store)
        assert resolver.resolve() == "from-env"

    def test_file_used_when_env_missing(
        self,
        isolated_config: Path,
    ) -> None:
        store = ConfigStore(path=isolated_config)
        store.set_grok_api_key("from-file")
        resolver = ApiKeyResolver(store=store)
        assert resolver.resolve() == "from-file"


class TestStatus:
    def test_missing(self, resolver_with_isolated_store: ApiKeyResolver) -> None:
        status = resolver_with_isolated_store.status()
        assert not status.ok
        assert status.source == "none"
        assert "cheap-search grok apikey set" in status.remediation

    def test_env_only(
        self,
        resolver_with_isolated_store: ApiKeyResolver,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("XAI_API_KEY", "xai-fromenv1234")
        status = resolver_with_isolated_store.status()
        assert status.ok
        assert status.source == "env"
        assert status.shadowed_by is None
        assert status.masked_value is not None and status.masked_value.endswith("1234")

    def test_file_only(self, isolated_config: Path) -> None:
        store = ConfigStore(path=isolated_config)
        store.set_grok_api_key("xai-fromfile1234")
        status = ApiKeyResolver(store=store).status()
        assert status.ok
        assert status.source == "config"
        assert status.shadowed_by is None

    def test_env_shadows_file(
        self,
        isolated_config: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        store = ConfigStore(path=isolated_config)
        store.set_grok_api_key("from-file")
        monkeypatch.setenv("XAI_API_KEY", "xai-fromenv1234")
        status = ApiKeyResolver(store=store).status()
        assert status.ok
        assert status.source == "env"
        assert status.shadowed_by == "config"
