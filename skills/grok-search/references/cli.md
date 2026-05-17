# cheap-search grok — CLI reference

Use `cheap-search grok web --help` / `cheap-search grok x --help` for the authoritative list. This file is a quick crib.

Every flag below maps 1:1 to the xAI Agent Tools API. Defaults come straight from the SDK; cheap-search adds no opinionated knobs of its own.

## `cheap-search grok web "<query>"`

| Flag | Notes |
|---|---|
| `--model` | Default `grok-4.3`. Any model id the xAI API accepts. |
| `--reasoning-effort {none,low,medium,high}` | Default medium. `low` saves tokens; `high` for hard questions. |
| `--max-tokens N` | Hard cap on completion tokens. |
| `--temperature F` | 0.0–2.0. |
| `--allowed-domain D` (repeatable) | Whitelist. Max 5. Mutually exclusive with excluded. |
| `--excluded-domain D` (repeatable) | Blacklist. Max 5. Mutually exclusive with allowed. |
| `--enable-image-understanding` | Let Grok interpret images on the pages it visits. |
| `-o, --output {text,json}` | Default text. Use json for agent parsing. |

## `cheap-search grok x "<query>"`

| Flag | Notes |
|---|---|
| `--model`, `--reasoning-effort`, `--max-tokens`, `--temperature`, `-o` | Same as `web`. |
| `--from YYYY-MM-DD` | Inclusive start of the post date window. |
| `--to YYYY-MM-DD` | Inclusive end of the post date window. |
| `--handle H` (repeatable) | Restrict to these X handles. `@` is stripped. |
| `--exclude-handle H` (repeatable) | Exclude these handles. Mutually exclusive with `--handle`. |
| `--enable-image-understanding` | Interpret images in posts. |
| `--enable-video-understanding` | Interpret videos in posts. |

## Output shape (`-o json`)

```json
{
  "answer": "…model's synthesized text…",
  "model": "grok-4.3",
  "tool_kind": "web",
  "citations": [{"url": "https://…", "title": "…"}, …]
}
```

`citations` is always present; an empty list means the tool didn't fire.

## Pricing reminder

Tool calls bill at ~$0.005 each. Grok decides fan-out internally — cheap-search does not cap it. If cost matters, lower `--reasoning-effort`.
