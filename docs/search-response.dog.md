# Data: SearchResponse

## Description

The result of a Grok-backed search, returned by `!GrokWebSearch` and `!GrokXSearch`. Wraps the model's synthesized answer with any citations Grok produced while invoking its server-side search tool.

## Fields

- answer: the model's synthesized text response
- citations: list of `&Citation` records, possibly empty
- model: the Grok model used for this invocation (e.g. `grok-4.3`)
- tool_kind: `web` or `x`, identifying which xAI tool produced the answer

## Notes

- `--output text` renders `answer` followed by a `**Citations:**` block; `--output json` serializes the whole record.
- `citations` is never `null` in JSON output; an empty list is used when no citations were returned.
- Codex output does not flow through this type in v0; `!CodexSearch` streams raw codex output instead.
