#!/usr/bin/env sh
set -e
# Minimal shim: forward to just using repo justfile
export JUSTFILE="bin/justfile"
if ! command -v just >/dev/null 2>&1; then
  echo "Error: just is required. See README for installation." >&2
  exit 1
fi
exec just "$@"
