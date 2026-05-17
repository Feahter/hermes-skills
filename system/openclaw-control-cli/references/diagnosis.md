# OpenClaw 故障诊断手册

## 1. Gateway 端口冲突（最常见根因）

**症状**：gateway 持续崩溃重启，CPU 100%，进程不断 fork。

**诊断**：
```bash
ps aux | grep "gateway --port" | grep -v grep
# 若看到多个进程 → 端口冲突
```

**常见冲突来源**：

| 安装来源 | 路径 | 版本检测 |
|----------|------|----------|
| Cellar (npm global) | `/usr/local/Cellar/node/*/lib/node_modules/openclaw/` | `openclaw -v` |
| npm global | `~/.npm-global/lib/node_modules/openclaw/` | `~/.npm-global/bin/openclaw -v` |
| nvm | `~/.nvm/versions/node/*/lib/node_modules/openclaw/` | `~/.nvm/versions/node/*/bin/openclaw -v` |
| QClaw app bundle | `~/Library/Application Support/QClaw/` | `openclaw -v` (交互式 shell) |

**排查命令**：
```bash
# 所有 launchd plist
ls ~/Library/LaunchAgents/ai.openclaw.*.plist

# 检查各路径版本
/usr/local/Cellar/node/25.9.0_1/bin/openclaw -v
~/.npm-global/bin/openclaw -v

# 交互式 shell 的 PATH（会走 nvm 等路径）
zsh -i -c 'which openclaw; openclaw -v'
```

---

## 2. 端口重分配（飞书/微信分立）

**场景**：飞书和微信各自需要独立 gateway，避免互相干扰。

**操作步骤**（以飞书为例，从 18789 → 28790）：

```bash
# a. 备份原 plist
cp ~/Library/LaunchAgents/ai.openclaw.gateway.feishu.plist ~/Library/LaunchAgents/ai.openclaw.gateway.feishu.plist.bak

# b. 修改 ProgramArguments 中的 --port 参数
# c. 修改 OPENCLAW_GATEWAY_PORT 环境变量
# d. 重载服务
launchctl bootout gui/$(id -u)/ai.openclaw.gateway.feishu
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.openclaw.gateway.feishu.plist

# e. 验证
sleep 2 && ps aux | grep "gateway --port" | grep -v grep
```

**注意**：同时要更新 openclaw.json 中的 channel 配置中对应的端口号。

---

## 3. openclaw 版本不一致

**症状**：`openclaw -v` 和 Cellar 里的版本不一致，交互 shell 和非交互 shell 结果不同。

**根因**：npm global 链接到了旧版本 Cellar/npm 包，或 nvm 路径在 PATH 中优先级高于 Cellar。

**解决**：
```bash
# 找到最新版本（Cellar npm 路径）
/usr/local/Cellar/node/*/bin/openclaw -v

# 如果 npm global 是旧的，替换链接
rm ~/.npm-global/bin/openclaw
ln -s /usr/local/Cellar/node/25.9.0_1/lib/node_modules/openclaw/openclaw.mjs ~/.npm-global/bin/openclaw
chmod +x ~/.npm-global/bin/openclaw

# 如果 nvm 里有过期版本，直接删掉
rm -rf ~/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw
```

**验证**：
```bash
zsh -i -c 'openclaw -v'   # 交互式 shell
openclaw -v               # 非交互式
```
两者结果应一致。

---

## 4. launchd 服务管理常用命令

```bash
# 查看服务状态
launchctl list | grep openclaw

# 停止服务
launchctl bootout gui/$(id -u)/ai.openclaw.gateway

# 启动服务
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.openclaw.gateway.plist

# 重载（stop + start）
launchctl bootout gui/$(id -u)/ai.openclaw.gateway
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.openclaw.gateway.plist

# 查看服务标识
grep -i label ~/Library/LaunchAgents/ai.openclaw.*.plist
```
