## 执行参数参考

| 参数 | Claude Code | OpenCode |
|------|------------|---------|
| 非交互模式 | `-p "task"` | `opencode run "task"` |
| 输出格式 | `--output-format json` | 默认 JSON |
| 禁止持久化 | `--no-session-persistence` | — |
| 跳过确认 | `--permission-mode bypassPermissions` | — |
| 指定 model | `--model <id>` | `--provider <name>` |
| 追加 system prompt | `--append-system-prompt <text>` | — |
| 流式输出 | `--output-format stream-json` | — |

### 常用 Claude Code 命令示例

```bash
# 基础用法（简单任务）
claude -p "在当前目录创建一个 README.md" --no-session-persistence

# 指定 model
claude -p "优化这个函数的性能" --model sonnet-4 --no-session-persistence

# 添加 system prompt
claude -p "写一个 CLI 工具" \
  --append-system-prompt "这个工具需要在 Linux 和 macOS 上都能运行" \
  --no-session-persistence

# 流式 JSON 输出（用于解析 AI 的思考过程）
claude -p "重构 src/ 目录" \
  --output-format stream-json \
  --no-session-persistence

# 跳过所有确认（在可信目录）
claude -p "..." --permission-mode bypassPermissions --no-session-persistence
```

---

## 信任目录规则

| 目录 | 可用工具 |
|------|---------|
| `~/project/` | 全部工具 |
| `/tmp/` | 有限（文件操作）|
| `~/.openclaw/` | 仅读取 |
| 工作区根目录 | 不启动（会读取 SOUL/MEMORY）|

### 信任目录设置

如果需要在非信任目录工作：

```bash
# 方案 1：在 ~/project/ 下创建软链接
ln -s /path/to/your/project ~/project/yourproject

# 方案 2：手动确认（不推荐，每次都会暂停）
claude -p "..."  # 不带 --permission-mode

# 方案 3：在项目目录下先运行一次 claude（建立信任）
cd /path/to/project && claaude
# 看到提示后选择 "Always allow in this directory"
```

---

