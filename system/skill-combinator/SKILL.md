---
name: skill-combinator
description: Skills 组合涌现引擎 — 根据任务特征自动发现、排序、组合 skills。触发：多 skill 协作需求、复杂任务分解、技能选型决策。
version: 1.1.0
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

**推断逻辑**：无声明时，从 skill name 和 triggers 推断 phases。

## 核心接口

### 1. 发现（Discover）

```python
def discover(task: str) -> list[tuple[skill_name, score]]:
    # 中英文混合分词：英文按 \w+，中文用 jieba
    #
    # 匹配顺序（第一个命中即退出）：
    #   1. audit skill（task 含 skill+analysis）→ +6
    #   2. prompt skill（task 含 prompt）→ +5
    #   3. skill combinator（task 含 skill+multi）→ +5
    #   4. analysis skill（name 含 analysis）→ +3
    #   5. skill orchestration 类 → +2
    #   6. coding/data 类（task 含 code/python/data）→ +3
    #   7. optimize/improve 类 → +2
    #
    # 无 trigger 匹配时，直接用 keyword-in-name 兜底
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

## 验证结果（v5 pipeline）

| Task | 预期 | 结果 | 首位 Skill |
|------|------|------|-----------|
| 分析 skill 系统 | skill-audit 首位 | ✅ | skill-audit |
| 写股票数据分析脚本 | coding/data 类 | ✅ | neodata-financial-search |
| prompt 优化方法 | prompt-engineering 首位 | ✅ | prompt-engineering |
| 多 skill 协作研究 | skill-combinator 首位 | ✅ | skill-combinator |

## 关键实现细节（已修复的 bug）

1. **中文分词**：必须用 `jieba`，`re.findall(r'\w+', ...)` 不分中文
2. **Parent 去重**：所有 `skill-*` 的 parent 都是 None，正确做法是用 skill 名前两段（如 `skill-audit`）做 category
3. **integration 排序**：phase index = 5（最高），拓扑排序时排在最后——正确
4. **Fallback 太 aggressive**：v2/v3 的 fuzzy phase bonus（is_analysis → 所有含 audit 的 skill +6）会误推无关 skill；v5 改用精准 keyword-in-name
5. **Hidden 目录**：glob `**/SKILL.md` 时要排除 `.` 开头的目录

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
