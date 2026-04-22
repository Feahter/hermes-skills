# GitHub Authentication Setup

See `github-auth/SKILL.md` in the original skills for the full setup guide. This reference provides the quick auth detection pattern used by all GitHub workflows.

## Quick Auth Detection

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
  AUTH="gh"
elif [ -n "$GITHUB_TOKEN" ]; then
  AUTH="curl"
elif [ -f "$HOME/.hermes/.env" ] && grep -q "^GITHUB_TOKEN=" "$HOME/.hermes/.env" 2>/dev/null; then
  export GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "$HOME/.hermes/.env" | head -1 | cut -d= -f2 | tr -d '\n\r')
  AUTH="curl"
elif [ -f "$HOME/.git-credentials" ] && grep -q "github.com" "$HOME/.git-credentials" 2>/dev/null; then
  export GITHUB_TOKEN=$(grep "github.com" "$HOME/.git-credentials" | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
  AUTH="curl"
else
  AUTH="none"
fi
```

## Using the gh-env Helper

```bash
source "${HERMES_HOME:-$HOME/.hermes}/skills/github/github-auth/scripts/gh-env.sh"
# Sets: GH_AUTH_METHOD, GITHUB_TOKEN, GH_USER, GH_OWNER, GH_REPO, GH_OWNER_REPO
```

## Setting Token for API Calls

```bash
# Option 1: Export as env var
export GITHUB_TOKEN="ghp_..."

# Option 2: Extract from git credentials
GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
```

## Token Retrieval Script Pattern (devops/github-skill)

The devops/github-skill used `$(bash '<SCRIPT_PATH>/get-token.sh')` for inline token retrieval. This pattern is preserved in `references/api-details.md` for backward compatibility with workflows that reference the old skill directory.
