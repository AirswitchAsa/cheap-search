# cheap-search

Lightweight, agent-facing CLI for provider-specific search. Wraps two backends behind one binary and ships two Claude Skills that teach a coding agent *when* and *how* to call it.

```
cheap-search
├── grok-search   # xAI / Grok — web + X (Twitter)
└── codex-search  # local Codex CLI passthrough
```

The agent picks the provider explicitly. There is no automatic routing.

## Why

Built-in agent search (Claude WebSearch, etc.) is fine for generic lookups. `cheap-search` exists for the cases where you specifically want **Grok's view of the web**, **Grok's read of X/Twitter**, or **Codex's grounding** — and you want the agent to invoke the provider you asked for, not pick one for you.

## Install

### macOS (Apple Silicon) / Linux (x64, arm64)

```bash
curl -fsSL https://raw.githubusercontent.com/AirswitchAsa/cheap-search/main/scripts/install.sh | sh
```

### Anywhere with Python 3.13

```bash
uv tool install cheap-search       # or: pip install cheap-search
```

### Ephemeral (no install)

```bash
uvx --from cheap-search cheap-search --help
```

## Configure

Grok needs an xAI API key. Either:

```bash
export XAI_API_KEY=xai-...
```

or persist it locally with the CLI (stores at `~/.config/cheap-search/config.toml`, mode `0600`):

```bash
cheap-search grok apikey set        # prompts with hidden input
echo "$KEY" | cheap-search grok apikey set -
cheap-search grok apikey status
cheap-search grok apikey unset
```

Env wins when both are set.

Codex handles its own auth — `codex login` once.

## Use

```bash
cheap-search grok web "latest stable Python release"
cheap-search grok x   "xAI announcements" --from 2026-05-01
cheap-search codex    "look up the OpenAI Responses API web search syntax"

cheap-search doctor          # verify local setup
cheap-search providers       # list supported providers
```

Pass `-o json` for agent-parsable output:

```json
{
  "answer": "…",
  "model": "grok-4.3",
  "tool_kind": "web",
  "citations": [{"url": "https://…", "title": "…"}]
}
```

For codex, trailing args after `--` are forwarded:

```bash
cheap-search codex "<query>" -- --skip-git-repo-check -m gpt-5-codex
```

## Skills

Two skills under [`skills/`](skills/):

- [`grok-search`](skills/grok-search/SKILL.md) — fires only when the user explicitly names Grok / xAI / X / Twitter.
- [`codex-search`](skills/codex-search/SKILL.md) — fires only when the user explicitly names Codex.

Each skill bundles `scripts/ensure-cheap-search.sh` which resolves the bundled binary, falls back to `uvx --from cheap-search cheap-search`, and only complains if neither is available.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Usage error |
| 2 | Missing configuration (no API key / no `codex` binary) |
| 3 | Provider failure (network, 4xx/5xx, codex non-zero) |

Agents can branch on these to choose between "tell user to configure" and "surface stderr."

## Specification

The behavioral contract lives as a [DOG](https://github.com/AirswitchAsa/dog) document graph under [`docs/`](docs/). Browse the [project index](docs/index.dog.md) for actors, behaviors, components, and data definitions. The implementation is built to match — lint stays clean: `dog lint docs`.

## Development

```bash
git clone https://github.com/AirswitchAsa/cheap-search
cd cheap-search
uv sync

# Unit tests (no network):
uv run pytest -m "not live"

# Full matrix incl. live xAI + codex calls (costs ~$0.10 in xAI tool fees):
echo 'XAI_API_KEY=xai-...' > .env
uv run pytest
```

CI is build-only (manual `workflow_dispatch`); tests are run locally with a real API key. See [`.github/workflows/release.yml`](.github/workflows/release.yml).

## License

MIT. See [LICENSE](LICENSE).
