# Code Review Checklist & Workflow

## Review Output Format

Use this structure for PR review summaries and inline comments:

```markdown
## Code Review Summary

**Verdict: [Approved ✅ | Changes Requested 🔴 | Reviewed 💬]** ([N] issues, [N] suggestions)

### 🔴 Critical
<!-- Issues that MUST be fixed before merge -->
- **file.py:line** — [description]. Suggestion: [fix].

### ⚠️ Warnings
<!-- Issues that SHOULD be fixed, but not strictly blocking -->
- **file.py:line** — [description].

### 💡 Suggestions
<!-- Non-blocking improvements -->
- **file.py:line** — [description].

### ✅ Looks Good
<!-- Positive observations -->
- [aspect done well]

---
*Reviewed by Hermes Agent*
```

## Severity Guide

| Level | Icon | When to use | Blocks merge? |
|-------|------|-------------|---------------|
| Critical | 🔴 | Security vulnerabilities, crashes, broken core functionality | Yes |
| Warning | ⚠️ | Bugs in non-critical paths, missing error handling, missing tests | Usually yes |
| Suggestion | 💡 | Style improvements, refactoring ideas, perf hints | No |
| Looks Good | ✅ | Clean patterns, good test coverage, clear naming | N/A |

## Verdict Decision

- **Approved ✅** — Zero critical/warning items
- **Changes Requested 🔴** — Any critical or warning item exists
- **Reviewed 💬** — Observations only (draft PRs, informational)

## Inline Comment Prefix Examples

```
🔴 **Critical:** User input passed directly to SQL query — use parameterized queries.
⚠️ **Warning:** This error is silently swallowed. At minimum, log it.
💡 **Suggestion:** This could be simplified with a dict comprehension.
✅ **Nice:** Good use of context manager — ensures cleanup on exceptions.
```

## Local (Pre-Push) Review Checklist

When reviewing local changes before push:

### 1. Get Scope
```bash
git diff main...HEAD --stat
git log main..HEAD --oneline
```

### 2. Review Per File
```bash
git diff main...HEAD -- path/to/file.py
# Then use read_file for full context around changes
```

### 3. Apply Checklist

**Correctness**
- Does the code do what it claims?
- Edge cases handled (empty inputs, nulls, large data)?
- Error paths handled gracefully?

**Security**
- No hardcoded secrets, credentials, or API keys
- Input validation on user-facing inputs
- No SQL injection, XSS, or path traversal
- Auth/authz checks where needed

**Code Quality**
- Clear naming (variables, functions, classes)
- No unnecessary complexity or premature abstraction
- DRY — no duplicated logic
- Functions are focused (single responsibility)

**Testing**
- New code paths tested?
- Happy path and error cases covered?
- Tests readable and maintainable?

**Performance**
- No N+1 queries or unnecessary loops
- Appropriate caching where beneficial
- No blocking operations in async code paths

**Documentation**
- Public APIs documented
- Non-obvious logic has comments explaining "why"
- README updated if behavior changed

### 4. Common Issue Detection

```bash
# Debug statements, TODOs, console.logs left behind
git diff main...HEAD | grep -in "print\|console\.log\|TODO\|FIXME\|HACK\|XXX\|debugger"

# Secrets or credential patterns
git diff main...HEAD | grep -in "password\|secret\|api_key\|token.*=\|private_key"

# Merge conflict markers
git diff main...HEAD | grep -n "<<<<<<\|>>>>>>\|======"

# Large files accidentally staged
git diff main...HEAD --stat | sort -t'|' -k2 -rn | head -10
```

## PR Review Workflow (End-to-End)

### Step 1: Set up environment
```bash
source "${HERMES_HOME:-$HOME/.hermes}/skills/github/github-auth/scripts/gh-env.sh"
```

### Step 2: Gather PR context
```bash
# With gh
gh pr view N
gh pr diff N --name-only
gh pr checks N

# With curl
PR_NUMBER=N
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER/files
```

### Step 3: Check out PR locally
```bash
git fetch origin pull/$PR_NUMBER/head:pr-$PR_NUMBER
git checkout pr-$PR_NUMBER
```

### Step 4: Read diff and understand changes
```bash
git diff main...HEAD
```

### Step 5: Run automated checks locally
```bash
# Run tests
python -m pytest 2>&1 | tail -20

# Run linter
ruff check . 2>&1 | head -30
```

### Step 6: Apply checklist (above)

### Step 7: Post review to GitHub

**With gh:**
```bash
# If no issues — approve
gh pr review $PR_NUMBER --approve --body "LGTM!"

# If issues found — request changes
gh pr review $PR_NUMBER --request-changes --body "Found issues — see inline comments."
```

**With curl (atomic review with inline comments):**
```bash
HEAD_SHA=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER/reviews \
  -d "{
    \"commit_id\": \"$HEAD_SHA\",
    \"event\": \"REQUEST_CHANGES\",
    \"body\": \"## Hermes Agent Review\n\nFound issues. See inline comments.\",
    \"comments\": [
      {\"path\": \"src/auth.py\", \"line\": 45, \"body\": \"🔴 Critical: SQL injection risk — use parameterized queries.\"}
    ]
  }"
```

### Step 8: Clean up
```bash
git checkout main
git branch -D pr-$PR_NUMBER
```
