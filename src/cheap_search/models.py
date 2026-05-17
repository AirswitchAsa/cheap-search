from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal


ToolKind = Literal["web", "x"]
KeySource = Literal["env", "config", "path", "none"]


@dataclass(frozen=True, slots=True)
class Citation:
    url: str
    title: str | None = None


@dataclass(frozen=True, slots=True)
class SearchResponse:
    answer: str
    model: str
    tool_kind: ToolKind
    citations: list[Citation] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_text(self) -> str:
        if not self.citations:
            return self.answer
        lines = [self.answer, "", "**Citations:**"]
        for c in self.citations:
            label = c.title or c.url
            lines.append(f"- [{label}]({c.url})")
        return "\n".join(lines)


@dataclass(frozen=True, slots=True)
class ProviderStatus:
    provider: str
    ok: bool
    source: KeySource
    remediation: str
    shadowed_by: KeySource | None = None
    masked_value: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)
