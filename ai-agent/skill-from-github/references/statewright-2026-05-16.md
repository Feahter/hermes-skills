# Statewright 研究归档

**日期：** 2026-05-16
**结论：** 状态机引擎对 Hermes 有参考价值；per-state tool whitelist 已有同类方案

---

## 一、项目核心定位

**Statewright** = 状态机 guardrails 系统，控制 AI coding agents 在不同阶段可用的工具。

核心价值主张：**"Agents are suggestions, states are laws."**

---

## 二、关键代码发现（必读）

### 2.1 架构分层

| 层 | 位置 | 说明 |
|----|------|------|
| Engine | `crates/engine/src/` | 纯 Rust 状态机引擎，无 LLM 依赖 |
| Agent | `crates/agent/src/` | LLM loop + tool enforcement |
| Orchestrator | `crates/agent/src/orchestrator.rs` | 子状态机嵌套调用 |

### 2.2 关键源文件

| 文件 | 核心发现 |
|------|---------|
| `types.rs` | StateDef 含 `allowed_tools` / `max_edit_lines` / `allowed_commands` / `max_files_per_state` / `blocked_env` |
| `guard.rs` | 确定性 guard 谓词（Eq/Exists/Contains 等），无 LLM 依赖 |
| `tool_enforcer.rs` | `enforce_tools()` 返回 `{ allowed, blocked, implicit_transition }`；Final state block 所有工具 |
| `executor.rs` | **Statewright 有自己的 LLM loop**（直接调 Ollama）；tool filtering 内建于 step() |
| `orchestrator.rs` | 子状态机嵌套执行，`AwaitingInvoke` → 运行子 → merge context → 回到父 |

### 2.3 Enforcement 层析

**README 说 MCP protocol layer hard enforcement，但实际：**

Executor 内部：
```rust
step(&mut self, client: &OllamaClient) {
    // 1. build prompt
    // 2. LLM call
    // 3. tool_enforcer.enforce_tools()  ← 应用层过滤
}
```

**结论：Statewright 是应用层过滤（自己的 executor loop 内），不是协议层。** 这和 Hermes 的 api_kwargs 过滤同属应用层，但 Statewright 在 LLM call 之前就过滤了 requested_tools，Hermes 在 api_kwargs 层面过滤 tools 参数。

---

## 三、Statewright vs Hermes 对比

| 维度 | Statewright | Hermes (stage-tool-whitelist) |
|------|------------|------------------------------|
| 状态机定义 | JSON DSL + Rust engine | Hook skill（关键词匹配）|
| 阶段检测 | deterministic | 关键词匹配 |
| 工具过滤 | 内建于 executor loop | pre_llm_call hook → api_kwargs 过滤 |
| Guard 条件 | 内置（Eq/Exists/Contains 等）| 无（只有 whitelist）|
| 子状态机 | orchestrator 支持嵌套 | 无 |
| Command allowlist | `allowed_commands` prefix match | 无 |
| Edit caps | `max_edit_lines` | 无 |
| 研究结果 | 2/10 → 10/10（小样本）| 未验证 |

---

## 四、对 Hermes 的价值评估

| 发现 | 价值 |
|------|------|
| **确定性 guard 模式** | 高：无需 LLM 做决策，pure predicate |
| **Orchestrator 子状态机** | 中高：嵌套任务分解有参考价值 |
| **Command allowlist + edit caps** | 高：实用的增量 guardrail |
| **Stage detection 方法** | 低：关键词匹配 Hermes 已有 |
| **Per-state whitelist 机制** | 低：stage-tool-whitelist 已实现 |

---

## 五、未深入的方向（可继续）

1. **Guard 模式的 Hermes 实现**：在 `stage-tool-whitelist` 里加确定性条件判断（不依赖 LLM）
2. **Orchestrator 子状态机**：Hermes 的 delegate_task 已有类似能力，但无状态机封装
3. **Command allowlist**：在 whitelist skill 里加 `allowed_commands` 支持

---

## 六、关键教训

1. **代码先于 README**：Statewright README 说"MCP protocol layer"，但代码里是应用层过滤
2. **enforcement 测试要用真实 session**：`hermes -z` 不激活 hooks
3. **Enforcement 强度分类**：协议层 > 应用层（LLM call 前）> 应用层（api_kwargs）
