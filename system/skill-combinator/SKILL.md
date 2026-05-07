---
name: skill-combinator
description: Skills 组合涌现引擎 — 根据任务特征自动发现、排序、组合 skills。触发：多 skill 协作需求、复杂任务分解、技能选型决策。
version: 1.7.0
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

## v7 核心改进

### 1. 反馈注入（核心智能机制）

用户纠正/确认组合后自动记录，下次 discover 时加权。

**反馈文件**：`~/.hermes/.skill_combinator_feedback.json`

```python
record_feedback(task="分析代码", chosen=["code-review-expert"], rejected=["skill-audit"])
# 效果：下次 discover "分析代码" 时，code-review-expert +0.5 分，skill-audit -0.5 分
```

**用法**：当用户纠正或确认 skill 组合时，模型调用 `record_feedback()` 记录。

### 2. 复杂度门槛（零开销优化）

| 条件 | 行为 |
|------|------|
| task 字符 < 35 + 含单 skill 关键词 | **直连**，不过 pipeline |
| 否则 | 正常三阶段 pipeline |

**单 skill 关键词映射**：
- `git` → `git`
- `github` → `github`
- `写代码` → `coding-agent`
- `写小说` → `novel-writing-sop`
- `ppt/幻灯片` → `html-ppt`
- `代码审查/code review` → `code-review-expert`
- `计划` → `plan`

### 3. Trigger Registry 化

Stage 1 硬编码 if-elif → `TRIGGER_STRATEGIES` 配置列表，可扩展免改代码：

```python
TRIGGER_STRATEGIES = [
    {"signals": ["分析", "audit", "检查"], "name_kw": ["audit"], "bonus": 6, "phase": "analysis"},
    {"signals": ["写", "代码", "python"], "name_kw": ["code", "coding"], "bonus": 3, "phase": "execution"},
    # 新策略直接加列表，不用改 if-elif
]
```

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

## 核心接口（v6 三阶段按需加载）

> 基于 Tony Gentilcore "Harness as Context Manager" 框架。
> 核心原则：**不加载不需要的，只有需要的那一刻才注入。**

### Stage 1：搜索索引（纯内存，无 I/O）

```python
def stage1_search_index(task: str, skills: dict, top_k: int = 20) -> list[tuple]:
    # 从 registry triggers/keywords 匹配
    # 不读文件，纯内存计算
    # 返回 top 20 候选，按相关性得分排序
```

### Stage 2：短列表 + 轻量描述（按 category 去重）

```python
def stage2_shortlist(matched: list[tuple], skills: dict, top_k: int = 6) -> list[dict]:
    # 按 category 去重，每类最多 2 个
    # 每个候选返回 {name, phase, summary} — 不加载 SKILL.md
    # 模型/用户选择加载哪几个
```

**输出示例：**
```
[analysis] skill-audit — AI Agent Skills 安全扫描器...
[execution] github — GitHub CLI 工作流... (truncated)
```

### Stage 3：按需加载完整 Schema（决定执行时才读文件）

```python
def stage3_load_schema(name: str, skills: dict) -> dict:
    # 只有模型决定执行某个 skill 时才调用
    # 读取完整 SKILL.md 内容（而非 registry cache）
    # 返回 {name, path, content, phase, triggers}
```

---

### 组合调用：`on_demand_discover(task)` → 一次完成三阶段

```python
result = on_demand_discover("帮我分析代码审查问题")
# result["stage1_candidates"]  — 搜索索引结果（top 20）
# result["stage2_shortlist"]  — 短列表（top 6，含 summary）
# 用 stage3_load_schema(name, skills) 按需加载完整 SKILL.md
```

**使用方式：**
```bash
# 标准模式（向后兼容）
python3 ~/.hermes/skills/system/skill-combinator/scripts/pipeline.py "分析代码审查"

# 按需模式（显示短列表）
python3 ~/.hermes/skills/system/skill-combinator/scripts/pipeline.py "分析代码审查" --on-demand
```

---

## 旧接口（v5，仍可用但推荐用 on_demand_discover）

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

自动从所有 SKILL.md 推断，包含 **204** skills 的 phases/triggers/description/summary。

**维护**：磁盘 skill 数量应与注册表一致。若不一致（常见于 skill 删除、插件嵌套、大小写问题），参见 `references/registry-maintenance.md`。

**技能清理工作流**：三阶段 audit → validate → execute 流程，参见 `references/skill-cleanup-workflow.md`。


> v6 registry 新增 `description`（全文）和 `summary`（一句话）字段，
> 支撑 Stage 2 短列表展示。

**脚本位置**：`~/.hermes/skills/system/skill-combinator/scripts/pipeline.py`

**运行方式：**
```bash
python3 ~/.hermes/skills/system/skill-combinator/scripts/pipeline.py "多skill协作任务"
```

## 验证结果（v7 pipeline）

| Task | 预期 | 结果 | 首位 Skill |
|------|------|------|-----------|
| 分析代码审查 | bypass 直连 | ✅ | code-review-expert |
| 帮我分析skill系统，给出优化建议，需要搜索GitHub找最佳实践 | 走 pipeline | ✅ | hv-analysis |
| github 搜索最佳实践 | bypass github | ✅ | github |
| 代码审查 | bypass 直连 | ✅ | code-review-expert |

**v7 新增验证**（2026-05-04）：
- 复杂度门槛：`"代码审查"` → bypass ✅，长任务 → pipeline ✅
- 反馈加权：`record_feedback()` → `apply_feedback()` +0.5/-0.5 ✅
- Word boundary：GitHub 不误匹配 git ✅
- Trigger registry：`TRIGGER_STRATEGIES` 列表可配置 ✅

## 关键实现细节（已修复的 bug）

1. **中文分词**：必须用 `jieba`，`re.findall(r'\w+', ...)` 不分中文
2. **Parent 去重**：所有 `skill-*` 的 parent 都是 None，正确做法是用 skill 名前两段（如 `skill-audit`）做 category
3. **integration 排序**：phase index = 5（最高），拓扑排序时排在最后——正确
4. **Fallback 太 aggressive**：v2/v3 的 fuzzy phase bonus（is_analysis → 所有含 audit 的 skill +6）会误推无关 skill；v5 改用精准 keyword-in-name
5. **Hidden 目录**：glob `**/SKILL.md` 时要排除 `.` 开头的目录
6. **v7 Word Boundary**：`"github"` 含 `"git"` 会误匹配，改用 `r'\b' + re.escape(kw) + r'\b'` 词边界匹配

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
- **反馈噪声**：反馈文件长期积累后 task_key 前缀匹配可能不准，可定期清理 `~/.hermes/.skill_combinator_feedback.json`
- **复杂度门槛误触发**：含多意图的短任务（如"写代码+测试"）会 bypass 成单 skill，可用长描述规避
- **Subagent 模型路由不验证**：`delegate_task` 的 `model` 参数不校验模型 ID 是否存在于 provider，若指定的 model ID 无效则静默降级到默认模型（实测：指定 `minimax-8b` 仍走了默认 MiniMax-M2.7）。测试高速模型需用确实存在于 provider 配置中的 model ID。
- **Highspeed 型号只在官方平台**：OpenRouter 不含 `minimax-*-highspeed` 型号（`minimax/minimax-m2.7-highspeed` 不存在），只有 MiniMax 官方 `api.minimaxi.com` 有。若要测 highspeed，需直接配 minimax provider，而非走 OpenRouter。
