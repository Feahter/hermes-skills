# GitHub Repo Wiki Ingestion — Session Patterns

## Source Cloning

### Shallow Clone (Always Use)
```bash
git clone --depth=1 https://github.com/owner/repo.git /tmp/RepoName
```
- `--depth=1` avoids timeout on large repos (>100MB pack)
- Timeout at 60s → retry with 90s or add `--depth=1`
- Clone to `/tmp/` for ephemeral workspace; wiki raw content goes to `~/wiki/raw/github/`

### Full Clone (When Needed)
```bash
git clone https://github.com/owner/repo.git ~/wiki/raw/github/repo-name/
```
Only use full clone when you need git history for later inspection.

---

## Directory Layout

```
/tmp/ClaudeCode101/          # git clone workspace
  ├── 01-llm-fundamentals.md
  ├── 02-what-is-claude-code.md
  └── img/                    # images referenced in markdown
      └── agentic-loop.svg

~/wiki/raw/github/ClaudeCode101-surfalytics-2026-05-16.md  # consolidated raw
~/wiki/entities/              # people, companies, products
~/wiki/concepts/              # methods, frameworks, techniques
```

---

## Ingestion Pattern (This Session)

### Step 1: Clone
```bash
git clone --depth=1 https://github.com/surfalytics/ClaudeCode101.git /tmp/ClaudeCode101
```

### Step 2: List Files
```bash
find /tmp/ClaudeCode101 -type f | grep -v '.git/'
```

### Step 3: Read All Files in Parallel
Read all markdown files simultaneously — small repo (12 files), all readable in one batch.

### Step 4: Wiki Page Creation (Batch)
Create **all** wiki pages in one round of parallel `write_file` calls:

| Type | Count | Examples |
|------|-------|---------|
| Raw article | 1 | ClaudeCode101-surfalytics-2026-05-16.md |
| Entities | 2 | surfalytics-dmitry-anoshin, claude-code |
| Concepts | 7 | agentic-loop, agent-teams, agent-skills, claude-md, headless-mode, mcp-model-context-protocol, sub-agents |

**Parallelism**: 8~10 `write_file` calls in one batch — no subagents needed for small repos.

### Step 5: Update Index
`index.md` header: update total page count and date.
Insert new entity entries in alphabetical order within their section.
Insert new concept entries in alphabetical order within Concepts section.

### Step 6: Append Log
```bash
## [2026-05-16] ingest | Claude Code 101 (surfalytics)
- Source: github.com/surfalytics/ClaudeCode101 (shallow clone)
- Raw: raw/articles/ClaudeCode101-surfalytics-2026-05-16.md
- Entities: surfalytics-dmitry-anoshin, claude-code (update)
- Concepts: agentic-loop, agent-teams, agent-skills, claude-md, headless-mode, mcp-model-context-protocol
- Index更新: 134→145頁
- Key content: 10模块数据专业人士Claude Code完整教程，涵盖LLM基础→Agent Army→MCP→多模型路由
```

---

## Key Lesson: Index Update Order (Entity Before Concept)

When updating `index.md`, entity entries must be added **before** concept entries. This matters because:
- Entities are listed first in the index file
- Wikilinks in concept pages often reference entity pages
- Consistent ordering prevents merge conflicts in collaborative wiki editing

Pattern:
```
## Entities
...
- [[surfalytics-dmitry-anoshin]] — Claude Code 101课程作者...

## Concepts（新增）
...
- [[agentic-loop]] — gather→action→verify→repeat自主循环
```

---

## Duplicate Entry Prevention

When adding entries to `index.md`, read the relevant section first. If the entry already exists (e.g., `[[Claude-Code]]` was already present), either:
- Update the existing entry with new information, OR
- Skip adding a duplicate entry

**Safe check**: `grep -n "Claude-Code" ~/wiki/index.md` before inserting.

---

## Wikilink Consistency

After batch creating wiki pages, verify all `[[wikilinks]]` resolve to existing files:

```bash
cd ~/wiki
grep -rho '\[\[[^]]\+\]\]' entities/ concepts/ | sort -u | sed 's/\[\[\([^\]]*\)\]\]/\1/g' > /tmp/links_needed.txt
find entities/ concepts/ -name "*.md" | xargs -I{} basename {} .md > /tmp/files_exist.txt
diff /tmp/links_needed.txt /tmp/files_exist.txt
```

**Common error**: CamelCase wikilink vs lowercase filename mismatch. e.g., `[[Claude-Code]]` but file is `claude-code.md`. Fix with `patch`.

---

## When to Use Subagents vs Direct Write

| Repo Size | Approach |
|-----------|----------|
| < 20 files | Direct `write_file` batch (this session's approach) |
| 20~50 files | `delegate_task` with 4-task batches |
| > 50 files | Split: subagent for raw extraction, main agent for wiki page creation |

**Subtask timeout protection (from skill)**:
-单个 delegate_task 的 task scope **必须小于 5 分钟预期**
- 大任务拆分粒度
- 超时后：主 agent 接手完成，不重试整个任务