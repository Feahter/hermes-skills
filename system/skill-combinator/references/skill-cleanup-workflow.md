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
| Different cognitive models | `ljg-think` (vertical drill-down: 表象→机理→原理→公理) vs `talent-mind` (three-layer recursive OS) | Neither contains the other; they're complementary mental tools |
| Different platform targets | `notion` vs `youdaonote` | Different APIs, different ecosystems |
| Architectural difference | `tapestry` (knowledge graph) vs `context-manager` (dialogue memory) | One is about document relationships, the other about conversation context |

### When in Doubt, Don't Merge — Add Cross-References Instead

For skills that are related but not mergeable:
1. Keep both skills independent
2. Add cross-reference in each skill's description:
   ```
   For [alternative use case], see the separate '[other-skill]' skill.
   ```
3. This prevents combinator misfire while preserving both entry points.

### Merge Decision Rule: Absorbed or Nothing

The only valid merge is **unambiguous absorption** — where one skill explicitly declares it absorbs another. If neither skill acknowledges the other, they stay separate, even if they seem similar.

**Valid merge (absorption):**
- `web-ppt-skill` description says it "融合了 magazine-web-ppt × frontend-slides × html-ppt-skill" → delete absorbed skills ✅
- `office-toolkit` created to unify same tool category (xlsx + docx → both Office docs) ✅

**Invalid merge (no acknowledgment):**
- `ljg-think` and `talent-mind` — neither mentions the other, despite similar domain
- `notion` and `youdaonote` — different platforms, different APIs
- `himalaya` and `imap-smtp-email` — different backends (CLI vs gateway)

**Duplicate merge (identical content):** When two skills have the same description, same tools, same methods — merge immediately (e.g., pptx + powerpoint, both just python-pptx wrappers).

### YAML/Frontmatter Verification (Pre-Phase-1 Check)

Before starting cleanup, run a YAML validation pass to catch:
- Missing `---` frontmatter block
- Missing `name:` or `description:` fields
- Unquoted colons in description (`description: text with: colon` → YAML error)
- Python expressions in YAML fields (`"prettier" if '/' in full else "prettier"` → invalid YAML)

These are WARN-level issues (skill still loads) but should be fixed during cleanup.

---

## Phase 3: High-Risk Decisions (需用户确认)

- Config file modifications (e.g., `~/.hermes/config.yaml` changes)
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

---

## Skill Registry Management

```bash
# Rebuild registry after any skill directory change
python3 ~/.hermes/scripts/skill_registry.py

# Verify alignment (should show 0 orphans, registry count == disk SKILL.md count)
python3 -c "
import json; from pathlib import Path
r = json.load(open(Path.home()/'.hermes/.skill_registry.json'))['skills']
d = list(Path.home()/'.hermes/skills'.rglob('SKILL.md'))
o = [n for n,i in r.items() if not Path(i['path']).exists()]
print(f'Registry: {len(r)}, Disk: {len(d)}, Orphans: {len(o)}')
"
```
