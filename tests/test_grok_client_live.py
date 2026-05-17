"""Live tests against the real xAI API.

These hit the network and cost ~$0.005 per tool call. Skip themselves
when XAI_API_KEY is missing.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from cheap_search.grok_client import GrokClient, GrokError


pytestmark = pytest.mark.live


class TestGrokWebSearchLive:
    async def test_basic_query_returns_answer(self, live_grok_key: str) -> None:
        client = GrokClient(live_grok_key)
        result = await client.web_search("What is the capital of France?")
        assert result.tool_kind == "web"
        assert result.model == "grok-4.3"
        assert "Paris" in result.answer

    async def test_query_returns_citations(self, live_grok_key: str) -> None:
        client = GrokClient(live_grok_key)
        result = await client.web_search("Latest stable Python release version")
        assert len(result.citations) >= 1
        assert all(c.url.startswith("http") for c in result.citations)

    async def test_reasoning_effort_low(self, live_grok_key: str) -> None:
        client = GrokClient(live_grok_key)
        result = await client.web_search(
            "When was the xAI Agent Tools API introduced?",
            reasoning_effort="low",
        )
        assert result.answer

    async def test_max_tokens_bounds_response(self, live_grok_key: str) -> None:
        client = GrokClient(live_grok_key)
        result = await client.web_search(
            "Describe the Eiffel Tower in detail.",
            max_tokens=64,
        )
        assert result.answer
        # max_tokens is a hard cap on completion tokens; the answer is short.
        assert len(result.answer) < 4000

    async def test_temperature_accepted(self, live_grok_key: str) -> None:
        client = GrokClient(live_grok_key)
        result = await client.web_search(
            "Name one programming language.",
            temperature=0.0,
        )
        assert result.answer

    async def test_allowed_domain_filter(self, live_grok_key: str) -> None:
        client = GrokClient(live_grok_key)
        result = await client.web_search(
            "What is on the Wikipedia page for Python language?",
            allowed_domains=["wikipedia.org"],
        )
        assert result.answer
        if result.citations:
            assert any("wikipedia.org" in c.url for c in result.citations)

    async def test_excluded_domain_filter(self, live_grok_key: str) -> None:
        client = GrokClient(live_grok_key)
        result = await client.web_search(
            "Python tutorial introduction",
            excluded_domains=["wikipedia.org"],
        )
        assert result.answer
        if result.citations:
            assert all("wikipedia.org" not in c.url for c in result.citations)

    async def test_mutually_exclusive_domain_filters(self, live_grok_key: str) -> None:
        client = GrokClient(live_grok_key)
        with pytest.raises(GrokError, match="cannot be combined"):
            await client.web_search(
                "test",
                allowed_domains=["a.com"],
                excluded_domains=["b.com"],
            )


class TestGrokXSearchLive:
    async def test_basic_query(self, live_grok_key: str) -> None:
        client = GrokClient(live_grok_key)
        result = await client.x_search("xAI announcements")
        assert result.tool_kind == "x"
        assert result.answer

    async def test_date_window(self, live_grok_key: str) -> None:
        client = GrokClient(live_grok_key)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=14)
        result = await client.x_search(
            "recent activity",
            from_date=from_date,
            to_date=to_date,
        )
        assert result.answer

    async def test_allowed_handle_filter(self, live_grok_key: str) -> None:
        client = GrokClient(live_grok_key)
        result = await client.x_search(
            "posts from this account",
            allowed_x_handles=["xai"],
        )
        assert result.answer

    async def test_excluded_handle_filter(self, live_grok_key: str) -> None:
        client = GrokClient(live_grok_key)
        result = await client.x_search(
            "AI news this week",
            excluded_x_handles=["elonmusk"],
        )
        assert result.answer

    async def test_mutually_exclusive_handle_filters(self, live_grok_key: str) -> None:
        client = GrokClient(live_grok_key)
        with pytest.raises(GrokError, match="cannot be combined"):
            await client.x_search(
                "test",
                allowed_x_handles=["a"],
                excluded_x_handles=["b"],
            )


class TestGrokClientErrors:
    async def test_empty_key_raises(self) -> None:
        with pytest.raises(GrokError, match="empty"):
            GrokClient("")

    async def test_invalid_key_returns_provider_failure(self) -> None:
        client = GrokClient("xai-definitely-not-valid-key-zzz")
        with pytest.raises(GrokError, match="xAI request failed"):
            await client.web_search("ping")
