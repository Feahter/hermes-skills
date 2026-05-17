# Memory Palace — 三层路由架构

> 2026-05-13 建立。源自 Hermes 记忆系统重构。
> 架构原则：记忆系统的 Index → Load → Reference 三层模型 = Skills 三层模型。

---

## 核心概念

Memory Palace 是一种记忆文件路由架构，核心思想：

```
Layer 1: Index（~2KB，始终注入）
  → 路由表：关键词 → 文件路径
  → 描述"什么时候需要这份记忆"

Layer 2: Load（按需加载，~5KB/次）
  → 被 Index 路由命中的文件
  → 内容正文，按 section 组织

Layer 3: Reference（显式引用，~10KB+）
  → diary/、深层 evolution/ 文件
  → 仅 agent 显式请求时加载
```

**类比 Skills 三层模型：**

| 记忆层 | Skills 对应 | 注入时机 |
|--------|-----------|---------|
| Index（路由表）| `available_skills` 列表 | 始终，全员付租 |
| Load（内容）| SKILL.md body | 关键词触发付租 |
| Reference（深层）| `references/` | 显式引用时付租 |

---

## 适用场景

**适合用 Memory Palace 的情况：**
- 单一 `.md` 文件超过 5KB 且覆盖多个不相关主题
- 不同 session 需要加载完全不同的记忆子集
- 记忆文件有明显的"冷热分层"（高频 vs 低频访问）

**不适合的情况：**
- 所有内容都高频使用 → 保持单文件更简单
- 内容之间高度耦合 → 拆分反而破坏上下文

---

## 实施步骤

**Step 1: Inventory — 列出所有现有记忆文件**
```bash
ls memory/
# 读每个文件，确认内容边界
```

**Step 2: 分类 — 三层归属**
```python
# 始终需要 → Layer 1 Index
# 关键词触发 → Layer 2 Load
# 按日期/显式引用 → Layer 3 Reference
```

**Step 3: 创建路由层（_index.md）**
- 文件名：`_index.md`（约定优于配置）
- 内容：机器可读路由表（关键词 → 文件路径）
- 大小目标：< 5KB

**Step 4: 拆分现有文件**
- 从原单文件提取各 section → 独立文件
- 补全缺失的专题文件（如 key-learnings.md）
- 旧文件加废弃声明头部

**Step 5: 归档而非删除**
- 过时内容 → `docs/archive/` 或文件内 `<!-- deprecated -->`
- 不直接删除：历史上下文有价值

---

## 文件命名约定

```
memory/
├── _index.md              ← 路由层入口（必须）
├── system/                ← Layer 1: Identity & System
│   ├── SOUL.md
│   └── AGENTS.md
├── evolution/             ← Layer 2: Knowledge沉淀
│   ├── skills-knowledge.md
│   ├── key-learnings.md
│   └── robobun.md
├── tasks/                 ← Layer 2: 工具专项
│   └── browser-rules.md
├── research/              ← Layer 2: 研究归档
│   └── *.md
└── diary/                 ← Layer 3: 时间索引
    └── YYYY-MM-DD.md
```

**命名原则：**
- `_index.md` = 路由入口（不可缺）
- `system/` = Layer 1，始终注入
- `evolution/` = 随时间积累的知识层
- `diary/` = 时间序列，单日单文件
- `tasks/` = 工具/项目专项

---

## 路由表示例

```markdown
## 路由表

| 文件 | 触发关键词 | Load Policy |
|------|-----------|-------------|
| `memory/system/SOUL.md` | 始终 | ALWAYS |
| `memory/evolution/skills-knowledge.md` | skill, 三层, gotcha | OFTEN |
| `memory/evolution/key-learnings.md` | 坑, 经验, lesson | ON-DEMAND |
| `memory/diary/YYYY-MM-DD.md` | "记得那天" | ON-DEMAND |

## 机器可读路由

```yaml
skills:      [skill, 三层, gotcha, SKILL.md]
learnings:   [坑, 经验, lesson, 过去, mistake]
diary:       [记得那天, 上次, 2026-04-21]
```
