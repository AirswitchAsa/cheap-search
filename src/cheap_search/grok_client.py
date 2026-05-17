from __future__ import annotations

from datetime import datetime
from typing import Any

from xai_sdk import AsyncClient
from xai_sdk.chat import user
from xai_sdk.tools import web_search as _web_search_tool
from xai_sdk.tools import x_search as _x_search_tool

from cheap_search.models import Citation, SearchResponse


DEFAULT_MODEL = "grok-4.3"


class GrokError(RuntimeError):
    pass


class GrokClient:
    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise GrokError("xAI API key is empty")
        # AsyncClient is created lazily inside an event loop so the underlying
        # grpc.aio channel binds to the loop that will actually `await` it.
        # Constructing it eagerly here would bind to whatever loop exists at
        # __init__ time (or none), which fails with "attached to a different
        # loop" when the CLI later wraps the call in asyncio.run().
        self._api_key = api_key

    async def web_search(
        self,
        query: str,
        *,
        model: str = DEFAULT_MODEL,
        reasoning_effort: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        allowed_domains: list[str] | None = None,
        excluded_domains: list[str] | None = None,
        enable_image_understanding: bool = False,
    ) -> SearchResponse:
        if allowed_domains and excluded_domains:
            raise GrokError("--allowed-domain and --excluded-domain cannot be combined")
        tool = _web_search_tool(
            allowed_domains=allowed_domains,
            excluded_domains=excluded_domains,
            enable_image_understanding=enable_image_understanding,
        )
        return await self._sample(
            query,
            tool=tool,
            tool_kind="web",
            model=model,
            reasoning_effort=reasoning_effort,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    async def x_search(
        self,
        query: str,
        *,
        model: str = DEFAULT_MODEL,
        reasoning_effort: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        allowed_x_handles: list[str] | None = None,
        excluded_x_handles: list[str] | None = None,
        enable_image_understanding: bool = False,
        enable_video_understanding: bool = False,
    ) -> SearchResponse:
        if allowed_x_handles and excluded_x_handles:
            raise GrokError("--handle and --exclude-handle cannot be combined")
        tool = _x_search_tool(
            from_date=from_date,
            to_date=to_date,
            allowed_x_handles=allowed_x_handles,
            excluded_x_handles=excluded_x_handles,
            enable_image_understanding=enable_image_understanding,
            enable_video_understanding=enable_video_understanding,
        )
        return await self._sample(
            query,
            tool=tool,
            tool_kind="x",
            model=model,
            reasoning_effort=reasoning_effort,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    async def _sample(
        self,
        query: str,
        *,
        tool: Any,  # noqa: ANN401 - xai_sdk proto type
        tool_kind: str,
        model: str,
        reasoning_effort: str | None,
        max_tokens: int | None,
        temperature: float | None,
    ) -> SearchResponse:
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": [user(query)],
            "tools": [tool],
        }
        if reasoning_effort is not None:
            kwargs["reasoning_effort"] = reasoning_effort
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        if temperature is not None:
            kwargs["temperature"] = temperature
        try:
            client = AsyncClient(api_key=self._api_key)
            chat = client.chat.create(**kwargs)
            response = await chat.sample()
        except Exception as e:
            raise GrokError(f"xAI request failed: {e}") from e
        return SearchResponse(
            answer=response.content or "",
            model=model,
            tool_kind=tool_kind,  # type: ignore[arg-type]
            citations=_extract_citations(response),
        )


def _extract_citations(response: Any) -> list[Citation]:  # noqa: ANN401 - SDK type
    raw = getattr(response, "citations", None) or []
    out: list[Citation] = []
    for c in raw:
        if isinstance(c, str):
            out.append(Citation(url=c))
            continue
        url = getattr(c, "url", None)
        if not url:
            continue
        title = getattr(c, "title", None)
        out.append(Citation(url=url, title=title if isinstance(title, str) and title else None))
    return out
