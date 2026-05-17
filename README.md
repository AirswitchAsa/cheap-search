# cheap-search

Cheaper alternatives to Claude's built-in WebSearch, packaged as one CLI plus two Claude Skills.

```
cheap-search
├── grok-search   # xAI / Grok — web + X (Twitter), ~$0.005/call
└── codex-search  # local Codex CLI — billed to your codex subscription
```

## Why

Claude's built-in WebSearch bills against the conversation's token budget. For an agent that searches often, that gets expensive fast. Both providers here offload that cost:

- **Grok** charges ~$0.005 per tool call to xAI directly. It's also the only path to **X/Twitter content** — Claude's WebSearch can't read X.
- **Codex** bills against your codex subscription/credits, not Claude tokens. Slower (~30s+) but pulls a different model's view of the web.

Default posture for both skills is **"prefer this over Claude's WebSearch"**. If you'd rather use cheap-search only when you explicitly name the provider, each skill ships with a one-line edit in its `SKILL.md` to flip to trigger-only mode.

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

- [`grok-search`](skills/grok-search/SKILL.md) — prefers Grok over Claude WebSearch by default; always fires for X/Twitter content. Flip to trigger-only mode by editing one line.
- [`codex-search`](skills/codex-search/SKILL.md) — prefers Codex over Claude WebSearch when latency permits. Flip to trigger-only mode by editing one line.

Each skill bundles `scripts/ensure-cheap-search.sh` which resolves the bundled binary, falls back to `uvx --from cheap-search cheap-search`, and only complains if neither is available.

### Switching to trigger-only mode

If you'd rather keep Claude WebSearch as the default and only invoke cheap-search when you explicitly ask for it, open the skill's `SKILL.md` and replace the `description:` line at the top with the "trigger-only" alternative shown in that file's "Switch to trigger-only mode" section. The `description:` line is what Claude's auto-selector matches against; nothing else needs to change.

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
