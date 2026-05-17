#!/usr/bin/env sh
set -eu

if command -v cheap-search >/dev/null 2>&1 && cheap-search --help >/dev/null 2>&1; then
  if [ "$#" -eq 0 ]; then
    printf '%s\n' "cheap-search"
    exit 0
  fi
  exec cheap-search "$@"
fi

if command -v uvx >/dev/null 2>&1; then
  if uvx --from cheap-search cheap-search --help >/dev/null 2>&1; then
    if [ "$#" -eq 0 ]; then
      printf '%s\n' "uvx --from cheap-search cheap-search"
      exit 0
    fi
    exec uvx --from cheap-search cheap-search "$@"
  fi
fi

cat >&2 <<'EOF'
cheap-search CLI is not available.

Install it with one of:
  curl -fsSL https://raw.githubusercontent.com/AirswitchAsa/cheap-search/main/scripts/install.sh | sh
  uv tool install cheap-search
  pip install cheap-search

Or run ephemerally when uvx is available:
  uvx --from cheap-search cheap-search <command>
EOF
exit 1
