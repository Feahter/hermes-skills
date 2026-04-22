# GitHub API Quick Reference

Base URL: `https://api.github.com` | Auth: `-H "Authorization: token $GITHUB_TOKEN"`

Helper: `source "${HERMES_HOME:-$HOME/.hermes}/skills/github/github-auth/scripts/gh-env.sh"`

## Repositories

| Action | Method | Endpoint |
|--------|--------|----------|
| Get repo info | GET | `/repos/{owner}/{repo}` |
| Create repo (user) | POST | `/user/repos` |
| Create repo (org) | POST | `/orgs/{org}/repos` |
| Update repo | PATCH | `/repos/{owner}/{repo}` |
| Delete repo ⚠️ | DELETE | `/repos/{owner}/{repo}` |
| List your repos | GET | `/user/repos?per_page=30&sort=updated` |
| Fork repo | POST | `/repos/{owner}/{repo}/forks` |
| Create from template | POST | `/repos/{owner}/{template}/generate` |
| Get/set topics | GET/PUT | `/repos/{owner}/{repo}/topics` |
| List branches | GET | `/repos/{owner}/{repo}/branches` |
| Branch protection | GET/PUT/DELETE | `/repos/{owner}/{repo}/branches/{branch}/protection` |
| Clone repo | git | `git clone https://github.com/owner/repo.git` |
| List secrets | GET | `/repos/{owner}/{repo}/actions/secrets` |
| Set secret | PUT | `/repos/{owner}/{repo}/actions/secrets/{name}` (needs encryption) |

## Pull Requests

| Action | Method | Endpoint |
|--------|--------|----------|
| List PRs | GET | `/repos/{owner}/{repo}/pulls?state=open` |
| Create PR | POST | `/repos/{owner}/{repo}/pulls` |
| Get PR | GET | `/repos/{owner}/{repo}/pulls/{number}` |
| Update PR | PATCH | `/repos/{owner}/{repo}/pulls/{number}` |
| List PR files | GET | `/repos/{owner}/{repo}/pulls/{number}/files` |
| Merge PR ⚠️ | PUT | `/repos/{owner}/{repo}/pulls/{number}/merge` |
| Request reviewers | POST | `/repos/{owner}/{repo}/pulls/{number}/requested_reviewers` |
| Create review | POST | `/repos/{owner}/{repo}/pulls/{number}/reviews` |
| Create review (inline) | POST | `/repos/{owner}/{repo}/pulls/{number}/comments` |
| Check out PR locally | git | `git fetch origin pull/N/head:pr-N && git checkout pr-N` |

**Merge body:** `{"merge_method": "squash", "commit_title": "feat: description (#N)"}`
**Merge methods:** `"merge"`, `"squash"`, `"rebase"`
**Review events:** `"APPROVE"`, `"REQUEST_CHANGES"`, `"COMMENT"`

## Issues

| Action | Method | Endpoint |
|--------|--------|----------|
| List issues | GET | `/repos/{owner}/{repo}/issues?state=open` |
| Create issue | POST | `/repos/{owner}/{repo}/issues` |
| Get issue | GET | `/repos/{owner}/{repo}/issues/{number}` |
| Update issue | PATCH | `/repos/{owner}/{repo}/issues/{number}` |
| Add comment | POST | `/repos/{owner}/{repo}/issues/{number}/comments` |
| Add labels | POST | `/repos/{owner}/{repo}/issues/{number}/labels` |
| Remove label | DELETE | `/repos/{owner}/{repo}/issues/{number}/labels/{name}` |
| Add assignees | POST | `/repos/{owner}/{repo}/issues/{number}/assignees` |
| List labels | GET | `/repos/{owner}/{repo}/labels` |
| Search issues | GET | `/search/issues?q={query}+repo:{owner}/{repo}` |
| Lock/unlock issue | PUT/DELETE | `/repos/{owner}/{repo}/issues/{number}/lock` |

Note: The Issues API also returns PRs. Filter with `'pull_request' not in item` when parsing.

## CI / GitHub Actions

| Action | Method | Endpoint |
|--------|--------|----------|
| List workflows | GET | `/repos/{owner}/{repo}/actions/workflows` |
| List runs | GET | `/repos/{owner}/{repo}/actions/runs?per_page=10` |
| Get run | GET | `/repos/{owner}/{repo}/actions/runs/{run_id}` |
| Download logs | GET | `/repos/{owner}/{repo}/actions/runs/{run_id}/logs` |
| Re-run | POST | `/repos/{owner}/{repo}/actions/runs/{run_id}/rerun` |
| Re-run failed | POST | `/repos/{owner}/{repo}/actions/runs/{run_id}/rerun-failed-jobs` |
| Trigger dispatch ⚠️ | POST | `/repos/{owner}/{repo}/actions/workflows/{id}/dispatches` |
| Cancel run | POST | `/repos/{owner}/{repo}/actions/runs/{run_id}/cancel` |
| Commit status | GET | `/repos/{owner}/{repo}/commits/{sha}/status` |
| Check runs | GET | `/repos/{owner}/{repo}/commits/{sha}/check-runs` |
| List artifacts | GET | `/repos/{owner}/{repo}/actions/artifacts` |

## Releases

| Action | Method | Endpoint |
|--------|--------|----------|
| List releases | GET | `/repos/{owner}/{repo}/releases` |
| Create release | POST | `/repos/{owner}/{repo}/releases` |
| Get release | GET | `/repos/{owner}/{repo}/releases/{id}` |
| Delete release ⚠️ | DELETE | `/repos/{owner}/{repo}/releases/{id}` |
| Upload asset | POST | `https://uploads.github.com/repos/{owner}/{repo}/releases/{id}/assets?name={filename}` |

## Users

| Action | Method | Endpoint |
|--------|--------|----------|
| Get current user | GET | `/user` |
| List user repos | GET | `/user/repos` |
| List user gists | GET | `/gists` |
| Create gist | POST | `/gists` |
| Search repos | GET | `/search/repositories?q={query}` |

## Search

| Action | Method | Endpoint |
|--------|--------|----------|
| Search repos | GET | `/search/repositories?q=...` |
| Search issues | GET | `/search/issues?q=...` |
| Search code | GET | `/search/code?q=...` |
| Search users | GET | `/search/users?q=...` |

Note: Search API has independent rate limit (30 req/min for authenticated).

## Common curl Patterns

```bash
# GET
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO

# POST with JSON body
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/issues \
  -d '{"title": "...", "body": "..."}'

# PATCH (update)
curl -s -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/issues/42 \
  -d '{"state": "closed"}'

# DELETE
curl -s -X DELETE \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/issues/42/labels/bug

# Parse JSON response with python3
curl -s ... | python3 -c "import sys,json; data=json.load(sys.stdin); print(data['field'])"
```

## Pagination

- Use `?per_page=100` on all list endpoints (GitHub default 30 causes silent truncation)
- Check `Link` header for `rel="next"` URL to determine if more pages exist
- Extract next URL: `grep -oP '<\K[^>]+(?=>; rel="next")'`
