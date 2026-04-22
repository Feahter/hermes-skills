---
name: gateway-health-monitor
description: |
  飞书 Gateway 健康检查技能。监控 `gateway-feishu.log` 中的消息接收和回复（reaction event）情况，连续 2 次 reply rate 低于 50% 时触发飞书告警。
triggers:
  - "飞书 gateway 健康检查"
  - "feishu gateway 告警"
  - "gateway health"
metadata:
  openclaw:
    emoji: "🩺"
---

## 触发场景

- **每 8 小时 cron 自动检查**（2026-04-22 从 4 小时调整，进一步降低频次）
- 手动诊断飞书不回复时运行

## ⚠️ OpenClaw 自身 cron vs Hermes cron vs 系统 crontab

**OpenClaw 管理自己的 cron**，不在 Hermes cronjob 里，也不在系统 crontab 里：
- 配置文件：`~/.openclaw/cron/jobs.json`
- 修改方式：直接编辑 JSON（`everyMs` 字段，4小时 = `14400000`）
- 查看列表：`openclaw cron list` 或直接读 JSON
- **不要在系统 crontab 里找健康检查任务** — 找不到

## 使用方式

```bash
python3 skills/gateway-health-monitor/scripts/gateway_health_checker.py
```

**Exit codes:**
- `0` = 健康
- `2` = 告警触发（reply rate 过低）
- `3` = 未知状态（无数据）

## 检测逻辑

1. 读取 `~/.openclaw/logs/gateway.log` 最近 15 分钟日志
2. 统计 `received message` 数量和 `reaction event` 数量
3. 计算 reply rate = replied / received
4. 连续 2 次 rate < 50% 且 total >= 2 → 告警
5. 告警通过 `print()` 输出（由 cron 任务捕获并推送飞书）

**注意**：message ID 格式为 `oc_xxx`（OpenClaw message ID），脚本中必须是 `oc_\w+` 而非 `om_`

## 状态文件

`~/.openclaw/workspace/.state/gateway-health-state.json`

```json
{
  "consecutive_failures": 0,
  "last_check": "2026-04-15T18:00:00",
  "last_alert": null,
  "reply_rates": [0.8, 0.9, 1.0, 0.7]
}
```

## Cron 配置

OpenClaw **使用自身内部调度器**，不依赖系统 crontab：
- 配置文件：`~/.openclaw/cron/jobs.json`
- 字段 `everyMs: 28800000` = 8 小时
- 修改后 OpenClaw 自动重载，无需重启

告警触发时输出包含：`⚠️ 飞书 Gateway 告警` 标记，供 cron handler 识别并推送飞书。

## 故障排查经验（2026-04-21）

### 08:16 首次 EAGAIN — 健康检查本身是多路并行 exec 的诱因
- **时间线**：08:16 第一次 EAGAIN 出现，也是健康检查 cron 触发时刻
- **机制**：cron session 并行 spawn 多个 exec（ps/lsof/cat/launchctl），如果系统资源已紧张，fork 竞争触发 EAGAIN；一旦 EAGAIN，新进程无法 spawn，已有的也卡住，形成死锁
- **解法**：降低 cron 频率（5min → 10min → 1h） + 脚本内增加 fork 预检，EAGAIN 时跳过检查

### 脚本内资源保护
- `check_system_resource()` 在检查前先做轻量 `fork()` 测试
- 如果 fork 报 EAGAIN/ENOMEM，跳过本次检查，避免雪上加霜
- 资源恢复后自动正常，不影响正常检查功能
- **症状**：所有 terminal/file/execute_code/browser 工具全部返回 `BlockingIOError: [Errno 35]`，连 `pwd` 都跑不了
- **根因**：不是文件 I/O 阻塞，而是 `/bin/zsh` 子进程 slot 全部被占用或僵死
- **判断**：`ps aux | grep openclaw` 确认进程是否活着；`lsof -p <pid> | grep openclaw.json` 确认用的是哪个配置
- **解法**：重启系统或 `pkill -9 zsh`（无其他补救手段）

### 两个配置文件容易混淆
- `~/.openclaw/openclaw.json` — gateway 实际使用（`lsof -p <pid>` 确认）
- `~/openclaw/openclaw.json` — 旧路径，历史错误日志来源
- **旧配置文件报错不一定是当前问题**，看时间戳和进程读取情况

### 日志格式与脚本正则不匹配（静默失效）
**症状**：health checker 一直返回 `reply_rate: null` 或 `total=0`，但 gateway 明明在处理消息

**根因**：脚本里 message ID 正则写的是 `om_\w+`（错误），实际日志格式是 `oc_\w+`

**验证方法**：
```bash
# 手动跑 health checker，看 JSON 输出
python3 ~/.hermes/skills/system/gateway-health-monitor/scripts/gateway_health_checker.py

# 确认日志格式匹配
grep "received message" ~/.openclaw/logs/gateway.log | head -3
# 应该看到: received message from ... in oc_xxx (p2p)
# 如果是 om_xxx → 脚本正则正确；如果是 oc_xxx → 需要修复正则
```

**修复**：脚本中 `om_` → `oc_`（两处，received 和 reaction 解析）

### 诊断优先级
1. `ps aux | grep openclaw` — 确认进程活着
2. `lsof -p <pid> | grep openclaw.json` — 确认用哪个配置
3. `tail recent gateway.log` — 确认 WebSocket 连接状态
4. `cat state.json` — 确认健康状态是否有残留旧数据（崩溃前）
5. **手动跑 health checker** — 验证脚本解析逻辑是否正常
