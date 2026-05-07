---
name: hermes-agent-testing
description: 测试 hermes-agent 内部方法（AIAgent 纯逻辑方法）的正确方式。适用场景：想对 run_agent.py 内部方法写单元测试，但直接实例化 AIAgent 会因 API key / provider 检查失败。
metadata:
  combinator:
    phases: [testing]
    triggers:
      - 测试 AIAgent
      - test run_agent
      - 单元测试 hermes agent
      - _should_replan 测试
      - verify-replan 测试
---

# Testing hermes-agent Internal Methods

## Problem

`AIAgent.__init__` 在实例化时会检查：
1. `OPENAI_API_KEY` / provider 配置
2. 调用 `hermes_cli.config.load_config()`
3. 可能触发网络探测

直接 `AIAgent(model=..., provider=...)` 会抛出 `RuntimeError: Provider 'openai' is set in config.yaml but no API key was found`。

## Solution: Mock Pattern

参考 `tests/run_agent/test_run_agent.py` 的 `_make_agent` fixture：

```python
from unittest.mock import MagicMock, patch
from run_agent import AIAgent

def _make_tool_defs(*names: str) -> list:
    return [
        {
            "type": "function",
            "function": {
                "name": n,
                "description": f"{n} tool",
                "parameters": {"type": "object", "properties": {}},
            },
        }
        for n in names
    ]

def _make_agent(**overrides):
    with (
        patch("run_agent.get_tool_definitions", return_value=_make_tool_defs("terminal", "web_search")),
        patch("run_agent.check_toolset_requirements", return_value={}),
        patch("run_agent.OpenAI"),
        patch("hermes_cli.config.load_config", return_value={"agent": {}}),
    ):
        agent = AIAgent(
            model="openai/gpt-4.1",
            api_key="test-key-1234567890",
            base_url="https://openrouter.ai/api/v1",
            quiet_mode=True,
            skip_context_files=True,
            skip_memory=True,
            **overrides,
        )
        agent.client = MagicMock()
        return agent
```

必须 mock 的 4 个：
- `run_agent.OpenAI` — 禁用真实 SDK 导入
- `run_agent.get_tool_definitions` — 避免工具注册
- `run_agent.check_toolset_requirements` — 避免工具集检查
- `hermes_cli.config.load_config` — 避免读取真实配置

## 访问内部方法

AIAgent 的 `_should_replan` / `_is_context_heavy` 等是实例方法，不是 `__init__` 的参数。

```python
agent = _make_agent()
result = agent._should_replan(messages_list)
```

## 设置内部状态

`_verify_enabled` 等在 `__init__` 内部设置，非构造参数：

```python
agent = _make_agent()
agent._verify_enabled = False  # 直接赋值
```

## 运行测试

hermes-agent 用 `pytest-xdist`（`pyproject.toml` 有 `addopts = "-m 'not integration' -n auto"`），无 venv 时会报 `pytest-xdist: unknown argument -n`：

```bash
source venv/bin/activate
python -m pytest tests/run_agent/test_verify_replan.py -v -o "addopts="
```

## Known Bug: _should_replan Negative Index

**Bug 位置**：`run_agent.py` ~line 4043

```python
# 错误（有负索引风险）
for i in range(len(messages) - 16, len(messages)):

# 正确
for i in range(max(0, len(messages) - 16), len(messages)):
```

当 `messages` 少于 16 条时，`len(messages) - 16` 为负数，触发 `IndexError`。

## 测试运行结果模式

- **9 failed**: `_verify_enabled` 作构造参数传入（不在 AIAgent 签名里）
- **5 passed, 4 failed**: 大部分测试正确，但 `_should_replan` 的 `range` 负索引 bug 导致部分消息少的测试失败
- **9 passed**: 所有正常

## 示例：测试 _should_replan

```python
def test_error_density_triggers_at_3_hits():
    agent = _make_agent()
    msgs = [
        {"role": "user", "content": "do something"},
        {"role": "assistant", "content": "calling tool", "tool_calls": [{"type": "function", "name": "read_file"}]},
        {"role": "tool", "content": "PermissionError denied"},
        {"role": "assistant", "content": "next", "tool_calls": [{"type": "function", "name": "patch"}]},
        {"role": "tool", "content": "FileNotFoundError: not found"},
        {"role": "assistant", "content": "next", "tool_calls": [{"type": "function", "name": "write_file"}]},
        {"role": "tool", "content": "Exception: timeout"},
    ]
    result = agent._should_replan(msgs)
    assert result is not None
    assert "Error keywords" in result
```
