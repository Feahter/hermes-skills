# Skill Cleanup Workflow — Validate Before Execution

Three-phase approach for auditing and consolidating a large skill library (100+ skills).

---

## Phase 1: Low-Risk Disk Operations (可直接执行)

- Delete empty/hollow skills (no content)
- Rename skills with better names
- Merge where absorption relationship is **unambiguous** (one skill explicitly says it absorbs another)
- Remove confirmed nested副本 (duplicate skill directories under another skill's path)

**Verification:** Run `python3 ~/.hermes/scripts/skill_registry.py` after each batch, confirm registry count decreases cleanly.

---

## Phase 2: Read Files Before Deciding (中风险)

For any proposed merge where the relationship is **unclear**, read both SKILL.md files before deciding.

### Red Flags That Indicate "Do NOT Merge"

| Pattern | Example | Why |
|---------|---------|-----|
| Different tool backends | `himalaya` (CLI) vs `imap-smtp-email` (full gateway) | Lightweight vs full-featured serve different use cases |
| Different language triggers | `brainstorming` (中文) vs `creative-ideation` (English constraint-based) | Same domain, different user language patterns |
| Different operational roles | `skill-creator` (create + benchmark + eval) vs `write-a-skill` (structured requirements) | One is superset in scope, but they serve different phases of creation |
| Different cognitive models | `ljg-think` (vertical drill-down) vs `talent-mind` (three-layer recursive OS) | Complementary mental tools |
| Different platform targets | `notion` vs `youdaonote` | Different APIs, different ecosystems |
| Architectural difference | `tapestry` (knowledge graph) vs `context-manager` (dialogue memory) | Different focus areas |

### Overlap Verification Gate (2026-05-15 新增)

当 skill-audit 或 combinator 发现"重叠"时，**必须先读取 SKILL.md 验证**，才能输出合并建议。

> **教训**：`xbrowser / agent-browser / browser-automation` 被 registry 描述相似度标记为重叠。实际读取后发现三者底层 CLI 不同（CDP vs Node vs Stagehand），能力有显著差异。registry 描述匹配 ≠ 实际功能重叠。

**判断可合并的充要条件**：
1. 一个 skill 的 SKILL.md 明确声明 absorbs 另一个
2. 两者底层 CLI 完全相同，只是描述文字不同
3. 两个 skill 的 description 完全相同

**不满足则保留独立** — 即使功能看起来"类似"，底层工具不同 = 能力集不同。

**验证方法**：
```bash
head -30 ~/.hermes/skills/<category>/<skill>/SKILL.md  # 看 description + backend
ls ~/.hermes/skills/<category>/<skill>/scripts/        # 脚本揭示真实工具链
```

### When in Doubt, Don't Merge — Add Cross-References Instead

For skills that are related but not mergeable:
1. Keep both skills independent
2. Add cross-reference in each skill's description

### Merge Decision Rule: Absorbed or Nothing

The only valid merge is **unambiguous absorption** — where one skill explicitly declares it absorbs another.

---

## Phase 3: High-Risk Decisions (需用户确认)

- Config file modifications
- Skills with external dependencies or service bindings
- Any skill where the "absorbed by" claim is unverified

**Always present the risk and await explicit confirmation before touching configuration files.**

---

## Decision Audit Checklist

Before executing any merge or delete:

- [ ] Read the actual SKILL.md content (not just registry description)
- [ ] Check if the skill has unique scripts, references/, or assets that would be lost
- [ ] Search for "related_skill" or "see also" cross-references in other skills
- [ ] Verify word-boundary matching in skill-combinator triggers (regex: `\bword\b`, not substring)
- [ ] Run registry rebuild after any disk operation
- [ ] **New (2026-05-15):** For any overlap claim, verify by reading SKILL.md and comparing backend tools before concluding merge

---

## Skill Registry Management

```bash
# Rebuild registry after any skill directory change
python3 ~/.hermes/scripts/skill_registry.py

# Verify alignment
python3 -c "
import json; from pathlib import Path
r = json.load(open(Path.home()/.hermes/.skill_registry.json))['skills']
d = list(Path.home()/.hermes/skills.rglob('SKILL.md'))
o = [n for n,i in r.items() if not Path(i['path']).exists()]
print(f'Registry: {len(r)}, Disk: {len(d)}, Orphans: {len(o)}')
"
```
