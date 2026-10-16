#!/usr/bin/env bash
# Crawl Nexus Zero Height (after SSO) and snapshot pages into baxter-ux.
set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PLUGIN_ROOT"
exec python3 "$PLUGIN_ROOT/scripts/zeroheight_dls.py" --plugin-root "$PLUGIN_ROOT" "$@"
