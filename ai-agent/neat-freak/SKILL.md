---
name: neat-freak
description: 知识库同步 Skill — 会话结束时同步项目文档和 Agent 记忆，OCD 级严格。触发词：同步、整理文档、更新记忆、收尾、梳理。源自 KKKKhazix/khazix-skills。
---

# Neat-Freak: Knowledge Base Synchronization Skill

## Overview

**Purpose**: End-of-session knowledge cleanup with OCD-level rigor — reconciles project docs (CLAUDE.md, README.md, docs/) and agent memory against the code so nothing rots.

**Core Principle**: You are a **knowledge base editor**, not a recorder. Editors review globally, merge duplicates, fix outdated info, and delete obsolete content. Recorders just append.

**Why It Matters**: Code can be rewritten anytime, but **docs and memory are the only bridges across sessions and agents**. Stale docs = wrong decisions by future agents. Confusing docs = wasted time by teammates.

## Trigger Modes

### Mode 1: Language Triggers (Explicit)

**MUST trigger** when user says any of:

| English | Chinese |
|---------|---------|
| "sync up" | "同步一下" |
| "tidy up docs" | "整理文档" |
| "update memory" | "更新记忆" |
| "clean up docs" | "整理一下" |
| "/sync" | "梳理一下" |
| "/neat" | "收尾" |
| "新人能直接上手" | "这个阶段做完了" |

**Also trigger when**: User reports stale docs, conflicting memories, or wants clean handoff to teammates/other agents.

> **Note**: Bare "整理" / "tidy" with prior dev context counts — do NOT under-trigger.

**Platforms**: Claude Code, OpenAI Codex, OpenCode, OpenClaw, Hermes

> **Memory Palace Pattern**: When restructuring large memory systems (single file >5KB or multi-topic), apply the three-layer routing model (Index → Load → Reference). See `references/memory-palace.md` for the architectural pattern and实施 guide.

## Key Concept: Three Types of Knowledge, Three Audiences

**Critical**: If you only edit CLAUDE.md and ignore docs/, you leave downstream colleagues and other agents stranded.

| Location | Audience | Responsibility | Cost of Not Syncing |
|----------|----------|----------------|---------------------|
| **Agent Memory System** | Agent self (cross-session) | Personal preferences, non-obvious facts, cross-project references | Agent forgets historical decisions |
| **Project Root `CLAUDE.md` / `AGENTS.md`** | AI in current project (next session) | Conventions, structure, red lines, env vars, route inventory | Next AI wastes time figuring things out |
| **Project `docs/` + `README.md`** | **Others** (human colleagues, downstream devs, future AI) | Onboarding, architecture diagrams, ops manual, handoff notes, API reference | **Others cannot correctly integrate or operate** |

### Critical Rule: Two Docs, Two Jobs

```
CLAUDE.md: "Added device flow with 5 routes"
           ↓
docs/integration-guide.md: "How downstream connects to this flow"
```

> **判断标准**: If user just finished building/modifying something and hasn't synced docs — trigger. Better to over-trigger than under-trigger.

### Mode 3: Proactive Trigger (Recommended)

After completing significant dev work (new API, env var, database table, multi-file feature), ASK at the end:
> "同步一下文档？" — don't wait to be asked.

---

## Source of Truth Rule

**Code is always the source of truth.** When doc and code conflict, trust code, update doc. Never modify code to match doc.

- README.md vs *.py → update README
- CLAUDE.md describes non-existent route → delete from CLAUDE.md, update docs/
- Memory has overturned decision → delete old, keep new

---

## Handling Missing docs/ (Graceful Degradation)

If `docs/` directory does not exist:

1. **Don't create unless necessary.** Only create if project genuinely needs docs (API surface, ops runbook)
2. **If creating**: Use standard structure — `docs/integration-guide.md`, `docs/architecture.md`, `docs/operator-runbook.md`
3. **If skipping**: Add comment in CLAUDE.md: `<!-- docs/ skipped: reason -->`

---

## Execution Flow

### Step 1: Inventory Current State (MANDATORY — NO EXCEPTIONS)

**First: ls, then judge.** Do not skip.

1. **List agent memory files** (if applicable):
   ```bash
   ls ~/.claude/projects/<...>/memory/
   cat MEMORY.md
   cat all referenced .md files
   ```

2. **For each project in this conversation**:
   ```bash
   ls /                    # Confirm root structure
   ls /docs/ 2>/dev/null   # ENUMERATE all docs (confirm if missing)
   find . -maxdepth 2 -name "*.md" \
     -not -path "*/node_modules/*" \
     -not -path "*/.git/*"   # Catch straggler .md files
   ```
   Read: `README.md`, `CLAUDE.md`/`AGENTS.md`, every `docs/*.md`

3. **Read global agent config** (if any): `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`

4. **Review entire conversation content**

**Output**: You MUST produce a written file manifest before proceeding to Step 2. This is your checkpoint — without it, you have not completed Step 1.

```markdown
## File Manifest — [Project Name]
| File | Status | Action |
|------|--------|--------|
| README.md | ✅ No changes | — |
| CLAUDE.md | 🔧 Modified | Update route list |
| docs/architecture.md | ⏭️ Not applicable | No relevant content |
| Memory/MEMORY.md | 🔧 Modified | Delete completed todos |
```
> **If you cannot produce this manifest, you have NOT finished Step 1. Do not proceed to Step 2.**

### Step 2: Identify Changes — Use "Change Impact Matrix"

**Don't just look at conversation 增量; look at which doc layers the changes affect.**

| Change Type | Requires Updates To |
|-------------|---------------------|
| New API/Routes | CLAUDE.md route list + integration-guide + architecture Routes section |
| New/Renamed Env Var | CLAUDE.md env table + runbook + downstream integration-guide |
| New Database Table | CLAUDE.md + architecture Data Model |
| Large Feature (multi-file) | All above + architecture new section + handoff/completed checklist |
| **Cross-project change** | **Both upstream AND downstream docs** |
| Memory: relative time | Convert to absolute date |
| Memory: outdated fact | Update |
| Memory: duplicate | Merge |
| Memory: completed todo | Delete |

### Step 3: Actually Edit (Use Tools, Don't Just Describe)

**Must use Edit/Write/Delete commands. Describing changes ≠ completing them.**

**Priority Order**: docs/ (external) → CLAUDE.md/AGENTS.md → Memory

**Editing Principles**:

| Principle | Application |
|-----------|-------------|
| **Merge > Append** | New info updates old entries, don't add another line |
| **Archive > Delete** | For memory: move obsolete items to `docs/archive/` with date, don't permanently erase — context matters |
| **Rewrite > Patch** | If entry is confusing, rewrite for clarity |

> **Why Archive not Delete**: Future debugging often needs to understand WHY a decision was made, not just what the current state is. Delete only truly ephemeral context (session-only temporary notes).

### Step 4: Final Verification

Run these commands and confirm no stale references remain:

```bash
grep -r "TODO" docs/ --include="*.md" | grep -v "template"
grep -r "FIXME" docs/ --include="*.md"
grep -r "old\|deprecated\|outdated" docs/ --include="*.md"
grep -rn "<username>" . --include="*.md" 2>/dev/null | grep -v "/node_modules/"
```

## Change Impact Matrix (Full)

### Code Layer → Doc Layer

| 本次对话发生的事 | 要改的文件(按受众) |
|---|---|
| 新增 API / 路由 | 项目根 markdown 路由清单 · `docs/integration-guide.md` API 速查表 · `docs/architecture.md` Routes 小节 |
| 新增 / 改名 环境变量 | 项目根 markdown 环境变量表 · `docs/operator-runbook.md` 环境变量章节 · `docs/integration-guide.md`(如果下游要配) |
| 新增数据库表 / 列 | 项目根 markdown 数据库表 · `docs/architecture.md` Data Model |
| 新增 / 改动 用户流程 | 项目根 markdown 用户流程 · README 相关命令行示例 · `docs/handoff.md` What Exists Today |
| 大特性(能跨多文件) | 以上全部 + `docs/architecture.md` 新增章节 + `docs/handoff.md` 已完成清单 |
| 新增术语 / 改命名 | `docs/integration-guide.md` 术语表 + 全局搜索旧术语替换 |
| 部署参数 / 基础设施变化 | `docs/operator-runbook.md` · 项目根 markdown 部署章节 |
| 下游项目接入方式变化 | 下游项目的 `docs/.md` · 上游项目的 `integration-guide.md` |

### Memory Layer

> **Boundary with context-manager**: context-manager handles active session context compression (what to keep in current context window). neat-freak handles cross-session persistence (what to sync to durable memory after session). They complement — don't conflate them.

| 情况 | 处理方式 |
|---|---|
| 过期事实 | 改记忆文件，同时更新索引(如 MEMORY.md)的 description |
| 相对时间("今天"、"最近") | 全部转成绝对日期(`2026-04-29` 而非"今天") |
| 重复记录(多条说同一件事) | 合并为一条，改索引 |
| 已完成的待办 | 归档到 `docs/archive/decisions-YYYY-MM.md`（带时间戳和原因），不要删除 |
| 推翻的决策 | 归档旧条目，留新决策 |
| 跨会话只用一次的临时上下文 | 删除（这是唯一直接删除的情况） |

### Cross-Project Check

最容易漏改的场景：
- **上游 API 变了 → 下游 SDK 文档**: 协议变化必须两边对齐
- **共享子域 / 路由 / 环境变量改了 → 所有 consumer 项目的 setup 文档**
- **认证中台变更 → 所有接入应用的 integration guide**
- **公共组件 / 基础设施 升级 → 各项目的 operator-runbook 提及版本号的地方**

## Common Patterns

1. **New API Added**: Route list + integration guide + architecture routes + memory
2. **Env Var Changed**: All places referencing old name + downstream docs + memory
3. **Memory Cleanup**: Delete completed todos, convert relative times, merge duplicates
4. **Large Feature**: Full doc sweep (all layers) + memory update

## Pitfalls

- **Under-triggering**: Bare "整理" without dev context still counts if prior conversation had dev content
- **Only editing CLAUDE.md**: Ignoring docs/ leaves human teammates stranded
- **Append-only mindset**: Not deleting obsolete content creates noise
- **Missing cross-project**: Forgetting to update downstream docs when upstream changes
- **Skipping Step 1 inventory**: Going straight to changes without reading all files first
- **Coding before indexing**: When restructuring memory systems, always create the routing layer (`_index.md`) and split files BEFORE touching code. The routing layer is the spec for the code changes.
- **Inventing changes**: Don't write new content that isn't backed by this conversation — sync reality, don't create fiction
- **Conflating with context-manager**: These are different tools — context-manager = compression, neat-freak = sync

## Verification Commands

```bash
# Check for stale TODOs
grep -r "TODO" docs/ --include="*.md" | grep -v "template"

# Check for outdated markers
grep -r "FIXME\|deprecated\|outdated" docs/ --include="*.md"

# Check for hardcoded usernames or session-specific content
grep -rn "<username>\|<your_name>\|session" . --include="*.md" 2>/dev/null | grep -v "/node_modules/"

# Verify links still work
find docs/ -name "*.md" -exec grep -l "http" {} \; | xargs -I {} sh -c 'echo "Checking {}"; curl -s -o /dev/null -w "%{http_code}" $(grep -o "http[s]*://[^)]*" {} | head -1)'
```

## Skill Origin

Based on [KKKKhazix/khazix-skills/neat-freak](https://github.com/KKKKhazix/khazix-skills/tree/main/neat-freak)
