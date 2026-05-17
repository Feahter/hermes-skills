---
name: deepseek-delegation
description: |
  通过 tmux + deepseek-tui 向 DeepSeek 分配任务。
  适用：调研、长文草稿、批量操作、简单编码、代码阅读。
  
trigger:
  - "分配给 deepseek"
  - "交给 deepseek"
  - "发给 deepseek"
  - "让 deepseek 做"
  - "委托 deepseek"
---

## 双模型策略

| 模型 | 用途 | 场景 |
|------|------|------|
| **deepseek-v4-pro** | 顾问模式 | 架构设计、高难问题、复杂决策、编程问题深度分析 |
| **deepseek-v4-flash** | 批量模式 | 调研、长文草稿、简单编码、批量操作 |

> v4-pro 用来处理"需要动脑子的"，v4-flash 用来处理"需要动手的"。

---

## 模板库

### T1：调研任务

```
请帮我调研「{topic}」，输出结构如下：

1. 核心概念（3句话内）
2. 主流方案/产品对比（表格形式）
3. 适用场景
4. 关键风险
5. 参考链接（3-5条）

要求：结论优先，避免废话。
```

### T2：长文草稿

```
请帮我写一篇关于「{topic}」的文章，结构如下：

- 标题
- 开篇钩子（1段）
- 正文（3-4个观点，每点1-2段）
- 结尾升华（1段）

风格：{style}
字数：{word_count}
受众：{audience}
```

### T3：代码阅读理解

```
请分析以下代码片段（文件：{filename}），回答：

1. 这个模块的核心功能是什么？
2. 关键函数及其作用
3. 可能的 bug 点或性能问题
4. 代码风格评价（简洁/可读/健壮）

---
{code_snippet}
---
```

### T4：简单编码任务

```
任务：{task_description}

要求：
- 语言：{language}
- 不要过度设计
- 附简要注释
- 输出完整可运行代码
```

### T5：多选项对比

```
请对比「{A}」和「{B}」，从以下维度打分（1-10）：

| 维度 | A | B |
|------|---|---|
| 易用性 |   |   |
| 性能   |   |   |
| 生态   |   |   |
| 维护性 |   |   |
| 成本   |   |   |

给出推荐结论及理由。
```

### T6：架构咨询（顾问模式）

```
我遇到一个架构问题，请帮我分析：

背景：
{background}

约束：
- {constraint1}
- {constraint2}

当前方案：
{current_approach}

我的困惑/问题：
{question}

请从以下几个角度分析：
1. 这个设计的问题在哪里？
2. 业界通常怎么解决？
3. 权衡取舍是什么？
4. 你会推荐什么方案？

要求：深入分析，不要蜻蜓点水。
```

### T7：代码/系统设计评审

```
请帮我评审以下设计/代码：

场景：{scenario}

设计/代码：
```
{code_or_design}
```

请从以下维度评审：
1. 正确性：逻辑是否有 bug
2. 健壮性：异常处理是否完善
3. 性能：瓶颈在哪里
4. 可维护性：后续改动成本
5. 安全性：风险点

给出结论和改进建议（如果有）。
```

---

## 模型切换

deepseek-tui 当前使用 **deepseek-v4-pro**（顾问模式）。

如需切换到 flash：
```
/model deepseek-chat  # 或 /model deepseek-v4-flash
```

---

## tmux 操作

```python
import subprocess

SESSION = "deepseek"

def send(prompt: str, confirm=False):
    """
    发送 prompt 到 deepseek-tui。
    confirm=True 时，表示这是 deepseek-tui 需要先写入 Draft 再确认发送的场景。
    如果 confirm=True，会发送 Ctrl+O 确认。
    """
    # 清空当前输入行（防止残留）
    subprocess.run(["tmux", "send-keys", "-t", SESSION, "C-c"], check=False)
    time.sleep(0.3)
    subprocess.run(["tmux", "send-keys", "-t", SESSION, prompt, "Enter"])
    if confirm:
        time.sleep(1)
        subprocess.run(["tmux", "send-keys", "-t", SESSION, "C-o"])  # confirm send

def send_and_confirm(prompt: str, wait: float = 15.0) -> str:
    """发送 Draft 并确认，等待回复"""
    send(prompt, confirm=True)
    time.sleep(wait)
    return parse_response(capture_raw())

def switch_model(model: str):
    """切换 deepseek-tui 模型"""
    subprocess.run(["tmux", "send-keys", "-t", SESSION, f"/model {model}", "Enter"])
    time.sleep(2)

def capture_last() -> str:
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", SESSION, "-p"],
        capture_output=True, text=True
    )
    return result.stdout

def wait_for_response(seconds=10) -> str:
    import time
    time.sleep(seconds)
    return capture_last()
```

---

## 使用流程

1. 调用 `tmux send-keys -t deepseek "<prompt>" Enter`
2. 等待 10-15 秒
3. `tmux capture-pane -t deepseek -p` 提取回复
4. 取 `╭─ ⚕ Hermes ─` 到 `╰───────────────────────────────────────────────────────────╯` 之间的内容
5. 返回给 Hermes

---

## 状态

- 创建时间：2026-05-16
- 验证：✅ 通路测试通过（2026-05-16）
- 模板数：5 个