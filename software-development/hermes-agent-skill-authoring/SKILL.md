---
name: hermes-agent-skill-authoring
description: "Load when: editing or creating in-repo SKILL.md files under hermes-agent/skills/, or need frontmatter/validator/structure conventions. Keywords: SKILL.md, in-repo, authoring, frontmatter, validator, structure"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, authoring, hermes-agent, conventions, skill-md]
    related_skills: [writing-plans, requesting-code-review]
---

# Authoring Hermes-Agent Skills (in-repo)

## Overview

There are two places a SKILL.md can live:

1. **User-local:** `~/.hermes/skills/<maybe-category>/<name>/SKILL.md` — personal, not shared. Created via `skill_manage(action='create')`.
2. **In-repo (this skill is about this case):** `/home/bb/hermes-agent/skills/<category>/<name>/SKILL.md` — committed, shipped with the package. Use `write_file` + `git add`. `skill_manage(action='create')` does NOT target this tree.

## When to Use

- User asks you to add a skill "in this branch / repo / commit"
- You're committing a reusable workflow that should ship with hermes-agent
- You're editing an existing skill under `/home/bb/hermes-agent/skills/` (use `patch` for small edits, `write_file` for rewrites; `skill_manage` still works for patch on in-repo skills, but not for `create`)

## Description Format: Index Layer vs Load Layer

There are two description formats depending on which layer you're targeting:

| Layer | Format | Purpose |
|---|---|---|
| **Index** (in `available_skills` list) | `Load when: <intent>` | Routing trigger — should the agent load this Skill at all? |
| **Load** (Skill body) | `Use when: <task>` | Functional summary — what does this Skill enable? |

> **When to use which:** For `hermes-agent-skill-authoring` (in-repo skills), the frontmatter `description` field appears in the Index layer → use "Load when..." format. The body uses "Use when..." for human-readable guidance.

**Checklist for Index descriptions:**
- [ ] Starts with "Load when..." (capital L, lowercase w)
- [ ] Target 50 words or fewer
- [ ] Describes user's intent from real queries
- [ ] Does NOT summarize the workflow

## Required Frontmatter

Source of truth: `tools/skill_manager_tool.py::_validate_frontmatter`. Hard requirements:

- Starts with `---` as the first bytes (no leading blank line).
- Closes with `\n---\n` before the body.
- Parses as a YAML mapping.
- `name` field present.
- `description` field present, ≤ **1024 chars** (`MAX_DESCRIPTION_LENGTH`).
- Non-empty body after the closing `---`.

Peer-matched shape used by every skill under `skills/software-development/`:

```yaml
---
name: my-skill-name               # lowercase, hyphens, ≤64 chars (MAX_NAME_LENGTH)
description: Use when <trigger>. <one-line behavior>.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [short, descriptive, tags]
    related_skills: [other-skill, another-skill]
---
```

`version` / `author` / `license` / `metadata` are NOT enforced by the validator, but every peer has them — omit and your skill sticks out.

## Size Limits

- Description: ≤ 1024 chars (enforced).
- Full SKILL.md: ≤ 100,000 chars (enforced as `MAX_SKILL_CONTENT_CHARS`, ~36k tokens).
- Peer skills in `software-development/` sit at **8-14k chars**. Aim for that range. If you're pushing past 20k, split into `references/*.md` and reference them from SKILL.md.

## Peer-Matched Structure

Every in-repo skill follows roughly:

```
# <Title>

## Overview
One or two paragraphs: what and why.

## When to Use
- Bulleted triggers
- "Don't use for:" counter-triggers

## <Topic sections specific to the skill>
- Quick-reference tables are common
- Code blocks with exact commands
- Hermes-specific recipes (tests via scripts/run_tests.sh, ui-tui paths, etc.)

## Common Pitfalls
Numbered list of mistakes and their fixes.

## Verification Checklist
- [ ] Checkbox list of post-action verifications

## One-Shot Recipes (optional)
Named scenarios → concrete command sequences.
```

Not every section is mandatory, but `Overview` + `When to Use` + actionable body + pitfalls are the minimum for the skill to feel like a peer.

## Directory Placement

```
skills/<category>/<skill-name>/SKILL.md
```

Categories currently in repo (confirm with `ls skills/`): `autonomous-ai-agents`, `creative`, `data-science`, `devops`, `dogfood`, `email`, `gaming`, `github`, `leisure`, `mcp`, `media`, `mlops/*`, `note-taking`, `productivity`, `red-teaming`, `research`, `smart-home`, `social-media`, `software-development`.

Pick the closest existing category. Don't invent new top-level categories casually.

## Workflow

1. **Survey peers** in the target category:
   ```
   ls skills/<category>/
   ```
   Read 2-3 peer SKILL.md files to match tone and structure.
2. **Check validator constraints** in `tools/skill_manager_tool.py` if unsure.
3. **Draft** with `write_file` to `skills/<category>/<name>/SKILL.md`.
4. **Validate locally**:
   ```python
   import yaml, re, pathlib
   content = pathlib.Path("skills/<category>/<name>/SKILL.md").read_text()
   assert content.startswith("---")
   m = re.search(r'\n---\s*\n', content[3:])
   fm = yaml.safe_load(content[3:m.start()+3])
   assert "name" in fm and "description" in fm
   assert len(fm["description"]) <= 1024
   assert len(content) <= 100_000
   ```
5. **Git add + commit** on the active branch.
6. **Note:** the CURRENT session's skill loader is cached — `skill_view` / `skills_list` will not see the new skill until a new session. This is expected, not a bug.

## Lifecycle Hooks

Skills can declare lifecycle hooks in frontmatter to react to agent events (tool calls, LLM calls, session boundaries) — the same hooks that plugin modules use.

### Declaration

In `SKILL.md` frontmatter:

```yaml
hooks:
  - post_tool_call    # fires after every tool execution
  - pre_llm_call     # fires before every LLM call (can inject context)
  - on_session_reset # fires when user starts a new session
```

Supported hooks (same as plugin hooks): `pre_tool_call`, `post_tool_call`, `transform_tool_result`, `pre_llm_call`, `post_llm_call`, `transform_llm_output`, `pre_approval_request`, `post_approval_response`, `on_session_start`, `on_session_end`, `on_session_finalize`, `on_session_reset`, `subagent_stop`, `pre_gateway_dispatch`, `pre_api_request`, `post_api_request`.

### Declaration

In `SKILL.md` frontmatter:

```yaml
hooks:
  - post_tool_call    # fires after every tool execution
  - pre_llm_call     # fires before every LLM call (can inject context)
  - on_session_reset # fires when user starts a new session
```

Supported hooks (same as plugin hooks): `pre_tool_call`, `post_tool_call`, `transform_tool_result`, `pre_llm_call`, `post_llm_call`, `transform_llm_output`, `pre_approval_request`, `post_approval_response`, `on_session_start`, `on_session_end`, `on_session_finalize`, `on_session_reset`, `subagent_stop`, `pre_gateway_dispatch`, `pre_api_request`, `post_api_request`.

### Implementation

For each declared hook, create `scripts/<hook_name>.py` in the skill directory:

```python
# scripts/post_tool_call.py
def post_tool_call(tool_name, args, result, task_id="", session_id="",
                   tool_call_id="", duration_ms=0, **kwargs):
    """Called after every tool execution. Return None to no-op."""
    pass
```

**Callback signatures by hook:**

| Hook | Signature |
|------|-----------|
| `pre_tool_call` | `(tool_name, args, task_id, session_id, tool_call_id)` |
| `post_tool_call` | `(tool_name, args, result, task_id, session_id, tool_call_id, duration_ms)` |
| `transform_tool_result` | `(tool_name, args, result, task_id, session_id, tool_call_id)` |
| `pre_llm_call` | `(session_id, user_message, conversation_history, is_first_turn, model, platform, sender_id, **kwargs)` |
| `post_llm_call` | `(messages, response, session_id, task_id)` |
| `transform_llm_output` | `(messages, response, session_id, task_id)` → return modified response |
| `on_session_reset` | `(session_id, task_id)` |

Function name must match hook name (or use generic `callback` as fallback).

**`pre_llm_call` return values — two forms:**

```python
# Form 1: Context injection only (existing documented behavior)
{"context": "injected text..."}           # string preferred, auto-wrapped
{"context": "...", "tools": []}          # tools=[] is a no-op (keeps all tools)

# Form 2: Tool whitelisting (RFC #26524, implemented run_agent.py ~11817-11828)
{"context": "stage reminder...", "tools": ["read_file", "terminal"]}
# The "tools" key whitelists which tools the model sees this turn.
# Canonical reference skill: skills/system/stage-tool-whitelist/
#
# Core implementation in run_agent.py:
#   - Lines ~11817-11828: parse tools key from pre_llm_call hook results
#   - Lines ~12269-12279: filter api_kwargs["tools"] post-_build_api_kwargs
# The filter is a whitelist — tools NOT in the list are removed from the
# API call's tool schema. self.tools (session registry) is untouched.
```

The callback function name must match the hook name (or be named `callback` as fallback). It receives the same kwargs as the plugin hook equivalent.

### Session Scoping

Skill hooks are **session-scoped** — they register when the skill is loaded and automatically clear on `/new` (session reset). This differs from plugin hooks which persist for the process lifetime.

The registration is idempotent: loading the same skill twice in one session is a no-op.

### Registration Flow

When `build_skill_invocation_message()` or `build_preloaded_skills_prompt()` loads a skill, it calls `_register_skill_hooks()` which:
1. Reads `hooks:` from frontmatter
2. For each hook, checks `scripts/<hook_name>.py`
3. Imports via `importlib.util.spec_from_file_location`
4. Registers via `hermes_cli.plugins.register_skill_hook(skill_name, hook_name, callback)`

### Clearing on Session Reset

`cli.py` calls `clear_all_skill_hooks()` + clears `_registered_skill_hooks` on `/new`. Gateway paths fire the `on_session_reset` hook which triggers skill hook cleanup via the same mechanism.

### Canonical Use Case: context-pollution-defender

This skill is the reference implementation. It demonstrates all three hook patterns: `post_tool_call` for counting, `pre_llm_call` for injecting reminders, `on_session_reset` for cleanup.

**Frontmatter registration:**
```yaml
hooks:
  - post_tool_call
  - pre_llm_call
  - on_session_reset
```

**scripts/post_tool_call.py** (thread-safe counter, three thresholds):
```python
import threading, time
_counter_lock = threading.Lock()
_session_counters: dict[str, dict] = {}

def _get_session_key(session_id, task_id):
    return session_id or task_id or "default"

def _increment(session_id, task_id):
    key = _get_session_key(session_id, task_id)
    with _counter_lock:
        entry = _session_counters.setdefault(key, {"count": 0})
        entry["count"] += 1
        return entry["count"]

def post_tool_call(tool_name, args, result, task_id="", session_id="", **kwargs):
    count = _increment(session_id, task_id)
    if count == 16:
        _queue_reminder(session_id, task_id, "精简模式：减少解释，结论先行")
    elif count == 32:
        _queue_reminder(session_id, task_id, "极简模式：只做当前最小动作")
    elif count == 56:
        _queue_reminder(session_id, task_id, "应急模式：立即停止，发起上下文重置")

def _queue_reminder(session_id, task_id, message):
    key = _get_session_key(session_id, task_id)
    with _counter_lock:
        _session_counters.setdefault(key, {})["pending_reminder"] = message

# scripts/pre_llm_call.py (consumes the queued reminder):
def pre_llm_call(messages, session_id="", task_id="", **kwargs):
    key = _get_session_key(session_id, task_id)
    with _counter_lock:
        entry = _session_counters.pop(key, {})
        reminder = entry.get("pending_reminder")
    if reminder:
        return {"context": f"[上下文污染预警] {reminder}"}

# scripts/on_session_reset.py:
def on_session_reset(session_id="", task_id="", **kwargs):
    key = _get_session_key(session_id, task_id)
    with _counter_lock:
        _session_counters.pop(key, None)
```

Key design decisions:
- Thread-safe via `threading.Lock` (cron jobs run in thread pool)
- Session-scoped via session_id/task_id bucket key (not global counter)
- `pre_llm_call` returns `{"context": ...}` to inject into user message
- `on_session_reset` clears per-session state (handles `/new` in both CLI and gateway)

### RFC Workflow for Core Changes

When a feature requires modifying `run_agent.py`, `plugins.py`, or other core files
(beyond what a skill can achieve in userspace), follow the RFC process:

1. **Confirm repo:** `gh auth status` → verify GitHub credentials (user: Feahter, keyring)
2. **Draft RFC:** Write the RFC body to `/tmp/issue-body.md` with sections:
   - Summary / Motivation
   - Proposed solution (with code examples)
   - Alternatives considered
   - Implementation status (what's done locally vs. needs core)
3. **Create issue:** `gh issue create --repo NousResearch/hermes-agent --title "[RFC] <title>" --body-file /tmp/issue-body.md`
4. **Add labels:** `gh issue edit <num> --add-label type/feature,comp/agent` (maintainer-only; issue creation succeeds without)
5. **Post implementation status:** After local implementation, add a comment with:
   - What was built (with file:line references)
   - What remains (requires core changes)
   - Reference skill path if applicable

**Example RFC structure:**
```markdown
## Summary
Brief one-paragraph description.

## Motivation
Why this is needed (decision fatigue, performance, etc.).

## Proposed Solution
Exact code changes with file:line references.

## Status
| Item | Status |
|------|--------|
| Core mechanism | ✅ Done / ⬜ Not done |
```

The `stage-tool-whitelist` skill (`skills/system/stage-tool-whitelist/`) is a reference
implementation of an RFC-driven feature (RFC #26524) — three script files, one SKILL.md,
demonstrating the full hook authoring + RFC cycle.

## Cross-Referencing Other Skills

`metadata.hermes.related_skills` unions both trees (`skills/` in-repo and `~/.hermes/skills/`) at load time. You CAN reference a user-local skill from an in-repo skill, but it won't resolve for other users who clone the repo fresh. Prefer referencing only in-repo skills from in-repo skills. If a frequently-referenced skill lives only in `~/.hermes/skills/`, consider promoting it to the repo.

## Editing Existing In-Repo Skills

- **Small fix (typo, added pitfall, tightened trigger):** `skill_manage(action='patch', name=..., old_string=..., new_string=...)` works fine on in-repo skills.
- **Major rewrite:** `write_file` the whole SKILL.md. `skill_manage(action='edit')` also works but requires supplying the full new content.
- **Adding supporting files:** `write_file` to `skills/<category>/<name>/references/<file>.md`, `templates/<file>`, or `scripts/<file>`. `skill_manage(action='write_file')` also works and enforces the references/templates/scripts/assets subdir allowlist.
- **Always commit** the edit — in-repo skills are source, not runtime state.

## Common Pitfalls

1. **Using `skill_manage(action='create')` for an in-repo skill.** It writes to `~/.hermes/skills/`, not the repo tree. Use `write_file` for in-repo creation.

2. **Leading whitespace before `---`.** The validator checks `content.startswith("---")`; any leading blank line or BOM fails validation.

3. **Description format wrong for Index layer.** The frontmatter `description` field appears in `available_skills` (Index layer) → must start with "Load when..." not "Use when...". Body guidance can use "Use when...".

4. **Forgetting the author/license/metadata block.** Not validator-enforced, but every peer has it; omitting makes the skill look half-finished.

5. **Writing a skill that duplicates a peer.** Before creating, `ls skills/<category>/` and open 2-3 peers. Prefer extending an existing skill to creating a narrow sibling.

6. **Expecting the current session to see the new skill.** It won't. The skill loader is initialized at session start. Verify in a fresh session or via `skill_view` using the exact path.

7. **Linking to skills that don't exist in-repo.** `related_skills: [some-user-local-skill]` works for you but breaks for other clones. Prefer only in-repo links.

## Verification Checklist

- [ ] File is at `skills/<category>/<name>/SKILL.md` (not in `~/.hermes/skills/`)
- [ ] Frontmatter starts at byte 0 with `---`, closes with `\n---\n`
- [ ] `name`, `description`, `version`, `author`, `license`, `metadata.hermes.{tags, related_skills}` all present
- [ ] Name ≤ 64 chars, lowercase + hyphens
- [ ] Description ≤ 1024 chars and starts with "Load when ..." (Index layer routing trigger)
- [ ] Total file ≤ 100,000 chars (aim for 8-15k)
- [ ] Structure: `# Title` → `## Overview` → `## When to Use` → body → `## Common Pitfalls` → `## Verification Checklist`
- [ ] `related_skills` references resolve in-repo (or are explicitly OK to be user-local)
- [ ] `git add skills/<category>/<name>/ && git commit` completed on the intended branch
