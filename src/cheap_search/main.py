from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime
from enum import Enum
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version
from typing import Annotated

import typer

from cheap_search import __version__ as _fallback_version
from cheap_search.api_key_resolver import ApiKeyResolver
from cheap_search.codex_invoker import CodexInvoker, CodexMissingError
from cheap_search.config_store import ConfigStore
from cheap_search.grok_client import DEFAULT_MODEL, GrokClient, GrokError
from cheap_search.models import ProviderStatus, SearchResponse


EXIT_OK = 0
EXIT_USAGE = 1
EXIT_MISSING_CONFIG = 2
EXIT_PROVIDER_FAILURE = 3


class OutputFormat(str, Enum):
    text = "text"
    json = "json"


class ReasoningEffort(str, Enum):
    none = "none"
    low = "low"
    medium = "medium"
    high = "high"


app = typer.Typer(
    name="cheap-search",
    help="Lightweight provider-specific search CLI (Grok web/X, local Codex).",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
grok_app = typer.Typer(name="grok", help="xAI / Grok search.", no_args_is_help=True)
grok_apikey_app = typer.Typer(name="apikey", help="Manage the local xAI API key.", no_args_is_help=True)
app.add_typer(grok_app)
grok_app.add_typer(grok_apikey_app)


def _resolve_version() -> str:
    try:
        return _pkg_version("cheap-search")
    except PackageNotFoundError:
        return _fallback_version


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"cheap-search {_resolve_version()}")
        raise typer.Exit()


@app.callback()
def _root(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help="Show the version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """cheap-search: provider-specific search CLI."""


def _emit_response(response: SearchResponse, output: OutputFormat) -> None:
    if output == OutputFormat.json:
        typer.echo(json.dumps(response.to_dict()))
    else:
        typer.echo(response.to_text())


def _emit_status(status: ProviderStatus, output: OutputFormat) -> None:
    if output == OutputFormat.json:
        typer.echo(json.dumps(status.to_dict()))
        return
    if not status.ok:
        typer.secho(f"{status.provider}: not configured", fg=typer.colors.RED)
        if status.remediation:
            typer.echo(f"  {status.remediation}")
        return
    masked = status.masked_value or ""
    if status.shadowed_by:
        typer.secho(
            f"{status.provider}: set via {status.source} ({masked}, active)",
            fg=typer.colors.GREEN,
        )
        typer.echo(f"  also stored in {status.shadowed_by} (shadowed by {status.source})")
    else:
        typer.secho(f"{status.provider}: set via {status.source} ({masked})", fg=typer.colors.GREEN)


def _run_grok(coro) -> SearchResponse:  # noqa: ANN001 - awaitable
    try:
        return asyncio.run(coro)
    except GrokError as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=EXIT_PROVIDER_FAILURE) from e


def _require_grok_key() -> str:
    key = ApiKeyResolver().resolve()
    if not key:
        typer.secho(
            f"xAI API key not configured. Set XAI_API_KEY in your shell, "
            f"or run `cheap-search grok apikey set`.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=EXIT_MISSING_CONFIG)
    return key


def _parse_date(value: str | None, *, flag: str) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError as e:
        typer.secho(f"{flag} must be in YYYY-MM-DD format: {value}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=EXIT_USAGE) from e


def _strip_at(handle: str) -> str:
    return handle.lstrip("@")


@grok_app.command("web")
def grok_web(
    query: Annotated[str, typer.Argument(help="Search query")],
    model: Annotated[str, typer.Option("--model", help="Grok model id")] = DEFAULT_MODEL,
    reasoning_effort: Annotated[
        ReasoningEffort | None,
        typer.Option("--reasoning-effort", help="Reasoning effort level"),
    ] = None,
    max_tokens: Annotated[int | None, typer.Option("--max-tokens", help="Max completion tokens")] = None,
    temperature: Annotated[float | None, typer.Option("--temperature", help="Sampling temperature")] = None,
    allowed_domain: Annotated[
        list[str] | None,
        typer.Option("--allowed-domain", help="Restrict to domain (repeatable, max 5)"),
    ] = None,
    excluded_domain: Annotated[
        list[str] | None,
        typer.Option("--excluded-domain", help="Exclude domain (repeatable, max 5)"),
    ] = None,
    enable_image_understanding: Annotated[
        bool,
        typer.Option("--enable-image-understanding", help="Allow Grok to interpret images in results"),
    ] = False,
    output: Annotated[OutputFormat, typer.Option("--output", "-o", help="Output format")] = OutputFormat.text,
) -> None:
    """Grok web search via xAI Agent Tools API."""
    if allowed_domain and excluded_domain:
        typer.secho("--allowed-domain and --excluded-domain cannot be combined", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=EXIT_USAGE)
    key = _require_grok_key()
    client = GrokClient(key)
    response = _run_grok(
        client.web_search(
            query,
            model=model,
            reasoning_effort=reasoning_effort.value if reasoning_effort else None,
            max_tokens=max_tokens,
            temperature=temperature,
            allowed_domains=allowed_domain or None,
            excluded_domains=excluded_domain or None,
            enable_image_understanding=enable_image_understanding,
        )
    )
    _emit_response(response, output)


@grok_app.command("x")
def grok_x(  # noqa: C901
    query: Annotated[str, typer.Argument(help="Search query")],
    model: Annotated[str, typer.Option("--model", help="Grok model id")] = DEFAULT_MODEL,
    reasoning_effort: Annotated[
        ReasoningEffort | None,
        typer.Option("--reasoning-effort", help="Reasoning effort level"),
    ] = None,
    max_tokens: Annotated[int | None, typer.Option("--max-tokens", help="Max completion tokens")] = None,
    temperature: Annotated[float | None, typer.Option("--temperature", help="Sampling temperature")] = None,
    from_date: Annotated[str | None, typer.Option("--from", help="Inclusive start date YYYY-MM-DD")] = None,
    to_date: Annotated[str | None, typer.Option("--to", help="Inclusive end date YYYY-MM-DD")] = None,
    handle: Annotated[
        list[str] | None,
        typer.Option("--handle", help="Restrict to X handle (repeatable)"),
    ] = None,
    exclude_handle: Annotated[
        list[str] | None,
        typer.Option("--exclude-handle", help="Exclude X handle (repeatable)"),
    ] = None,
    enable_image_understanding: Annotated[
        bool,
        typer.Option("--enable-image-understanding", help="Interpret images attached to posts"),
    ] = False,
    enable_video_understanding: Annotated[
        bool,
        typer.Option("--enable-video-understanding", help="Interpret videos attached to posts"),
    ] = False,
    output: Annotated[OutputFormat, typer.Option("--output", "-o", help="Output format")] = OutputFormat.text,
) -> None:
    """Grok X (Twitter) search via xAI Agent Tools API."""
    if handle and exclude_handle:
        typer.secho("--handle and --exclude-handle cannot be combined", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=EXIT_USAGE)
    key = _require_grok_key()
    client = GrokClient(key)
    allowed = [_strip_at(h) for h in handle] if handle else None
    excluded = [_strip_at(h) for h in exclude_handle] if exclude_handle else None
    response = _run_grok(
        client.x_search(
            query,
            model=model,
            reasoning_effort=reasoning_effort.value if reasoning_effort else None,
            max_tokens=max_tokens,
            temperature=temperature,
            from_date=_parse_date(from_date, flag="--from"),
            to_date=_parse_date(to_date, flag="--to"),
            allowed_x_handles=allowed,
            excluded_x_handles=excluded,
            enable_image_understanding=enable_image_understanding,
            enable_video_understanding=enable_video_understanding,
        )
    )
    _emit_response(response, output)


@grok_apikey_app.command("set")
def grok_apikey_set(
    source: Annotated[
        str | None,
        typer.Argument(help="`-` to read from stdin; omit to be prompted with hidden input"),
    ] = None,
) -> None:
    """Persist the xAI API key locally (chmod 0600)."""
    if source is None:
        key = typer.prompt("xAI API key", hide_input=True, confirmation_prompt=False).strip()
    elif source == "-":
        key = sys.stdin.readline().strip()
    else:
        typer.secho(
            "Refusing to accept the key as a positional argument (leaks via shell history). "
            "Run without arguments to be prompted, or pipe it: `... apikey set -`.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=EXIT_USAGE)
    if not key:
        typer.secho("xAI API key is empty", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=EXIT_USAGE)
    store = ConfigStore()
    try:
        store.set_grok_api_key(key)
    except OSError as e:
        typer.secho(f"Could not write config: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=EXIT_PROVIDER_FAILURE) from e
    typer.secho(f"xAI API key saved to {store.path}", fg=typer.colors.GREEN)


@grok_apikey_app.command("unset")
def grok_apikey_unset() -> None:
    """Remove the locally persisted xAI API key (idempotent)."""
    store = ConfigStore()
    try:
        store.unset_grok_api_key()
    except OSError as e:
        typer.secho(f"Could not update config: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=EXIT_PROVIDER_FAILURE) from e
    typer.secho("xAI API key removed", fg=typer.colors.GREEN)
    if os.environ.get("XAI_API_KEY"):
        typer.echo("Note: XAI_API_KEY is still set in your environment.")


@grok_apikey_app.command("status")
def grok_apikey_status(
    output: Annotated[OutputFormat, typer.Option("--output", "-o", help="Output format")] = OutputFormat.text,
) -> None:
    """Show whether an xAI API key is configured and where it comes from."""
    status = ApiKeyResolver().status()
    _emit_status(status, output)


@app.command(
    "codex",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def codex_cmd(
    ctx: typer.Context,
    query: Annotated[str, typer.Argument(help="Query to forward to the local `codex` CLI")],
) -> None:
    """Forward a query to the local `codex` CLI. Trailing args after `--` are passed through."""
    invoker = CodexInvoker()
    forwarded = list(ctx.args)
    try:
        exit_code = asyncio.run(invoker.run(query, forwarded=forwarded))
    except CodexMissingError as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=EXIT_MISSING_CONFIG) from e
    if exit_code != 0:
        raise typer.Exit(code=EXIT_PROVIDER_FAILURE)


@app.command("doctor")
def doctor(
    output: Annotated[OutputFormat, typer.Option("--output", "-o", help="Output format")] = OutputFormat.text,
) -> None:
    """Report local configuration status for every provider."""
    statuses = [ApiKeyResolver().status(), CodexInvoker().status()]
    if output == OutputFormat.json:
        typer.echo(json.dumps([s.to_dict() for s in statuses]))
    else:
        for s in statuses:
            _emit_status(s, OutputFormat.text)
    raise typer.Exit(code=EXIT_OK if all(s.ok for s in statuses) else EXIT_USAGE)


_PROVIDERS = [
    {"name": "grok", "command": "cheap-search grok", "description": "xAI / Grok web and X search."},
    {"name": "codex", "command": "cheap-search codex", "description": "Local Codex CLI passthrough."},
]


@app.command("providers")
def providers(
    output: Annotated[OutputFormat, typer.Option("--output", "-o", help="Output format")] = OutputFormat.text,
) -> None:
    """List supported providers in this build."""
    if output == OutputFormat.json:
        typer.echo(json.dumps({"providers": _PROVIDERS}))
        return
    for p in _PROVIDERS:
        typer.echo(f"{p['name']:<8} {p['command']:<24} {p['description']}")


if __name__ == "__main__":
    app()
