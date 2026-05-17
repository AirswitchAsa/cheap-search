# Data: Citation

## Description

A single citation produced by Grok's `web_search` or `x_search` tool while answering a query. Carried inside a `&SearchResponse`.

## Fields

- url: the cited URL
- title: optional human-readable title, may be `null`

## Notes

- The xAI SDK returns either a bare string URL or an object with `url`/`title`; both shapes are normalized to this record.
- A `&Citation` with `title` missing is rendered as `- <url>` in text output.
