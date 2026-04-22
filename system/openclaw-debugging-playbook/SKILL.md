---
name: openclaw-debugging-playbook
description: OpenClaw 问题诊断 playbook。当飞书 gateway 异常时，从日志检查、健康监控、进程管理三个维度系统化排查。合并 openclaw-gateway-debug 全部功能。
triggers:
  - "飞书 openclaw 不回复"
  - "openclaw 报错"
  - "gateway 健康检查"
  - "openclaw 日志"
  - "飞书验证问题"
  - "gateway 崩溃"
  - "openclaw restart loop"
  - "multiple openclaw-gateway processes"
  - "QCLAW_LLM_API_KEY missing"
  - "launchd gateway failed to start"
  - "KeepAlive crash loop"
---

# OpenClaw 诊断 Playbook

## 工具可用性矩阵

| 工具 | 阻塞时可用？ | 用途 |
|------|-------------|------|
| terminal | ❌ 阻塞时不可用 | 命令执行 |
| read_file | ❌ 阻塞时不可用 | 文件读取 |
| search_files | ❌ 阻塞时不可用 | 内容搜索 |
| execute_code | ❌ 阻塞时不可用 | Python 脚本 |
| **cronjob** | ✅ **始终可用** | 列出/管理定时任务 |
| skill_view | ✅ 始终可用 | 读取 skill 内容 |

> ⚠️ **经验**：`BlockingIOError: [Errno 35]` 大面积出现时，通常是会话级文件句柄耗尽。cronjob 走独立通道此时仍可用。

---

## 诊断流程

### Step 1: 确认进程存活

```bash
ps aux | grep -i openclaw | grep -v grep
# 或
ps aux | grep -i qclaw | grep -v grep
```

### Step 2: 查看飞书日志

日志路径：`~/.openclaw/logs/gateway-feishu.log`

**可用工具**（按优先级）：
1. `read_file` — 直接读取日志文件
2. `search_files` — 在日志中搜索关键词（auth、error、health、validation）
3. `terminal` — `tail -n 100 ~/.openclaw/logs/gateway-feishu.log`

---

### Step 3: 识别进程身份

每个进程属于哪个系统：

| 进程类型 | PPID | 来源 | 配置目录 |
|---|---|---|---|
| PPID=1, 无端口监听 | launchd残留 | 旧 plist KeepAlive | 看 launchd list |
| PPID=1, 监听 `:18789` | launchd (旧) | `.openclaw` 全局安装 | `~/.openclaw/openclaw.json` |
| PPID=1, 监听 `:28789` | QClaw App | QClaw App 自带 | `~/.qclaw/openclaw.json` |
| PPID≠1 | QClaw App 子进程 | Electron fork | `~/Library/Application Support/QClaw/` |

```bash
# 确认每个进程的父进程
ps -p <PID> -o pid,ppid,etime,command=

# 检查 gateway 端口监听状态
lsof -i :18789 -i :28789 2>/dev/null | grep LISTEN

# 查看所有 launchd agents
launchctl list | grep -E "ai.openclaw|com.openclaw|qclaw"
```

**崩溃特征**：`SecretRefResolutionError: Environment variable "QCLAW_LLM_API_KEY" is missing`

### Step 5: 两套系统区分

**系统 A — QClaw App（腾讯）**：
```
配置目录: ~/.qclaw/
状态目录: ~/.qclaw/
Plist 标签: ai.openclaw.gateway.wechat (wechat channel)
Node 路径: /Applications/QClaw.app/Contents/Resources/node/ 或 /usr/local/Cellar/node/.../lib/node_modules/openclaw/
端口: 28789
```

**系统 B — 全局安装 openclaw（Homebrew/nvm/npm global）**：
```
配置目录: ~/.openclaw/
Plist 标签: ai.openclaw.gateway 或 ai.openclaw.gateway.feishu
Node 路径: /Users/fuzhuo/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/
端口: 18789
```

### Step 6: 找出缺失的环境变量

崩溃日志中的 `${VAR_NAME}` 占位符就是缺失的变量。

常见缺失变量：
- `QCLAW_LLM_API_KEY` — 模型 API key
- `QCLAW_LLM_BASE_URL` — 模型服务地址
- `QCLAW_WECHAT_WS_URL` — 微信 WebSocket URL

**找 key 来源**：
```bash
# 检查环境变量（如果之前 export 过）
env | grep -iE "(qclaw_llm|api_key|base_url)"
```

### Step 7: 健康检查状态

状态文件：`~/.openclaw/workspace/.state/gateway-health-state.json`

关键指标：
- `consecutive_failures`：连续失败次数
- `reply_rates`：最近几次的回复率

健康检查脚本：`~/.hermes/skills/system/gateway-health-monitor/scripts/gateway_health_checker.py`

**手动运行健康检查**：
```bash
cd ~/.openclaw/workspace && python3 skills/gateway-health-monitor/scripts/gateway_health_checker.py
# exit 0 = 健康，exit 2 = 告警，exit 3 = 未知
```

---

### Step 8: 降低健康检查频次

当前配置：每 5 分钟（`*/5 * * * *`）

**修改方式**：
1. 列出当前 cron 任务：`cronjob list`
2. 删除旧任务（获取 job_id 后）：`cronjob remove job_id`
3. 创建新频率任务（如每 15 分钟）：`cronjob create` with `schedule: "*/15 * * * *"`

---

### Step 9: 验证问题介入

如果健康检查发现 reply rate 低于 50%：

1. **查看具体错误** — 在日志中搜索 `error`、`auth`、`validation`、`signature`
2. **常见问题**：
   - Token 过期 → 需要刷新飞书 token
   - 签名验证失败 → 检查 app_secret
   - 消息队列堵塞 → 重启 openclaw 进程
3. **临时措施**：降低检查频次避免告警轰炸
4. **长期解决**：根据错误类型修复配置

### Step 10: 修复方案

#### 方案 A：在 launchd plist 中补上环境变量

编辑 plist 添加缺失变量：

```xml
<key>EnvironmentVariables</key>
<dict>
    <!-- 其他已有变量保持不变 -->
    <key>QCLAW_LLM_API_KEY</key>
    <string>你的key值</string>
    <key>QCLAW_LLM_BASE_URL</key>
    <string>https://api.minimax.chat</string>
    <key>QCLAW_WECHAT_WS_URL</key>
    <string>wss://...</string>
</dict>
```

重启服务：
```bash
launchctl unload ~/Library/LaunchAgents/ai.openclaw.gateway.wechat.plist
launchctl load ~/Library/LaunchAgents/ai.openclaw.gateway.wechat.plist
```

#### 方案 B：如果 QClaw App 的 gateway 正常，考虑清理旧系统

如果 wechat channel 本应由 QClaw App 管理，旧的 wechat launchd plist 是冗余的，可以卸载：

```bash
launchctl unload ~/Library/LaunchAgents/ai.openclaw.gateway.wechat.plist
# 可选：删除 plist 文件
rm ~/Library/LaunchAgents/ai.openclaw.gateway.wechat.plist
```

### 关键经验

1. **QClaw App 和全局 openclaw 是两套独立系统** — 不要混用配置
2. **每个 plist 只管自己的 channel** — wechat plist 管 wechat，feishu plist 管 feishu
3. **变量引用格式 `${VAR}`** — 在 openclaw.json 中看到 `${QCLAW_LLM_API_KEY}`，意味着需要在运行时环境提供该变量
4. **launchd 环境是独立的** — 在 shell 里 export 的变量，launchd 服务看不到（除非写在 plist 的 EnvironmentVariables 里）
5. **KeepAlive 会让 crash 循环持续** — 只有修复了根因才能停止重启

---

## 关键文件路径

| 文件 | 路径 |
|------|------|
| 飞书日志 | `~/.openclaw/logs/gateway-feishu.log` |
| 健康状态 | `~/.openclaw/workspace/.state/gateway-health-state.json` |
| OpenClaw 配置 | `~/.qclaw/openclaw.json` |
| 健康检查脚本 | `~/.hermes/skills/system/gateway-health-monitor/scripts/gateway_health_checker.py` |
| workspace | `~/.openclaw/workspace/` |

---

## 进程管理

```bash
# 重启 openclaw（通过 launchctl）
launchctl unload ~/Library/LaunchAgents/com.openclaw.agent.plist
launchctl load ~/Library/LaunchAgents/com.openclaw.agent.plist

# 或通过 qclaw 命令
qclaw restart
```
