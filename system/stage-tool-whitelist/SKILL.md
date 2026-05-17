---
name: stage-tool-whitelist
description: |
  Per-turn tool whitelisting + StateWright 风格状态机 guardrails。
  基于 pre_llm_call 实现 stage 检测 + 工具过滤，
  移植自 statewright 的核心能力：Guard 条件求值、Transition 解析、
  Command allowlist、Edit line/file caps。
  v0.3: 新增 StateWright 增强。
hooks:
  - pre_llm_call
  - post_tool_call
  - on_session_reset
triggers:
  - "stage tool whitelist"
  - "per-turn tool filter"
  - "decision fatigue plugin"
  - "阶段工具白名单"
  - "statewright"
category: system
version: 0.3.0
---

# Stage Tool Whitelist（StateWright 增强版）

Per-turn tool restriction + deterministic guardrails，基于 Hermes hook 机制实现。

**核心价值**：把概率性防护（依赖模型听从指令）变成确定性防护（白名单直接拒绝）。

**移植来源**：Statewright（Rust 状态机引擎）的核心算法，
crates: engine/src/guard.rs、transition.rs、tool_enforcer.rs。

---

## 架构

```
user message
    ↓
stage_machine.detect_stage()  ← 关键词匹配
    ↓
[可选] workflow state machine  ← StateWright workflow
    ↓
pre_llm_call → {"context": stage info + guardrails, "tools": [whitelist]}
    ↓
run_agent.py 过滤 api_kwargs["tools"]（API 层软过滤）
    ↓
post_tool_call → command_filter / edit_enforcer（检测层）
    ↓
下一轮 pre_llm_call → 注入边界警告
```

**注意**：工具过滤是 API 层软过滤（api_kwargs 过滤工具列表）。
command_filter / edit_enforcer 是 post-hook 检测层，警告注入 context。

---

## 两套模式

### 模式 1：Stage 模式（默认）

基于关键词的阶段检测 + 固定白名单。

| Stage | 触发关键词 | 工具 | Command Allowlist | Max Edit Lines |
|-------|-----------|------|------------------|----------------|
| PLAN | 计划/方案/分析/拆解/架构 | read_file, search_files, plan... | **BLOCKED** | **0** |
| SEARCH | 搜索/查找/调研/research | web_search, web_extract... | **BLOCKED** | **0** |
| CODE | 写代码/debug/实现 | read_file, write_file, patch, terminal... | patch, sed -i, git diff | 50 |
| REVIEW | 测试/验证/check | terminal, read_file, execute_code... | pytest, cargo test, npm test | 20 |
| WRITE | 写文档/报告/总结 | read_file, write_file, patch... | — | 100 |
| CHAT | 其他 | 无限制 | 无限制 | 无限制 |

### 模式 2：Workflow 模式（激活后）

StateWright JSON 状态机，完整 guard 条件 + transition。

激活方式（skill 命令）：
```
/skill stage-tool-whitelist activate bugfix  ← 激活 bugfix workflow
/skill stage-tool-whitelist activate tdd     ← 激活 TDD workflow
/skill stage-tool-whitelist deactivate       ← 关闭 workflow
```

内置 workflow：

**bugfix**：
```
planning → implementing → testing → review → completed
                         ↓
                  (guard: tests_passed)
```

**TDD**：
```
write_test → implementing → testing → review
                                    ↓
                              (guard: all_tests_pass)
```

---

## Guard 条件（移植自 statewright_engine guard.rs）

Guard 是确定性布尔条件，用于控制 transition 是否能执行。

| Op | 说明 | 示例 |
|----|------|------|
| eq | 等于 | `{"field": "status", "op": "eq", "value": "pass"}` |
| neq | 不等于 | `{"field": "error", "op": "neq", "value": ""}` |
| gt / gte / lt / lte | 数值比较 | `{"field": "count", "op": "gt", "value": 0}` |
| exists / not_exists | 字段存在 | `{"field": "email", "op": "exists"}` |
| in | 在数组中 | `{"field": "status", "op": "in", "value": ["draft", "pending"]}` |
| contains | 字符串包含 | `{"field": "name", "op": "contains", "value": "foo"}` |

**Guard 求值示例**（在 workflow transition 时）：
```json
{
  "on": {
    "PASS": {"target": "review", "guard": "tests_passed"}
  }
}
// tests_passed = {"field": "test_result", "op": "eq", "value": "pass"}
```

---

## Command Allowlist（移植自 statewright tool_enforcer.rs）

**前缀匹配**：白名单 `["pytest", "cargo test"]` 允许：
- `pytest tests/`
- `pytest -xvs`
- `cargo test --lib`
- `cargo test`

**无条件 Block**：
- `rm -rf` / `rm -rf /`
- `dd if=` / `mkfs` / `fdisk`
- Fork bomb 模式
- `| sh` / `curl ... | sh`
- `eval()` / `exec()` / `__import__()` 在代码内容中

**Shell 内建命令总是允许**：`cd`, `echo`, `export`, `source`, `pwd`, `ls`, `history`

---

## Edit Caps（移植自 statewright state def）

| 字段 | 说明 |
|------|------|
| `max_edit_lines` | 单次 edit 的行数上限（超过则警告）|
| `max_files_per_state` | 单个状态内允许编辑/创建的文件数 |

---

## Hooks

### `pre_llm_call`
- 检测 stage（关键词 + sticky）
- 激活 workflow 时注入完整状态机 context
- 注入边界警告
- 支持 workflow transition（"完成了" → DONE, "测试通过" → PASS）

### `post_tool_call`
- 检查工具名白名单
- 检查 terminal 命令 allowlist（前缀匹配）
- 检查 patch/write_file 的 edit 行数
- 记录文件编辑用于 max_files 追踪
- 队列警告到下一轮

### `on_session_reset`
- 清除 session state
- 清除 workflow state

---

## 文件结构

```
scripts/
  guard_engine.py        # Guard 条件求值器（无 LLM 依赖）
  transition_resolver.py # Transition 解析 + context patch
  workflow.py            # Workflow 加载/状态机管理 + 内置模板
  command_filter.py      # Command allowlist 前缀匹配 + 危险命令检测
  edit_enforcer.py       # Edit 行数/file caps 检查
  whitelist_config.py    # Stage → tools/commands/lines mapping
  stage_machine.py       # Stage 检测 + sticky
  pre_llm_call.py        # 主 hook + workflow activation
  post_tool_call.py      # 边界检测 hook
```

---

## 测试

**⚠️ Hooks 在 `-z` 模式下不激活。** 需要真实 session 测试。

```bash
source venv/bin/activate && hermes --yolo

# 在 session 内：
帮我写一个快速排序
# → CODE stage，browser_navigate 被过滤

# 测试 command allowlist（REVIEW 阶段）：
pytest tests/  # 允许
rm file.txt   # 被 block，警告注入

# 测试 workflow：
/skill stage-tool-whitelist activate bugfix
# → planning 阶段，编辑功能 BLOCKED
```

---

## 核心实现

**API 层过滤**（run_agent.py ~12269-12279）：
```python
if getattr(self, "_hook_tools_restriction", None):
    _allowed = set(self._hook_tools_restriction)
    _orig_tools = api_kwargs.get("tools") or []
    api_kwargs["tools"] = [
        t for t in _orig_tools
        if t.get("function", {}).get("name", "") in _allowed
    ]
```

**局限性**：这是软过滤（api_kwargs 层面），
不是硬过滤（协议层）。模型仍可能生成 tool call，
但 call 出去时会被过滤为空。

真正的硬过滤需要 core 改动（目前无计划）。
