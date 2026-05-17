from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any


_FILE_MODE = 0o600
_DIR_MODE = 0o700


def default_config_path() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "cheap-search" / "config.toml"


class ConfigStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path: Path = path or default_config_path()

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        with self.path.open("rb") as f:
            return tomllib.load(f)

    def get_grok_api_key(self) -> str | None:
        data = self.load()
        grok = data.get("grok")
        if not isinstance(grok, dict):
            return None
        key = grok.get("api_key")
        return key if isinstance(key, str) and key else None

    def set_grok_api_key(self, key: str) -> None:
        data = self.load()
        grok = data.setdefault("grok", {})
        if not isinstance(grok, dict):
            grok = {}
            data["grok"] = grok
        grok["api_key"] = key
        self._write(data)

    def unset_grok_api_key(self) -> None:
        if not self.path.exists():
            return
        data = self.load()
        grok = data.get("grok")
        if isinstance(grok, dict) and "api_key" in grok:
            del grok["api_key"]
            if not grok:
                del data["grok"]
        if not data:
            self.path.unlink()
            return
        self._write(data)

    def _write(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=_DIR_MODE)
        os.chmod(self.path.parent, _DIR_MODE)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        rendered = _render_toml(data)
        # O_EXCL would race; just open and chmod before rename.
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, _FILE_MODE)
        try:
            with os.fdopen(fd, "w") as f:
                f.write(rendered)
        except Exception:
            tmp.unlink(missing_ok=True)
            raise
        os.chmod(tmp, _FILE_MODE)
        os.replace(tmp, self.path)


def _render_toml(data: dict[str, Any]) -> str:
    lines: list[str] = []
    for section, body in data.items():
        if not isinstance(body, dict):
            raise ValueError(f"Top-level value for {section!r} must be a table")
        lines.append(f"[{section}]")
        for key, value in body.items():
            lines.append(f"{key} = {_render_value(value)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_value(value: Any) -> str:  # noqa: ANN401
    if isinstance(value, str):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return str(value)
    raise ValueError(f"Unsupported TOML value type: {type(value).__name__}")
