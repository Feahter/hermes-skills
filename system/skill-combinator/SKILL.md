---
name: skill-combinator
description: Skills 组合涌现引擎 — 根据任务特征自动发现、排序、组合 skills。触发：多 skill 协作需求、复杂任务分解、技能选型决策。
version: 1.0.0
author: Hermes Agent
metadata:
  combinator:
    phases: [integration]
    triggers: [skill组合, 多skill, 协作, 涌现]
---

# SkillCombinator

Skills 组合涌现引擎。根据任务特征自动发现最合适的 skill 组合，避免 1+1=2。

## 何时激活

- 用户提到"组合"、"协作"、"多个 skill"
- 复杂任务需要多阶段处理（分析→生成→验证）
- skill-orchestrator 需要扩展时

## Schema：Skill 能力声明

在 SKILL.md frontmatter 中可选声明：

```yaml
metadata:
  combinator:
    phases: [analysis, generation]  # 支持哪些阶段
    triggers: [优化, 重构]          # 触发关键词
    conflicts: [other-skill]        # 不能组合的 skill
```

**推断逻辑**：无声明时，从 description 和 skill name 自动推断 phases + triggers。

## 核心接口

### 1. 发现（Discover）

```python
def discover(task: str) -> list[tuple[skill_name, score]]:
    # 中英文混合分词：英文按\w+，中文按 bigram（2-gram）
    # 三级匹配得分：
    #   - trigger 英文词重叠 × 2
    #   - trigger 中文 bigram 重叠 × 1
    #   - phase signal bonus（analysis/optimize 任务 → analysis skill +3）
    # 返回按得分降序排列
```

### 2. 排序（Sequence）

```python
def sequence(skills: list[skill_name], task: str) -> list[skill_name]:
    # Phase 拓扑排序：analysis(0) → planning(1) → generation(2)
    #   → execution(3) → validation(4) → integration(5)
    # 同 phase 按 discover 得分排列
    # integration 排最后（最高层）
```

### 3. 组合（Compose）

```python
def compose(skills: list[skill_name], task: str) -> dict:
    return {
        "chain": [...],           # 顺序排列的 skill 名
        "phases": [...],          # 对应 phase
        "reasoning": "...",      # 为什么这样组合
        "conflicts_resolved": [],
    }
```

### 4. 验证（Validate）

```python
def validate(chain: list, task: str) -> dict:
    # 检查 phase 链是否有逆向（如 validation → analysis）
    # 返回 {valid, issues, recommendation}
```

## Registry

注册表位置：`~/.hermes/.skill_registry.json`

自动从所有 SKILL.md 推断，包含 188 skills 的 phases/triggers。

**重建命令：**
```bash
python3 ~/.hermes/scripts/skill_registry.py
```

**脚本位置**：`~/.hermes/skills/system/skill-combinator/scripts/pipeline.py`

**运行方式：**
```bash
python3 ~/.hermes/skills/system/skill-combinator/scripts/pipeline.py "多skill协作任务"
```

**关键实现细节（已修复的 bug）：**
1. **中文分词**：必须用 bigram（2-gram），否则 `re.findall(r'\w+', ...)` 把整句中文当一个 token，导致中文任务永远匹配不上
2. **Parent 去重**：所有 skill-* 的 parent 都是 None，直接用 None 去重会只剩 1 个；正确做法是用 skill 名前两段（如 `skill-audit`）做 category
3. **integration 排序**：phase index = 5（最高），拓扑排序时会排在最后——这是正确的
4. **Hidden 目录**：glob `**/SKILL.md` 时要排除 `.` 开头的目录，但 `.hermes` 不是 hidden

## Phase 覆盖

| Phase | 数量 | 代表 Skill |
|-------|------|----------|
| analysis | 11 | code-review-expert, metacognition-auditor |
| validation | 5 | test-driven-development, skill-audit |
| generation | 4 | songwriting-and-ai-music |
| planning | 3 | plan, checklist-manager |
| integration | 1 | skill-orchestrator |
| execution | 167 | 大多数 skill |

## 组合模式

### 模式 A：分析 → 生成
```
metacognition-auditor (analysis) 
  → prompt-engineering (generation)
```

### 模式 B：分析 → 执行 → 验证
```
code-review-expert (analysis)
  → coding-agent (execution)  
  → test-driven-development (validation)
```

### 模式 C：规划 → 执行
```
plan (planning)
  → coding-agent (execution)
```

## 冲突解决

当两个 skill 互相冲突时：
1. 保留 phase 更高级的（analysis > generation > execution）
2. 或要求用户确认

## 使用方式

激活后直接调用 `discover(task)` 分析任务，返回候选 skills 和组合方案。

## Pitfalls

- **推断误差**：自动推断不准确时，在 SKILL.md 加显式声明
- **Phase 模糊**：多数 skill 默认 execution，可能误匹配 planning
- **过度组合**：不是所有任务都需要多 skill，单 skill 能解决的不强行组合
