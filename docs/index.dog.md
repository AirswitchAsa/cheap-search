# Project: cheap-search

## Description

`cheap-search` is a lightweight, agent-facing CLI for provider-specific search. v0 ships one Python binary built with Nuitka plus two Claude Skills (`grok-search`, `codex-search`) that are thin wrappers teaching the agent when and how to call the CLI. There is no automatic provider routing; the `@User` or `@Agent` always names the provider explicitly.

## Actors

- [Agent](agent.dog.md)
- [User](user.dog.md)

## Behaviors

- [CodexSearch](codex-search.dog.md)
- [Doctor](doctor.dog.md)
- [GrokWebSearch](grok-web-search.dog.md)
- [GrokXSearch](grok-x-search.dog.md)
- [ListProviders](list-providers.dog.md)
- [SetGrokApiKey](set-grok-api-key.dog.md)
- [ShowGrokApiKeyStatus](show-grok-api-key-status.dog.md)
- [UnsetGrokApiKey](unset-grok-api-key.dog.md)

## Components

- [ApiKeyResolver](api-key-resolver.dog.md)
- [CLI](cli.dog.md)
- [CodexInvoker](codex-invoker.dog.md)
- [ConfigStore](config-store.dog.md)
- [GrokClient](grok-client.dog.md)

## Data

- [Citation](citation.dog.md)
- [Config](config.dog.md)
- [ProviderStatus](provider-status.dog.md)
- [SearchResponse](search-response.dog.md)

## Notes

- v0 providers: Grok (xAI web + X) and local Codex CLI.
- v0 explicitly excludes: browser automation, Firecrawl, Exa, Gemini, Perplexity, automatic router skill, unified result schema, multi-provider merging.
- Python 3.13 + uv + hatchling + Typer; binary built with Nuitka standalone mode.
- Credential storage uses TOML at `~/.config/cheap-search/config.toml` (mode `0600`); env vars always win.
