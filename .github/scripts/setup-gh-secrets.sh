#!/usr/bin/env bash
set -euo pipefail

# Sets GitHub Actions secrets and variables for the skill-review workflow
# by reading values from local environment variables.
#
# Usage:
#   export OPENAI_API_KEY="sk-..."
#   export ANTHROPIC_API_KEY="sk-ant-..."
#   export LLM_PROVIDER="openai"         # optional, defaults to "openai"
#   bash .github/scripts/setup-gh-secrets.sh
#
# Prerequisites: gh CLI authenticated with repo admin access.

REPO="${GH_REPO:-kayaman/skills}"
PROVIDER="${LLM_PROVIDER:-openai}"

echo "==> Target repository: $REPO"
echo "==> LLM provider:      $PROVIDER"
echo ""

errors=0

# --- Secrets ---

if [ -n "${OPENAI_API_KEY:-}" ]; then
  echo "[secret] Setting OPENAI_API_KEY..."
  echo "$OPENAI_API_KEY" | gh secret set OPENAI_API_KEY --repo "$REPO"
  echo "         Done."
else
  echo "[secret] OPENAI_API_KEY not set in environment — skipping."
  if [ "$PROVIDER" = "openai" ]; then
    echo "         WARNING: LLM_PROVIDER is 'openai' but OPENAI_API_KEY is missing."
    errors=$((errors + 1))
  fi
fi

if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  echo "[secret] Setting ANTHROPIC_API_KEY..."
  echo "$ANTHROPIC_API_KEY" | gh secret set ANTHROPIC_API_KEY --repo "$REPO"
  echo "         Done."
else
  echo "[secret] ANTHROPIC_API_KEY not set in environment — skipping."
  if [ "$PROVIDER" = "anthropic" ]; then
    echo "         WARNING: LLM_PROVIDER is 'anthropic' but ANTHROPIC_API_KEY is missing."
    errors=$((errors + 1))
  fi
fi

# --- Variables ---

echo "[var]    Setting LLM_PROVIDER=$PROVIDER..."
gh variable set LLM_PROVIDER --repo "$REPO" --body "$PROVIDER"
echo "         Done."

# --- Summary ---

echo ""
echo "==> Setup complete."
gh secret list --repo "$REPO" 2>/dev/null && echo "" || true
gh variable list --repo "$REPO" 2>/dev/null || true

if [ "$errors" -gt 0 ]; then
  echo ""
  echo "WARNING: $errors issue(s) detected. Review the output above."
  exit 1
fi
