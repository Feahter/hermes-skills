# Statewright 研究归档

**日期：** 2026-05-16
**结论：** 移植核心 Guard + Transition 算法；Executor/Orchestrator 不可移植

---

## 一、研究背景

目标：评估 Statewright 对 Hermes stage-tool-whitelist 的参考价值。

**Statewright 核心能力：**
- Rust 状态机引擎（状态定义 + transition + guard）
- Per-state tool whitelist（MCP 协议层硬过滤）
- Guard 条件（确定性布尔，无 LLM）
- Command allowlist / Edit caps / Env scoping
- Orchestrator 子状态机

---

## 二、关键发现

### 2.1 Enforcement 层差异（README vs 代码）

| 层级 | 位置 | Statewright | Hermes |
|------|------|-------------|--------|
| 协议层 | MCP 协议 | executor 内 enforcement，非 MCP 本身 | 无 |
| 应用层（LLM call 前）| api_kwargs | `enforce_tools()` 应用层过滤 | api_kwargs 过滤 |

**教训**：README 说"MCP protocol layer hard enforcement"，实际是 executor 内应用层过滤。

### 2.2 可移植性分类

| 优先级 | 模块 | 可移植性 | 原因 |
|--------|------|---------|------|
| P0 | Guard 条件求值 | 高 | 纯函数，无 LLM 依赖 |
| P0 | Transition 解析 | 高 | 确定性算法，JSON 驱动 |
| P1 | Command allowlist | 高 | 前缀匹配 + 危险命令黑名单 |
| P1 | Edit caps | 高 | 行数/file 计数检查 |
| P2 | Workflow JSON schema | 高 | 配置驱动 |
| P3 | Executor loop | 低 | 依赖 Statewright 自有的 LLM 控制流 |
| 不可移植 | Orchestrator 子状态机 | 低 | 架构差异过大 |
| 不可移植 | Ollama only | 0 | 违背 Hermes provider 抽象 |

### 2.3 核心价值

**确定性 enforcement**（vs Hermes 原有的概率性）：

```
研究数据：13.8GB 模型 2/10 → 10/10（提升 5 倍）
这不是模型变聪明了，是移除了概率性
```

---

## 三、移植结果

### 3.1 新增模块（5 个，~1480 行）

| 文件 | 功能 |
|------|------|
| `guard_engine.py` | 确定性条件求值（Eq/Neq/Gt/.../Contains）|
| `transition_resolver.py` | Transition 解析 + context patch |
| `workflow.py` | StateWright JSON 状态机 + 内置 bugfix/TDD |
| `command_filter.py` | Command allowlist 前缀匹配 + 危险命令黑名单 |
| `edit_enforcer.py` | Edit 行数/file caps 检查 |

### 3.2 测试结果

- Guard Engine: 10/10
- Transition Resolver: 7/7
- Command Filter: 15/15
- Edit Enforcer: 4/4
- Workflow (file cap): 5/5
- **总计：41/41，100%**

### 3.3 修复的问题

1. `python -m pytest` → 映射为 `pytest`（module runner 适配）
2. `python -c 'code'` → 直接拒绝（危险命令检测）
3. Shell builtin（ls/cat/head/tail）→ 无条件放行

---

## 四、未移植的部分

| 模块 | 原因 |
|------|------|
| Executor loop | Hermes 有自己的 run_agent.py 主循环，架构不兼容 |
| Orchestrator 子状态机 | 需要 Statewright 自有 LLM 控制流，Hermes 无法直接用 |
| Ollama 依赖 | 违背 Hermes 的 provider 抽象（支持多 provider）|

---

## 五、关键教训

### 教训 1：研究顺序

**错误**：README → 结论 → 代码验证（结论已固化）
**正确**：代码关键文件 → README 交叉验证 → 结论

Statewright 我在 README 层停留太久，导致对 enforcement 强度的判断有误。

### 教训 2：架构可行性先于代码量

最小改动方案在架构不可行时，成本是**完全重做**。

ContextEngine 接口不支持 per-tool-call hook → 方案 B 架构不可行，不讨论代码量。

### 教训 3：实验验证核心假设

方案 B 的核心假设（agent 理解 `[ref:node_id]`）需要先验证，再投入 400-600 行代码。

实验发现：工具必须在 schema 真实注册，描述无效。

---

## 六、对 Hermes 的后续价值

1. **Guard 条件**：确定性条件判断，Hermes 可用于 workflow transition 控制
2. **Command allowlist**：已有 command_filter.py，直接可用
3. **Edit caps**：已有 edit_enforcer.py，直接可用
4. **Workflow 模板**：bugfix / TDD 内置workflow，可直接激活

后续如需真正硬过滤（协议层），需 Hermes core 改动，非 skill 层面可解决。