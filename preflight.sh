#!/usr/bin/env bash
# Stable root entrypoint for the complete local certification gate.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$repo_root/scripts/preflight.sh" "$@"
