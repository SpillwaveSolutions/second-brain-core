#!/usr/bin/env bash
# PostToolUse hook: fail-closed validate of the touched second-brain bundle.
# Accepts a file path as $1, or reads a Claude / Codex PostToolUse payload
# from stdin (Write/Edit file_path, or apply_patch patch text).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

FILE="${1:-}"
if [[ -z "$FILE" ]]; then
  FILE="$(python3 -c '
import json, re, sys
def extract(data):
    if not isinstance(data, dict):
        return ""
    nests = [data.get("tool_input"), data.get("arguments"), data]
    for nest in nests:
        if not isinstance(nest, dict):
            continue
        for key in ("file_path", "path", "file"):
            v = nest.get(key)
            if isinstance(v, str) and v.strip():
                return v.strip()
        for key in ("input", "patch"):
            v = nest.get(key)
            if not isinstance(v, str):
                continue
            m = re.search(r"\*\*\* (?:Add|Update|Delete) File: (.+)", v)
            if m:
                return m.group(1).strip()
    return ""
try:
    print(extract(json.load(sys.stdin)))
except Exception:
    pass
' 2>/dev/null || true)"
fi

if [[ -z "$FILE" ]]; then
  # No touched path (empty apply_patch / malformed stdin). Validate the
  # claimed root if the session exported one; otherwise this is not our tree.
  if [[ -n "${SECOND_BRAIN_ROOT:-}" && -d "${SECOND_BRAIN_ROOT}" ]]; then
    python3 "$SCRIPT_DIR/sbc_common.py" validate --bundle "$SECOND_BRAIN_ROOT"
    exit $?
  fi
  exit 0
fi

case "$FILE" in
  *.md|*.markdown) ;;
  *) exit 0 ;;
esac

if [[ "$FILE" != /* ]]; then
  FILE="$(pwd)/$FILE"
fi

find_bundle_root() {
  local dir
  dir="$(cd "$(dirname "$FILE")" 2>/dev/null && pwd)" || return 1
  while [[ "$dir" != "/" ]]; do
    if [[ -f "$dir/index.md" ]] && grep -q 'okf_version' "$dir/index.md" 2>/dev/null; then
      echo "$dir"
      return 0
    fi
    dir="$(dirname "$dir")"
  done
  return 1
}

BUNDLE_ROOT="$(find_bundle_root || true)"
if [[ -z "${BUNDLE_ROOT:-}" ]]; then
  exit 0
fi

echo "sbc-validate: validating bundle at $BUNDLE_ROOT (touched: $FILE)"
python3 "$SCRIPT_DIR/sbc_common.py" validate --bundle "$BUNDLE_ROOT"
