---
name: github
description: Unified GitHub skill — repo management, PRs, issues, code review, Actions, and authentication. Works with gh CLI or git + curl fallback.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Repositories, Pull-Requests, Issues, Code-Review, CI/CD, Actions, Git]
    related_skills: []
    delegated_skills: [codebase-inspection]
---

# GitHub Unified Skill

Comprehensive GitHub workflow covering authentication, repos, PRs, issues, code review, and Actions. Prefers `gh` CLI when available, falls back to `git` + `curl` REST API.

---

## Delegation Table

| Task | Delegated Skill / Reference |
|------|---------------------------|
| GitHub authentication setup | `github-auth/` (see §1) |
| Repo create/clone/fork/settings/releases/secrets | `references/api-quick-ref.md` |
| PR lifecycle (create, monitor, merge) | `references/api-quick-ref.md` |
| Issues (create, triage, labels, assign) | `references/api-quick-ref.md` |
| Code review (local diffs, PR review, inline comments) | `references/review-checklist.md` |
| CI failure diagnosis and auto-fix | `references/ci-troubleshooting.md` |
| Conventional commit format | `references/conventional-commits.md` |
| API endpoint lookup (206 endpoints) | `references/api-index.md` |
| API details (parameters + examples) | `references/api-details.md` |
| Shell templates (bash/PowerShell) | `references/shell-templates.md` |
| LOC counting, language breakdown | `codebase-inspection/` (keep — unique) |

---

## §1 Authentication

See `github-auth/SKILL.md` for full setup. Quick detection:

```bash
source "${HERMES_HOME:-$HOME/.hermes}/skills/github/github-auth/scripts/gh-env.sh"
# Sets: GH_AUTH_METHOD (gh/curl/none), GITHUB_TOKEN, GH_USER, GH_OWNER, GH_REPO
```

---

## §2 Quick Auth Detection Pattern

At the start of any GitHub workflow, run this to determine the auth method:

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

---

## §3 Common Shell Patterns

**gh vs curl selection:**
```bash
# With gh
gh repo clone owner/repo
gh pr create --title "..." --body "..."

# With curl (set AUTH=curl, GITHUB_TOKEN=..., GH_OWNER, GH_REPO first)
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls \
  -d '{"title":"...","head":"branch","base":"main"}'
```

**Extract owner/repo from git remote:**
```bash
GH_OWNER_REPO=$(git remote get-url origin | sed -E 's|.*github\.com[:/]||; s|\.git$||')
GH_OWNER=$(echo "$GH_OWNER_REPO" | cut -d/ -f1)
GH_REPO=$(echo "$GH_OWNER_REPO" | cut -d/ -f2)
```

---

## §4 Rate Limiting

- Authenticated: **5,000 req/hour** (core API), **30 req/min** (Search API)
- Monitor via `x-ratelimit-remaining` and `x-ratelimit-reset` headers
- On 429 or secondary 403: wait `retry-after` or use exponential backoff (max 5 min)
- **Always use `per_page=100`** to avoid pagination truncation

---

## §5 High-Risk Operations (Confirmation Required)

These require explicit user confirmation before executing:

| Operation | API |
|-----------|-----|
| Delete repository | `DELETE /repos/{owner}/{repo}` |
| Merge PR | `PUT /repos/{owner}/{repo}/pulls/{n}/merge` |
| Delete branch | `DELETE /repos/{owner}/{repo}/git/refs/heads/{branch}` |
| Delete release | `DELETE /repos/{owner}/{repo}/releases/{id}` |
| Delete secret | `DELETE /repos/{owner}/{repo}/actions/secrets/{name}` |

---

## §6 Workflow Quick-Reference

### PR Workflow
```bash
# 1. Create branch
git checkout -b feat/my-feature

# 2. Make changes (use file tools)

# 3. Commit (see references/conventional-commits.md)
git add . && git commit -m "feat(scope): description"

# 4. Push
git push -u origin HEAD

# 5. Create PR
gh pr create --title "feat: ..." --body "..." \
  || curl -s -X POST .../pulls -d '{"title":"...","head":"branch","base":"main"}'

# 6. Monitor CI
gh pr checks --watch \
  || curl -s .../commits/$(git rev-parse HEAD)/status

# 7. Merge
gh pr merge --squash --delete-branch \
  || curl -s -X PUT .../pulls/N/merge -d '{"merge_method":"squash"}'
```

### Issue Workflow
```bash
# List open issues
gh issue list --state open \
  || curl -s "...issues?state=open&per_page=100" ...

# Create issue
gh issue create --title "..." --body "..." --label bug \
  || curl -s -X POST .../issues -d '{"title":"...","labels":["bug"]}'

# Triage: label + assign
gh issue edit N --add-label "priority:high" --add-assignee username
```

### Code Review (local diff)
```bash
# Get scope
git diff main...HEAD --stat

# Review full diff
git diff main...HEAD

# Check for common issues
git diff main...HEAD | grep -in "password\|secret\|TODO\|FIXME\|debugger"

# Present findings in structured format (see references/review-checklist.md)
```

---

## §7 API Reference Locations

| Reference | Contents | Lines |
|-----------|----------|-------|
| `references/api-index.md` | 206-endpoint table (Issues, PRs, Repos, Users, Search, Actions, Orgs, Git, Gists, Deployments) | ~270 |
| `references/api-details.md` | Parameter tables + curl examples for all endpoints | ~1360 |
| `references/shell-templates.md` | bash/PowerShell template conversion guide | ~70 |
| `references/api-quick-ref.md` | Merged from 5 sub-skills: cheatsheet, conventional commits, CI guide, review template | ~430 |

---

## §8 Security Rules

1. **Never echo token values** — only use in tool calls
2. **No token display** — even on user request
3. **No token in text output** — scripts only
4. **Check error body before assuming 403 is auth failure** — secondary rate limit also returns 403

---

## §9 Sub-Skill Reference (Absorbed)

These sub-skills have been merged into the unified `SKILL.md` + `references/`:

| Sub-skill | Status |
|-----------|--------|
| `github-repo-management/` | **Deleted** — merged into `references/api-quick-ref.md` |
| `github-pr-workflow/` | **Deleted** — merged into `references/api-quick-ref.md` + `references/conventional-commits.md` |
| `github-issues/` | **Deleted** — merged into `references/api-quick-ref.md` |
| `github-code-review/` | **Deleted** — merged into `references/review-checklist.md` |
| `github-auth/` | **Deleted** — auth section simplified above, full guide at `references/github-auth.md` |
| `devops/github-skill/` | **Deleted** — merged into `references/api-index.md` + `references/api-details.md` + `references/shell-templates.md` |
| `codebase-inspection/` | **Kept** — unique LOC/ pygount capability |
