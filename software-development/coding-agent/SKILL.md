---
name: coding-agent
description: >
  Autonomous coding execution engine — use whenever someone asks to code, build, create, implement,
  refactor, debug, fix, optimize, or ship software. Handles everything from one-liners to full
  application scaffolds. Triggers on: "帮我写代码/写个/写一个/做一个小工具/实现/开发/写个脚本/
  代码有问题/调试/bug/修复/重构/优化性能/迁移代码/搭建项目/初始化项目/add feature/
  implement/build this/create a script/write function/fix this bug/refactor/optimize".
  Not for: reading docs, explaining concepts, or answering questions — only for actually producing code.
triggers:
  - "帮我写代码"
  - "写个"
  - "写一个"
  - "做一个小工具"
  - "实现"
  - "开发"
  - "写个脚本"
  - "代码有问题"
  - "调试"
  - "有bug"
  - "修复"
  - "重构"
  - "优化性能"
  - "迁移代码"
  - "搭建项目"
  - "初始化项目"
  - "add feature"
  - "implement"
  - "build this"
  - "create a script"
  - "write function"
  - "fix this bug"
  - "refactor"
  - "optimize"
  - "帮我写"
  - "帮我做"
  - "能不能写"
  - "能不能做个"
  - "能帮我写"
  - "能帮我做"
  - "帮我生成"
  - "生成代码"
  - "写个函数"
  - "写个类"
  - "写个组件"
  - "写个工具"
  - "自动化"
  - "写个脚本"
  - "跑不起来"
  - "报错"
  - "出错了"
  - "不对"
  - "有问题"
  - "不工作"
metadata: {"clawdbot":{"emoji":"🧩","requires":{"anyBins":["claude","opencode"]}}}
pipeline:
  root: pipeline/
  state: .state/
---

# Coding Agent — 执行管道

> 当前支持：**Claude Code**（✅ 已安装 2.1.88）、**OpenCode**（✅ 已安装 1.3.0）

---

## 什么时候用这个 Skill

**毫不犹豫地用，当你听到：**
- "帮我写个..." / "帮我做..." / "帮我生成..."
- "能不能写个..." / "能不能做个..."
- "这个功能帮我实现一下"
- "代码跑不起来" / "报错了" / "有bug"
- "帮我调试一下" / "帮我看看哪里有问题"
- "重构一下这段代码"
- "优化一下性能"
- "搭建一个项目" / "初始化一个项目"
- "写个脚本自动化..."
- "把这个从X迁移到Y"
- "帮我在XXX基础上开发..."
- 任何提到具体编程语言 + "写/做/实现/开发"

**不用这个 Skill，当：**
- 只是问"怎么写"而不需要实际产出代码 → 用普通对话
- 只是读文档/查资料 → 用 web_search / web_fetch
- 只是解释代码逻辑 → 用普通对话
- 只是问概念 → 用普通对话

**一句话：** 要代码产出就用 coding-agent，别在普通对话里让它"试着写写"。

---

## 任务路由决策（必读）

根据任务复杂度选择执行方式，**只看这一个表就够了**：

| 任务类型 | 特征 | 执行方式 | 示例 |
|---------|------|---------|------|
| **简单** | 单文件、< 60s、无外部依赖 | `exec` 前台 | 写个脚本、修个 bug、生成一个文件 |
| **中等** | 3-5 文件、1-5 min、可能装依赖 | `exec background:true` | 初始化项目、实现一个模块、自动化脚本 |
| **复杂** | 5+ 文件、> 5 min、需要多轮迭代 | `sessions_spawn` 子 session | 大型重构、框架迁移、全栈功能开发 |
| **调试** | 需要读代码+分析+多次尝试 | `sessions_spawn` 子 session | 偶现 bug、性能分析、日志追踪 |

**判断流程**：任务涉及 5+ 文件？→ 子 session。否则需要装依赖或后台跑？→ exec background。否则 → exec 前台。

### ⚠️ 源码超量处理原则（强制）

**源码/文件总 tokens 超过 100K 时，禁止直接注入原始内容到上下文**：
1. 分段读取（每次 ≤200 行）：`exec cat file | head -200 | tail -100`
2. 本地逐段提炼要点（Python 预处理脚本）
3. 各段摘要合并后再输入 LLM
4. 触发条件：检测到文件 > 100K tokens 时自动触发此流程

---

## 架构

```
coding-agent/
├── pipeline/
│   ├── run-task.sh          # 启动任务（bash + Claude Code CLI）
│   ├── check-progress.sh    # 监控进度（调用 check-progress.py）
│   ├── check-progress.py    # Python 版状态解析（处理 JSON）
│   ├── collect-results.sh   # 收集结果（调用 collect-results.py）
│   ├── collect-results.py   # Python 版：git diff + JSON 报告
│   ├── verify.sh            # 验证产出
│   └── list-sessions.sh     # 列出所有会话
├── .state/
│   ├── progress/            # 每个会话的 JSON 状态
│   ├── results/             # 收集后的完整 JSON 报告
│   ├── logs/                # 原始 stdout/stderr 日志
│   ├── pids/                # 进程 PID
│   ├── context.md           # 管道状态
│   └── learnings.md         # 执行积累
└── SKILL.md
```

**依赖**：`claude`（Claude Code CLI 2.1.88 ✅）、`opencode`（1.3.0 ✅）

---

## 快速开始

### 1. 启动一个编程任务

```bash
SKILL_DIR=~/.openclaw/workspace/skills/coding-agent

# 方式 A：exec（推荐，自动处理后台）
exec bash $SKILL_DIR/pipeline/run-task.sh \
  "为 ~/project/myapp 添加用户认证模块" \
  "$HOME/project/myapp"

# 方式 B：使用 sessions_spawn（OpenClaw 原生子 session）
# 见下方「子 Session 模式」
```

### 2. 监控进度

```bash
bash $SKILL_DIR/pipeline/check-progress.sh <session_id> [tail_lines]
# 例如
bash $SKILL_DIR/pipeline/check-progress.sh 1745112345-12345 50
```

### 3. 收集结果

```bash
# 会话完成后
bash $SKILL_DIR/pipeline/collect-results.sh <session_id>
# 输出：JSON 报告，含 git diff + 完整日志
cat $SKILL_DIR/.state/results/<session_id>.json
```

### 4. 验证产出

```bash
bash $SKILL_DIR/pipeline/verify.sh <session_id>
# 自动检查：git diff / package.json / Cargo.toml / Makefile
```

### 5. 列出所有会话

```bash
bash $SKILL_DIR/pipeline/list-sessions.sh [running|completed|all]
```

---

## OpenClaw 原生模式（推荐）

用 `exec` 工具直接调用，不需要子 shell：

```bash
exec workdir:$PROJECT_DIR background:true \
  command:"claude -p '你的编程任务' --output-format stream-json --no-session-persistence"
```

**关键参数**：
- `-p` — 非交互打印模式
- `--output-format stream-json` — 流式 JSON 输出
- `--no-session-persistence` — 不保存会话到磁盘
- `--permission-mode bypassPermissions` — 跳过确认（仅在可信目录）

---

## 子 Session 模式（复杂任务）⭐

对于需要多轮迭代的复杂任务，用 `sessions_spawn` 启动专用子 session。**这是处理复杂编程任务的标准方式。**

### 为什么需要子 Session

普通 exec 调用的局限：
- 单次执行，无法多轮自我修正
- 无法中途读取代码决定下一步
- 任务失败无法重试

子 Session 的优势：
- 独立上下文，可多次执行 exec
- 可读取和分析代码
- 支持多轮自我修正
- 可访问完整工具集（不只是 exec）

### 标准调用方式

```bash
sessions_spawn(
  task="对 $PROJECT_DIR 进行以下改动：$TASK_DESCRIPTION",
  runtime="subagent",
  mode="session"
)
```

### 子 Session 任务模板

当需要子 session 时，使用以下模板描述任务：

```
## 目标
[具体要实现的功能或修复的问题]

## 项目上下文
- 项目路径：$PROJECT_DIR
- 技术栈：[如 Node.js + Express, Python + FastAPI 等]
- 现有文件：[相关文件列表]
- package.json / requirements.txt 存在：是/否

## 约束
- 不要删除现有功能（如果有）
- 如果涉及依赖，先检查 package.json / requirements.txt
- 完成后运行测试验证

## 验收标准
- [ ] [具体可检查的标准 1]
- [ ] [具体可检查的标准 2]
```

### 与主 Session 的协作模式

```
主 Session                          子 Session
    |                                  |
    |-- sessions_spawn -------------> |
    |    (task=完整任务描述)            |
    |                                  |--- 执行多次 exec
    |                                  |--- 读取代码
    |                                  |--- 写文件
    |                                  |--- 运行测试
    |                                  |
    |<-------- 子 Session 完成推送 -------|
    |    (包含 git diff + 验证结果)     |
    |                                  |
```

### 子 Session 生命周期管理

```bash
# 查看子 session 状态
bash $SKILL_DIR/pipeline/list-sessions.sh running

# 查看某个 session 的日志
cat $SKILL_DIR/.state/logs/<session_id>.log

# 强制终止卡住的 session
kill $(cat $SKILL_DIR/.state/pids/<session_id>.pid)
```

### 子 Session 典型场景

1. **大型功能开发**（超过 30 分钟工作量的任务）
   → 拆分成子 session，避免主 session 超时

2. **多文件重构**（涉及 5+ 文件）
   → 子 session 有完整上下文，跨文件修改更安全

3. **测试驱动开发**（TDD）
   → 子 session 内可运行多次测试-修改循环

4. **迁移项目**（如 React → Vue）
   → 子 session 可逐步验证每个模块

---

## Session 状态机

```
pending → running → completed
                      ↘ failed
```

### 状态说明

| 状态 | 含义 | 处理方式 |
|------|------|---------|
| pending | 任务已创建，还没启动 | 等待或检查 pid |
| running | 执行中 | 监控进度或等待完成 |
| completed | 正常完成 | 收集结果并验证 |
| failed | 执行失败 | 查看日志，分析原因，重试或手动修复 |

### 状态文件位置

```
.state/progress/<session_id>.json   # 实时状态
.state/results/<session_id>.json    # 完成后的完整报告
.state/logs/<session_id>.log        # 原始日志
.state/pids/<session_id>.pid        # 进程 PID
```

---


## 失败处理（Best Practices）

> 详细内容 → `references/troubleshooting.md`

---

## 超时处理（Best Practices）

> 详细内容 → `references/timeout-handling.md`

---

## 结果验证（Standard Procedure）

> 详细内容 → `references/result-verification.md`

---

## 执行参数参考

> 详细内容 → `references/execution-params.md`

---

## 常见使用场景示例

> 详细内容 → `references/usage-examples.md`

---

## Learnings（积累）

每次编程任务后，将结果记录到 learnings：

→ 见 `.state/learnings.md`


---

