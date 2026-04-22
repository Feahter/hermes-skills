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
def discover(task: str) -> list[Skill]:
    """根据任务文本匹配最相关的 skills"""
    # 匹配 triggers（关键词重叠计分）
    # 匹配 phases（任务阶段 × skill 阶段覆盖度）
    # 返回排序后的候选列表
```

### 2. 排序（Sequence）

```python
def sequence(skills: list[Skill], task: str) -> list[Skill]:
    """确定组合顺序，拓扑排序"""
    # 优先：analysis → planning → generation → execution → validation
    # 同 phase 按 priority
    # 冲突检测：有 conflicts 关系的skill不放相邻
```

### 3. 组合（Compose）

```python
def compose(skills: list[Skill], task: str) -> dict:
    """返回组合方案"""
    return {
        "chain": [...],           # 顺序排列的 skill 名
        "reasoning": "...",      # 为什么这样组合
        "conflicts_resolved": [], # 解决了哪些冲突
    }
```

## Registry

注册表位置：`~/.hermes/.skill_registry.json`

自动从所有 SKILL.md 推断，包含 188 skills 的 phases/triggers。

重建命令：
```bash
python3 -c "
import sys; sys.path.insert(0, '~/.hermes/scripts');
from skill_registry import build; build()
"
```

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
