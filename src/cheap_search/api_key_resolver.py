from __future__ import annotations

import os

from cheap_search.config_store import ConfigStore
from cheap_search.models import ProviderStatus


ENV_VAR = "XAI_API_KEY"


def mask_key(key: str) -> str:
    tail = key[-4:] if len(key) >= 4 else key
    return f"xai-{'•' * 8}{tail}"


class ApiKeyResolver:
    def __init__(self, store: ConfigStore | None = None) -> None:
        self.store = store or ConfigStore()

    def resolve(self) -> str | None:
        env_value = os.environ.get(ENV_VAR)
        if env_value:
            return env_value
        return self.store.get_grok_api_key()

    def status(self) -> ProviderStatus:
        env_value = os.environ.get(ENV_VAR)
        file_value = self.store.get_grok_api_key()
        if env_value:
            shadowed = "config" if file_value else None
            return ProviderStatus(
                provider="grok",
                ok=True,
                source="env",
                shadowed_by=shadowed,
                masked_value=mask_key(env_value),
                remediation="",
            )
        if file_value:
            return ProviderStatus(
                provider="grok",
                ok=True,
                source="config",
                masked_value=mask_key(file_value),
                remediation="",
            )
        return ProviderStatus(
            provider="grok",
            ok=False,
            source="none",
            remediation=(
                f"Set {ENV_VAR} in your shell, or run `cheap-search grok apikey set` "
                "to persist a key locally."
            ),
        )
