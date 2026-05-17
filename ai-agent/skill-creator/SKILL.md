---
name: skill-creator
description: "Load when: creating a new skill from scratch, editing or improving an existing skill, running evals to test skill quality, benchmarking performance, or optimizing a skill's description for better triggering accuracy. Keywords: create skill, edit skill, improve skill, run evals, benchmark, optimize description, skill-authoring"
---

# Skill Creator

> **Core paradigm (Perplexity, 2026):** A Skill is **not** code — it is **context for models**. Writing code and writing Skills require fundamentally different intuitions. Many patterns that make code clean make Skills ineffective.

## Zen of Skills vs Zen of Python

| Zen of Python | Zen of Skills |
|---|---|
| Simple is better than complex | **Complexity is the feature — multilevel hierarchy is indispensable** |
| Explicit is better than implicit | **Activation is implicit pattern matching — description is a routing trigger** |
| Sparse is better than dense | **Context is expensive — maximum signal per token** |
| Special cases aren't special enough | **Gotchas ARE the highest-value content** |
| If easy to explain, may be good | **If easy to explain, the model already knows it — delete it** |

## Skill Taxonomy: What vs When

- **Description field** = routing trigger ("Load when..."), NOT functional summary ("This Skill does X")
- **Body** = behavioral instructions + gotchas, NOT step-by-step procedure (model knows standard tools)
- **Supporting files** = only loaded when agent explicitly references them (lazy, not eager)

## Skill Tax (Pascal's Law)

> *"Je n'ai fait celle-ci plus longue que parce que je n'ai pas eu le loisir de la faire plus courte."* — Blaise Pascal, 1657

Every sentence in a Skill is paid by **everyone, every session, always**. If a sentence doesn't need to be there, it cannot afford to be there. A good Skill is as short as it can be.

**LLMs writing Skills for themselves provides no benefit.** Models cannot reliably author the procedural knowledge they benefit from consuming.

## Three-Tier Context Cost Model

| Tier | What | Budget | Who Pays |
|---|---|---|---|
| **Index** | `name: description` | ~100 tokens/Skill | Everyone, every session, always |
| **Load** | Full SKILL.md body | ~5,000 tokens | When Skill is loaded |
| **Runtime** | `references/`, `scripts/`, `assets/`, `FORMATTING.md`, `SPECIAL_CASES.md` | Unbounded | Only when agent explicitly reads them |

**Implication:** Index descriptions must be extremely terse (≤60 chars in our system). Runtime files should NOT be listed eagerly — let agent discover them as needed.

## Gotcha-First Writing

> **The highest-signal content in any Skill is the gotchas — boundary conditions, common mistakes, and edge cases.**

Don't write procedures the model already knows. Don't describe what the Skill does. Write:
- What the model gets wrong without this instruction
- What breaks in edge cases
- What the model assumes incorrectly

---

A skill for creating new skills and iteratively improving them.

## Process

### Step 0: Write Evals First (Evals-First Principle)

Source evaluation cases from:
- **Real user queries** — production samples or known conversation patterns
- **Known failures** — agent failed because the Skill didn't exist
- **Neighbor confusion** — close to domain boundary but routes elsewhere

**Negative examples are extremely powerful** — they often matter more than positive ones. A Skill that triggers incorrectly is worse than no Skill.

> ❌ "Model wrote a Skill for itself = no benefit." Perplexity research, 2026.

### Hermes Evals Integration

After writing evals, save to `~/.hermes/skills/.evals/{skill-name}.eval.md`:

```markdown
## POSITIVE — 应该触发
| # | 触发词 | 预期行为 | 边界条件 |

## NEGATIVE — 不应触发
| # | 触发词 | 不触发原因 | 正确路由 |

## BOUNDARY — 边界情况
| # | 触发词 | 边界描述 | 预期行为 |
```

Update `_index.md` after writing. See `~/.hermes/skills/.evals/_schema.md` for full format.

### Minimum Requirement
- **至少 3 条 POSITIVE + 2 条 NEGATIVE + 1 条 BOUNDARY**
- **禁止臆造触发词** — 必须来自真实 query

### Hermes Eval Loop
由于 Hermes 下 eval loop（`claude -p`）不可用，采用手动验证：
1. 生成 eval queries
2. 实际触发 skill 验证路由
3. 对比结果与预期，更新 eval 或 description

### Step 1: Write the Description (Hardest Part)

This is a **routing trigger**, not documentation.

| ❌ Bad | ✅ Good |
|---|---|
| "This Skill monitors pull requests" | "Load when: babysit this PR until it lands" |

**Checklist:**
- [ ] Starts with "Load when..." (not "Use when..." or "This Skill does...")
- [ ] Target 50 words or fewer
- [ ] Describes user's intent from real queries
- [ ] Does NOT summarize the workflow

### Step 2: Write the Body (Gotcha-First)

**Skip the obvious.** Don't write command sequences the model already knows.

| ❌ Don't | ✅ Do |
|---|---|
| `git log; git checkout main; git checkout -b <branch>; git cherry-pick <commit>` | "Cherry-pick the commit onto a clean branch. Resolve conflicts preserving intent. If it can't land cleanly, explain why." |

- Model knows standard tools — don't repeat them
- **Inline support file hints** — wherever the agent would need to go deeper (an example, a schema, a script), put a direct hint in the body: `→ See \`references/foo.md\`` so the agent knows exactly where to `skill_view()`
- **Focus on gotchas** — boundary conditions, failure modes, what breaks
- Conditional/branching logic belongs in `references/` or `scripts/`, not the hub

### Step 3: Standard Supporting Files

| File | Purpose | When to Create |
|---|---|---|
| `references/` | Heavy docs, loaded conditionally on demand | Domain-specific reference material |
| `scripts/` | Deterministic logic the agent would otherwise reinvent | "Give it code to compose, not reconstruct" |
| `assets/` | Templates, schemas, data | Structural inputs |
| `FORMATTING.md` | Output formatting rules | When output style matters |
| `SPECIAL_CASES.md` | Edge cases and gotchas | **Always create — gotchas are highest-value content**（模板 → `references/special-cases-template.md`） |

> Note: Our current runtime loading is "notification + agent self-loads" — agent sees the file list but must explicitly call `skill_view` to read. True lazy-loading (Perplexity model) requires architectural changes.

### Step 4: Iterate via Evals

Loop:
- Agent triggered incorrectly → tighten description, add negative evals
- Agent failed to trigger → add positive evals, clarify keywords
- Agent output wrong → add gotcha, add to `SPECIAL_CASES.md`

## ⚠️ Hermes Environment: Skip Step 3 Eval Loop

**Step 3（eval loop）不可用。** 优化 loop 依赖 `claude -p` 触发 skill 路由，在 Hermes 里是独立进程，不走 Hermes skill 加载 → 全零分数，误导优化。

**experiment-logger Phase 2/3 同样受限：**
- `--probe`（主动探测）依赖 `claude -p` executor，同样不可用
- `--scan`（被动边界学习）✅ 可用 — 从历史调用数据学习
- `skills_feedback.py --full-loop` ✅ 可用 — 更新边界签名

**Hermes 下 Skill Ratchet 正确流程：**
1. **Phase 1** — 写 evals（`~/.hermes/skills/.evals/{skill}.eval.md`）✅ 手动完成
2. **Phase 2** — eval loop 不可用，改为**被动积累**：真实用户调用 → experiment-logger 记录 → fail_cases 积累 → 手动生成 regression_tests
3. **Phase 3** — probe 不可用，改为**定期扫描**：`skills_feedback.py --scan <skill>` 从已有调用数据更新边界签名

## ⚠️ 高影响字段规范（来自 write-a-skill）

> 详细内容 → `references/write-a-skill-rules.md`（description 规范 / SKILL.md 行数限制 / 脚本添加原则）

---

## 道层工具

遇到复杂 skill 创建/优化决策时，可用 `talent-mind` 进行三层递归分析（系统A/系统B双轨 + 元认知校准）。

## Quick-start example

Here's a complete minimal skill that shows all the pieces working together:

```markdown
---
name: my-first-skill
description: Load when: user wants to X. Does Y. Keywords: X, Y, Z.
---

# My First Skill

## What it does
Explain in 1-2 sentences what this skill enables.

## When to trigger
List the exact contexts where this skill should activate.

## Gotchas

> **Most important section.** What does the model get wrong without this instruction? What breaks in edge cases?

> 📋 Gotcha 收集规范 → `references/special-cases-template.md`

## Verification Checklist

- [ ] Description starts with "Load when:" and is ≤ 150 chars
- [ ] SKILL.md body skips obvious steps — model knows standard tools
- [ ] At least 3 gotchas documented (in body or `SPECIAL_CASES.md`)
- [ ] Each gotcha: **error behavior** + **trigger condition** + **correct behavior**
- [ ] Supporting files placed in correct subdirs (`references/` / `scripts/` / `assets/`)
- [ ] Body contains inline hints `→ See \`references/...\`` directing agent to support files at natural decision points

## Step-by-step guide

> 详细内容 → `references/test-evaluation.md`（测试评估完整流程）
> 详细内容 → `references/improvement.md`（持续改进）
> 详细内容 → `references/description-optimization.md`（Description 优化）
> 详细内容 → `references/platform-notes.md`（Claude.ai / Cowork 特定说明）

---

## §Absorbed Sub-skills

The following narrow sub-skills have been absorbed into this umbrella (archived → content merged):

| Sub-skill | Absorbed as | Reason |
|-----------|------------|--------|
| `mattpocock/triage` | `references/mattpocock-triage.md` | Issue triage is a skill-authoring workflow phase |
| `mattpocock/diagnose` | `references/mattpocock-diagnose.md` | Diagnosis loop is a dev/debug phase within skill iteration |
| `mattpocock/to-issues` | `references/mattpocock-to-issues.md` | Breaking plans into issues is a skill planning workflow |
| `mattpocock/grill-me` | `references/mattpocock-grill-me.md` | Stress-testing designs is a skill validation phase |
| `mattpocock/to-prd` | `references/mattpocock-to-prd.md` | PRD authoring is a skill specification workflow |
| `ai-agent/write-a-skill` | (absorbed directly into body above) | Core skill-writing workflow already covered |

## Quick-Reference: Sub-Skill Workflows

### Issue Triage (from mattpocock/triage)
> "Triage issues through a state machine driven by triage roles."
- Use when: creating issues, reviewing bugs/feature requests, managing issue workflow
- Key concept: tracer-bullet vertical slices

### Diagnosis Loop (from mattpocock/diagnose)
> "Disciplined diagnosis loop for hard bugs: Reproduce → minimise → hypothesise → instrument → fix → regression-test."
- Use when: user says "diagnose this", reports a bug, describes performance regression
- Pattern: structured debugging with explicit hypothesis testing

### Plan → Issues (from mattpocock/to-issues)
> "Break a plan, spec, or PRD into independently-grabbable issues using tracer-bullet vertical slices."
- Output: project issue tracker tickets
- Key: vertical slices, not horizontal layers

### Design Stress-Test (from mattpocock/grill-me)
> "Interview the user relentlessly about a plan or design until reaching shared understanding."
- Pattern: one question at a time, resolve each branch of the decision tree

### Context → PRD (from mattpocock/to-prd)
> "Turn the current conversation context into a PRD and publish to the project issue tracker."

## Reference files

> 详细内容 → `references/schemas.md`（完整 schema，包含 assertions 字段）

