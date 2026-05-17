# Component: GrokClient

## Description

Thin wrapper around the `xai_sdk.AsyncClient` that builds agentic chats with either the `web_search` or `x_search` server-side tool and returns a `&SearchResponse`. Constructs a fresh client per invocation using a key supplied by `#ApiKeyResolver`; the CLI is single-shot, so no client reuse is necessary.

## State

- api_key: the resolved xAI API key (held only for the lifetime of one invocation)
- model: the Grok model identifier (default `grok-4.3`)
- tool_kind: `web` or `x` for the active invocation
- tool_options: provider-specific filters (allowed/excluded domains, date window, X handles, image/video understanding)

## Events

- chat_created
- chat_sampled
- chat_failed

## Notes

- Uses the Agent Tools API only; the deprecated `SearchParameters(sources=[...])` shape returns 410 since 2026-01-12.
- Citations attached to the model response are converted into `&Citation` records on the returned `&SearchResponse`.
- Network or gRPC errors surface as a single exception that the `#CLI` translates into exit code 3.
- The xAI SDK does not expose a per-call timeout on `chat.create`; if a timeout is later required, it must be added at client construction.
