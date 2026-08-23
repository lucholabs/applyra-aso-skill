#!/usr/bin/env bash
set -u

PASS=0
WARN=0
FAIL=0
NETWORK=0

if [[ "${1:-}" == "--network" ]]; then
  NETWORK=1
elif [[ $# -gt 0 ]]; then
  printf 'Usage: %s [--network]\n' "$0" >&2
  exit 64
fi

pass() { printf 'PASS  %s\n' "$1"; PASS=$((PASS+1)); }
warn() { printf 'WARN  %s\n' "$1"; WARN=$((WARN+1)); }
fail() { printf 'FAIL  %s\n' "$1"; FAIL=$((FAIL+1)); }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
EXPECTED_MCP_VERSION="1.4.2"
MCP_LIST_TIMEOUT_SECONDS=10

run_with_timeout() {
  python3 - "$MCP_LIST_TIMEOUT_SECONDS" "$@" <<'PY'
import subprocess
import sys

try:
    result = subprocess.run(
        sys.argv[2:],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        timeout=float(sys.argv[1]),
        check=False,
    )
except subprocess.TimeoutExpired:
    sys.exit(124)
sys.stdout.buffer.write(result.stdout)
sys.exit(result.returncode)
PY
}

if command -v python3 >/dev/null 2>&1; then
  pass "python3 is available: $(python3 --version 2>&1)"
else
  fail "python3 is required for metadata validation."
fi

if command -v node >/dev/null 2>&1; then
  NODE_VERSION="$(node --version 2>/dev/null || true)"
  NODE_MAJOR="$(printf '%s' "$NODE_VERSION" | sed -E 's/^v([0-9]+).*/\1/')"
  if [[ "$NODE_MAJOR" =~ ^[0-9]+$ ]] && (( NODE_MAJOR >= 20 )); then
    pass "Node.js is compatible with Applyra MCP: $NODE_VERSION"
  else
    fail "Applyra MCP requires Node.js 20 or later; found $NODE_VERSION"
  fi
else
  fail "node is not installed."
fi

if command -v npx >/dev/null 2>&1; then
  pass "npx is available."
else
  fail "npx is required to start @applyra/mcp-server."
fi

CLIENTS=0
if command -v codex >/dev/null 2>&1; then
  CLIENTS=$((CLIENTS+1))
  pass "Codex CLI is available."
  MCP_LIST="$(run_with_timeout codex mcp list || true)"
  if printf '%s' "$MCP_LIST" | grep -qi 'applyra'; then
    pass "Applyra MCP appears in Codex configuration."
  else
    warn "Applyra MCP was not found in 'codex mcp list'; a plugin install may still provide it at runtime."
  fi
fi

if command -v claude >/dev/null 2>&1; then
  CLIENTS=$((CLIENTS+1))
  pass "Claude Code is available."
  MCP_LIST="$(run_with_timeout claude mcp list || true)"
  if printf '%s' "$MCP_LIST" | grep -qi 'applyra'; then
    pass "Applyra MCP appears in Claude Code configuration."
  else
    warn "Applyra MCP was not found in 'claude mcp list'; a plugin install may still provide it at runtime."
  fi
fi

if (( CLIENTS == 0 )); then
  warn "Neither Codex CLI nor Claude Code is available in this shell; skill files and validation remain usable."
fi

if [[ -n "${APPLYRA_API_KEY:-}" ]]; then
  pass "APPLYRA_API_KEY exists in the environment (value not printed)."
else
  warn "APPLYRA_API_KEY is not present in this shell. Export it before using live Applyra tools."
fi

if [[ -f "$SKILL_DIR/SKILL.md" ]]; then
  pass "SKILL.md exists."
else
  fail "SKILL.md is missing from $SKILL_DIR"
fi

if [[ -f "$SKILL_DIR/agents/openai.yaml" ]]; then
  pass "agents/openai.yaml exists."
else
  warn "agents/openai.yaml is missing; Codex UI metadata will be reduced."
fi

if command -v python3 >/dev/null 2>&1; then
  if python3 "$SCRIPT_DIR/validate_metadata.py" --self-test >/dev/null 2>&1; then
    pass "Metadata validator self-test passed."
  else
    fail "Metadata validator self-test failed."
  fi
fi

if (( NETWORK == 1 )); then
  if command -v npm >/dev/null 2>&1; then
    LATEST="$(npm view @applyra/mcp-server version 2>/dev/null || true)"
    if [[ -z "$LATEST" ]]; then
      warn "Could not query the npm registry for @applyra/mcp-server."
    elif [[ "$LATEST" == "$EXPECTED_MCP_VERSION" ]]; then
      pass "Pinned Applyra MCP version is current: $LATEST"
    else
      warn "Pinned Applyra MCP is $EXPECTED_MCP_VERSION; npm reports $LATEST. Review upstream before updating."
    fi
  else
    warn "npm is unavailable; skipped upstream version check."
  fi
fi

printf '\nSummary: %d pass, %d warning, %d fail\n' "$PASS" "$WARN" "$FAIL"

if (( FAIL > 0 )); then
  exit 1
fi
exit 0
