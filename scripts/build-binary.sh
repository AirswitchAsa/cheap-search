#!/usr/bin/env bash
set -euo pipefail

MODE="${CHEAP_SEARCH_NUITKA_MODE:-standalone}"
OUT_DIR="${CHEAP_SEARCH_BINARY_OUT_DIR:-dist-bin}"
NAME="${CHEAP_SEARCH_BINARY_NAME:-cheap-search}"

case "$MODE" in
  standalone | onefile) ;;
  *)
    echo "CHEAP_SEARCH_NUITKA_MODE must be 'standalone' or 'onefile'" >&2
    exit 2
    ;;
esac

uv run python -m nuitka \
  --mode="$MODE" \
  --assume-yes-for-downloads \
  --remove-output \
  --output-dir="$OUT_DIR" \
  --output-filename="$NAME" \
  --include-package=cheap_search \
  --include-package=xai_sdk \
  --include-package=grpc \
  --python-flag=-m \
  --main=src/cheap_search
