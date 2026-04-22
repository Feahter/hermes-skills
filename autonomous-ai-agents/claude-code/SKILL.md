---
name: claude-code
description: Delegate coding tasks to Claude Code (Anthropic's CLI agent). Use for building features, refactoring, PR reviews, and iterative coding. Requires the claude CLI installed.
version: 2.2.0
author: Hermes Agent + Teknium
license: MIT
metadata:
  hermes:
    tags: [Coding-Agent, Claude, Anthropic, Code-Review, Refactoring, PTY, Automation]
    related_skills: [codex, hermes-agent, opencode]
---

# Claude Code — Hermes Orchestration Guide

Delegate coding tasks to [Claude Code](https://code.claude.com/docs/en/cli-reference) (Anthropic's autonomous coding agent CLI) via the Hermes terminal. Claude Code v2.x can read files, write code, run shell commands, spawn subagents, and manage git workflows autonomously.

**Full CLI reference:** See [references/cli-reference.md](./references/cli-reference.md) for complete flags, slash commands, keyboard shortcuts, hooks, MCP, and env vars.

## Prerequisites

- **Install:** `npm install -g @anthropic-ai/claude-code`
- **Auth:** run `claude` once to log in (browser OAuth for Pro/Max, or set `ANTHROPIC_API_KEY`)
- **Console auth:** `claude auth login --console` for API key billing
- **SSO auth:** `claude auth login --sso` for Enterprise
- **Check status:** `claude auth status` (JSON) or `claude auth status --text` (human-readable)
- **Health check:** `claude doctor`
- **Update:** `claude update`

## Two Orchestration Modes

Hermes interacts with Claude Code in two fundamentally different ways. Choose based on the task.

### Mode 1: Print Mode (`-p`) — Non-Interactive (PREFERRED)

Print mode runs a one-shot task, returns the result, and exits. No PTY needed. No interactive prompts.

```bash
terminal(command="claude -p 'Add error handling to all API calls in src/' --allowedTools 'Read,Edit' --max-turns 10", workdir="/path/to/project", timeout=120)
```

**When to use print mode:**
- One-shot coding tasks (fix a bug, add a feature, refactor)
- CI/CD automation and scripting
- Structured data extraction with `--json-schema`
- Piped input processing (`cat file | claude -p "analyze this"`)
- Any task where you don't need multi-turn conversation

**Print mode skips ALL interactive dialogs** — no workspace trust prompt, no permission confirmations.

### Mode 2: Interactive PTY via tmux — Multi-Turn Sessions

Interactive mode gives you a full conversational REPL. **Requires tmux orchestration.**

```bash
# Start a tmux session
terminal(command="tmux new-session -d -s claude-work -x 140 -y 40")

# Launch Claude Code inside it
terminal(command="tmux send-keys -t claude-work 'cd /path/to/project && claude' Enter")

# Wait for startup, then send your task (~3-5 seconds for welcome screen)
terminal(command="sleep 5 && tmux send-keys -t claude-work 'Refactor the auth module to use JWT tokens' Enter")

# Monitor progress
terminal(command="sleep 15 && tmux capture-pane -t claude-work -p -S -50")

# Send follow-up tasks
terminal(command="tmux send-keys -t claude-work 'Now add unit tests for the new JWT code' Enter")

# Exit when done
terminal(command="tmux send-keys -t claude-work '/exit' Enter")
```

**When to use interactive mode:**
- Multi-turn iterative work (refactor → review → fix → test cycle)
- Tasks requiring human-in-the-loop decisions
- Exploratory coding sessions
- When you need Claude's slash commands (`/compact`, `/review`, `/model`)

## PTY Dialog Handling (CRITICAL for Interactive Mode)

Claude Code presents up to two confirmation dialogs on first launch. Handle these via tmux send-keys:

### Dialog 1: Workspace Trust (first visit)
```
❯ 1. Yes, I trust this folder    ← DEFAULT (just press Enter)
  2. No, exit
```
**Handling:** `tmux send-keys -t <session> Enter`

### Dialog 2: Bypass Permissions (only with `--dangerously-skip-permissions`)
```
❯ 1. No, exit                    ← DEFAULT (WRONG choice!)
  2. Yes, I accept
```
**Handling:** Must navigate DOWN first, then Enter:
```bash
tmux send-keys -t <session> Down && sleep 0.3 && tmux send-keys -t <session> Enter
```

### Robust Dialog Handling Pattern
```bash
# Launch with permissions bypass
terminal(command="tmux send-keys -t claude-work 'claude --dangerously-skip-permissions \"your task\"' Enter")

# Handle trust dialog (Enter for default "Yes")
terminal(command="sleep 4 && tmux send-keys -t claude-work Enter")

# Handle permissions dialog (Down then Enter for "Yes, I accept")
terminal(command="sleep 3 && tmux send-keys -t claude-work Down && sleep 0.3 && tmux send-keys -t claude-work Enter")

# Now wait for Claude to work
terminal(command="sleep 15 && tmux capture-pane -t claude-work -p -S -60")
```

**Note:** After first trust acceptance for a directory, the trust dialog won't appear again. Only the permissions dialog recurs each time you use `--dangerously-skip-permissions`.

## Print Mode Deep Dive

### Structured JSON Output
```bash
terminal(command="claude -p 'Analyze auth.py for security issues' --output-format json --max-turns 5", workdir="/project", timeout=120)
```

Returns a JSON object with `session_id`, `num_turns`, `total_cost_usd`, `subtype` (`success`, `error_max_turns`, `error_budget`).

### Streaming JSON Output
```bash
claude -p "Explain X" --output-format stream-json --verbose --include-partial-messages | \
  jq -rj 'select(.type == "stream_event" and .event.delta.type? == "text_delta") | .event.delta.text'
```

### Piped Input
```bash
# Pipe a file for analysis
cat src/auth.py | claude -p 'Review this code for bugs' --max-turns 1

# Pipe git diff
git diff HEAD~3 | claude -p 'Summarize these changes' --max-turns 1
```

### JSON Schema for Structured Extraction
```bash
claude -p 'List all functions in src/' --output-format json \
  --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}' \
  --max-turns 5
```

### Session Continuation
```bash
# Start a task
claude -p 'Start refactoring the database layer' --output-format json --max-turns 10 > /tmp/session.json

# Resume with session ID
claude -p 'Continue and add connection pooling' --resume $(cat /tmp/session.json | python3 -c 'import json,sys; print(json.load(sys.stdin)["session_id"])') --max-turns 5

# Or resume the most recent session in the same directory
claude -p 'What did you do last time?' --continue --max-turns 1

# Fork a session (new ID, keeps history)
claude -p 'Try a different approach' --resume <id> --fork-session --max-turns 10
```

### Bare Mode for CI/Scripting
```bash
claude --bare -p 'Run all tests and report failures' --allowedTools 'Read,Bash' --max-turns 10
```

`--bare` skips hooks, plugins, MCP discovery, and CLAUDE.md loading. Fastest startup. Requires `ANTHROPIC_API_KEY`.

### Fallback Model for Overload
```bash
claude -p 'task' --fallback-model haiku --max-turns 5
```
Automatically falls back to specified model when default is overloaded (print mode only).

## PR Review Pattern

### Quick Review (Print Mode)
```bash
git diff main...feature-branch | claude -p 'Review this diff for bugs, security issues, and style problems.' --max-turns 1
```

### Deep Review (Interactive + Worktree)
```bash
tmux new-session -d -s review -x 140 -y 40
tmux send-keys -t review 'cd /path/to/repo && claude -w pr-review' Enter
sleep 5 && tmux send-keys -t review Enter  # Trust dialog
sleep 2 && tmux send-keys -t review 'Review all changes vs main. Check for bugs, security issues.' Enter
sleep 30 && tmux capture-pane -t review -p -S -60
```

### PR Review from Number
```bash
claude -p 'Review this PR thoroughly' --from-pr 42 --max-turns 10
```

## Parallel Claude Instances

Run multiple independent Claude tasks simultaneously:

```bash
# Task 1: Fix backend
tmux new-session -d -s task1 -x 140 -y 40
tmux send-keys -t task1 'cd ~/project && claude -p "Fix the auth bug" --allowedTools "Read,Edit" --max-turns 10' Enter

# Task 2: Write tests
tmux new-session -d -s task2 -x 140 -y 40
tmux send-keys -t task2 'cd ~/project && claude -p "Write integration tests" --allowedTools "Read,Write,Bash" --max-turns 15' Enter

# Task 3: Update docs
tmux new-session -d -s task3 -x 140 -y 40
tmux send-keys -t task3 'cd ~/project && claude -p "Update README" --allowedTools "Read,Edit" --max-turns 5' Enter

# Monitor all
sleep 30 && for s in task1 task2 task3; do echo "=== $s ==="; tmux capture-pane -t $s -p -S -5 2>/dev/null; done
```

## CLAUDE.md — Project Context File

Claude Code auto-loads `CLAUDE.md` from the project root. Use it to persist project context:

```markdown
# Project: My API

## Architecture
- FastAPI backend with SQLAlchemy ORM
- PostgreSQL database, Redis cache
- pytest for testing with 90% coverage target

## Key Commands
- `make test` — run full test suite
- `make lint` — ruff + mypy
- `make dev` — start dev server on :8000

## Code Standards
- Type hints on all public functions
- Docstrings in Google style
- 2-space indentation for YAML, 4-space for Python
- No wildcard imports
```

**Be specific.** Instead of "Write good code", use "Use 2-space indentation for JS".

### Auto-Memory
Claude automatically stores learned project context in `~/.claude/projects/<project>/memory/`:
- **Limit:** 25KB or 200 lines per project
- This is separate from CLAUDE.md — it's Claude's own notes across sessions

## Monitoring Interactive Sessions

### Reading the TUI Status
```bash
tmux capture-pane -t dev -p -S -10
```

Look for indicators:
- `❯` at bottom = waiting for your input (Claude is done or asking)
- `●` lines = Claude is actively using tools
- `⏵⏵ bypass permissions on` = permissions mode
- `◐ medium · /effort` = current effort level
- `ctrl+o to expand` = tool output was truncated

### Context Window Health
Use `/context` in interactive mode:
- **< 70%** — Normal operation
- **70-85%** — Consider `/compact`
- **> 85%** — Hallucination risk spikes, use `/compact` or `/clear`

## Cost & Performance Tips

1. **Use `--max-turns`** in print mode (start with 5-10)
2. **Use `--max-budget-usd`** for cost caps (minimum ~$0.05)
3. **Use `--effort low`** for simple tasks, `high`/`max` for complex
4. **Use `--bare`** for CI/scripting to skip plugin overhead
5. **Use `--allowedTools`** to restrict to only what's needed
6. **Use `/compact`** when context gets large
7. **Pipe input** instead of having Claude read files for analysis
8. **Use `--model haiku`** for simple tasks, `--opus` for complex
9. **Use `--fallback-model haiku`** for graceful overload handling
10. **Start new sessions for distinct tasks** — fresh context is more efficient
11. **Use `--no-session-persistence`** in CI

## Pitfalls & Gotchas

1. **Interactive mode REQUIRES tmux** — Claude Code is a full TUI app
2. **`--dangerously-skip-permissions` dialog defaults to "No, exit"** — must send Down then Enter
3. **`--max-budget-usd` minimum is ~$0.05** — system prompt cache creation
4. **`--max-turns` is print-mode only** — ignored in interactive sessions
5. **Session resumption requires same directory** — `--continue` finds recent session for current CWD
6. **`--json-schema` needs enough `--max-turns`** — Claude must read files before producing output
7. **Trust dialog only appears once per directory** — then cached
8. **Background tmux sessions persist** — always clean up with `tmux kill-session -t <name>`
9. **Slash commands only work in interactive mode** — in `-p` mode, use natural language
10. **`--bare` skips OAuth** — requires `ANTHROPIC_API_KEY`
11. **Context degradation is real** — quality degrades above 70% context. Monitor with `/context`

## Rules for Hermes Agents

1. **Prefer print mode (`-p`)** — cleaner, no dialog handling, structured output
2. **Use tmux for multi-turn interactive work** — the only reliable way to orchestrate the TUI
3. **Always set `workdir`** — keep Claude focused on the right project directory
4. **Set `--max-turns` in print mode** — prevents infinite loops and runaway costs
5. **Monitor tmux sessions** — use `tmux capture-pane -t <session> -p -S -50`
6. **Look for `❯` prompt** — indicates Claude is waiting for input
7. **Clean up tmux sessions** — kill them when done to avoid resource leaks
8. **Report results to user** — summarize what Claude did
9. **Don't kill slow sessions** — Claude may be doing multi-step work
10. **Use `--allowedTools`** — restrict capabilities to what the task actually needs
