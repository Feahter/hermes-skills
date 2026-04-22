---
name: skill-audit
description: AI Agent Skills 安全扫描器。扫描 SKILL.md 内容中的危险 pattern、权限过大、数据外传风险。三层递归扫描：批量自动扫描（5min/179skills）→ 重点精准分析 → 元认知自我演进。触发：安装新 skill 前、批量审查、遇到可疑 skill。Keywords: skill audit, security scan, 安全扫描, 漏洞检测, 红队检测。
version: 1.0.0
tags: [security, auditing, risk-assessment]
source:
  project: skill-audit
  license: MIT
  auto_generated: false
  enhanced_via: skill-vetter + talent-mind + skill-creator
  updated_at: 2026-04-20
---

# Skill Audit 🔒🦀

三层递归安全扫描系统 + 自我演进引擎。

> 参考 `skill-evolution-manager` 的演进模式：`evolution.json` → 增量合并 → 缝合回规则库

## 三层扫描架构

### 第一层：认知架构（自动扫描引擎）— 系统A

> 类比 talent-mind 的系统A：直觉模式识别，高速批量处理

- `danger-pulse`：179 个 SKILL.md 全文正则扫描，5 分钟出全量结果
- `risk-classifier`：基于规则的风险分级（⚪干净/⚠️警告/🚨确定/⛔阻断）
- `source-tracer`：来源追溯 + 自动化指标获取（下载量/Stars/更新时间）
- `license-checker`：许可证识别（MIT/Apache/GPL/proprietary）

### 第二层：表征方式（多模态分析报告）— 系统B

> 类比 talent-mind 的系统B：逻辑验证，防止系统A的误报

- **威胁建模视角**：credential/token/key/exfil 路径识别
- **最小权限视角**：文件/网络/命令的实际需求是否超出声称范围
- **信任层级视角**：来源可信度 × 下载量 × 更新频率
- **模糊地带视角**：灰度 skill（功能合理但权限过大）

### 第三层：元认知协议（自我演进）— 元层

> 类比 talent-mind 的元认知钩子：定期跳出观察扫描器本身的盲区

```
每次扫描后 → 自动发现新危险 pattern → 加入规则库（规则版本化）
                                       ↓
                          扫描"扫描器本身"的盲区
```

---

## 使用场景

| 场景 | 触发方式 |
|------|----------|
| 安装新 skill 前 | `skill-audit scan <skill-name>` |
| 批量审查全部 skills | `skill-audit full-scan` |
| 审查 skill-cache 中待安装项 | `skill-audit cache-scan` |
| 查看高危 skill 详情 | `skill-audit deep-dive <skill-name>` |
| 导出安全报告 | `skill-audit report [--format=json\|md]` |
| 更新危险 pattern 库 | `skill-audit update-rules` |

---

## 快速开始

```bash
# 扫描单个 skill
skill-audit scan wecomcli-setup

# 全量扫描（179 skills，~5分钟）
skill-audit full-scan

# 扫描 skill-cache（待安装项）
skill-audit cache-scan

# 深度分析高危 skill
skill-audit deep-dive lobster-evolution

# 导出报告
skill-audit report --format=md
```

---

## 危险 Pattern 分级

### ⚪ CLEAN（0分）- 通过

无危险 pattern，功能与权限匹配。

### ⚠️ WARNING（1-2分）- 需人工复核

| Pattern | 说明 |
|---------|------|
| `npm install -g` | 全局安装，可能污染系统 |
| `curl http://` | 非加密传输 |
| `~/.bashrc` / `~/.zshrc` | 修改 shell 配置 |
| `sudo` | 请求管理员权限 |
| `eval` | 动态代码执行 |
| `subprocess` / `os.system` | 命令执行 |
| 外部域名的 curl/wget | 需验证域名可信度 |

### 🚨 DANGER（3-4分）- 高风险，需人工审批

| Pattern | 说明 |
|---------|------|
| 读取 `~/.ssh/` | 敏感密钥目录 |
| 读取 `~/.aws/` | 云凭证 |
| 读取 `~/.config/` | 配置文件 |
| `base64 decode` | 代码混淆 |
| 发送数据到外部服务器 | 数据外传 |
| `eval()` / `exec()` 动态执行 | 任意代码执行 |
| 请求 API key / token | 凭证请求 |
| 网络调用到 IP 而非域名 | 难以追踪 |
| 安装未声明的包 | 隐藏依赖 |

### ⛔ BLOCK（5+分）- 阻断，不建议安装

| Pattern | 说明 |
|---------|------|
| 访问 `MEMORY.md` / `USER.md` / `SOUL.md` | 记忆/身份文件 |
| 访问 `~/.netrc` | 明文密码 |
| 浏览器 cookie/session 访问 | 会话劫持 |
| 修改系统文件（/etc/等） | 系统破坏 |
| Obfuscated code（压缩/编码/混淆） | 隐藏恶意代码 |
| `rm -rf` 无确认 | 危险删除 |

---

## 输出格式

```
SKILL AUDIT REPORT
═══════════════════════════════════════════════
Skill: [name]
Source: [ClawHub / GitHub / skill-cache / local]
Author: [username or "unknown"]
───────────────────────────────────────────────
METRICS:
• Downloads/Stars: [count or "N/A"]
• Last Updated: [date or "unknown"]
• Files Reviewed: [count]
───────────────────────────────────────────────
DANGER PATTERN SCORE: [0-15]
• Found: [list or "None"]

PERMISSION SCOPE:
• Files: [list or "None"]
• Network: [list or "None"]
• Commands: [list or "None"]
───────────────────────────────────────────────
RISK LEVEL: [⚪ CLEAN / ⚠️ WARNING / 🚨 DANGER / ⛔ BLOCK]

VERDICT: [✅ INSTALL / ⚠️ CAUTION / ❌ REJECT]

RECOMMENDATIONS:
1. [action item]
2. [action item]
═══════════════════════════════════════════════
```

---

## 演进机制

> 参考 `skill-evolution-manager` 的增量模式：`evolution.json` → 增量合并 → 缝合回规则库

### 演进流程

```
扫描结果 → False Positive 分析 → 规则增量生成 → 人工确认 → 缝合回规则库
```

### 演进命令

```bash
# 查看演进状态
skill-audit evolve --status

# 查看待处理变更（需人工确认）
skill-audit evolve

# 自动模式（无需确认，直接应用）
skill-audit evolve --auto

# 部分接受（只接受第1、3条）
skill-audit evolve --accept 1,3

# 拒绝所有变更
skill-audit evolve --reject
```

### 演进约束

- **保守策略**：只降级误报规则（高命中 + 低实际风险 → 降 severity）
- **不擅自升级**：从不主动加严规则（防止漏报）
- **版本化 delta**：每次变更生成独立 patch 文件，可回滚
- **人工确认**：默认需要确认（`--auto` 跳过）

### 演进判定标准

| 条件 | 动作 |
|------|------|
| 误报率 > 30% 且 clean 命中 >= 3 | 降级 severity |
| severity >= 4 的规则误报 | 降 2 级 |
| severity == 3 的规则误报 | 降 1 级 |

### 演进历史数据

```json
// ~/.hermes/.skill-audit-cache/rules_history.json
{
  "current_version": "1.0.0",
  "total_evolutions": 3,
  "last_evolved": "2026-04-20T18:00:00",
  "deltas": [...],
  "false_positive_stats": {...}
}
```

### 规则固化

- 当前版本规则固化：`references/rules_v1.md`
- 演进后规则覆盖：`~/.hermes/.skill-audit-cache/rules_v{N}.py`

## ⚠️ 已知的假阳性模式（2026-04-20 人工审核发现）

第一层正则扫描会把 **"描述危险行为的文本"** 当成 **"实际执行危险操作"** 来匹配，导致严重的假阳性。以下是已确认的误报模式：

### 误报来源 1：SKILL.md 中的规则说明文字

当 SKILL.md 描述"检查是否使用危险操作"时，关键词会被正则命中，但实际并无危险操作：

| 被误匹配的关键词 | 出现场景 | 示例 |
|---|---|---|
| `MEMORY.md / USER.md / SOUL.md` | "检查是否访问" 的说明句 | `• Accesses MEMORY.md, USER.md, SOUL.md` |
| `eval() / exec()` | "检查是否使用" 的 checklist 项 | `• Uses eval() or exec()` |
| `base64 decode` | "检查是否混淆" 的描述 | `• Uses base64 decode on anything` |
| `~/.ssh / ~/.aws` | "检查是否读取" 的说明 | `• Reads ~/.ssh, ~/.aws without clear reason` |
| `sudo` | "检查是否请求权限" 的清单 | `• Requests elevated/sudo permissions` |
| `curl / wget` | "检查是否下载" 的描述 | `• curl/wget to unknown URLs` |
| `api key / token / credential` | "检查是否请求凭证" 的功能描述 | `• Requests credentials/tokens/API keys` |

### 误报来源 2：SKILL.md 中的代码示例

SKILL.md 中的内联代码块如果包含危险关键词，正则同样会命中：
- 文档中 `base64 decode` 作为功能示例 → 被 base64 decode 规则匹配
- 文档中 `curl https://example.com` 作为 curl 用法示例 → 被网络规则匹配

### 验证方法

当 BLOCK 分数来自纯文档型 skill（如 skill-audit 自审 872.1分、skill-vetter 455.1分）时，必须：

1. **手动检查 scripts/ 目录**：实际危险操作一定在脚本文件里，不在 SKILL.md 文字里
2. **查看 rules_triggered 的匹配行**：如果匹配行都是普通段落文字而非命令，属于误报
3. **关键词上下文判断**：出现在 "检查是否..." 描述句中 → 误报；出现在 `$()、 ``、代码块" 中 → 真危险

### 已确认的真实高危技能（经人工审核）

| Skill | 评分 | 真实风险 |
|---|---|---|
| `autonomous-ai-agents/claude-code` | 142.6 | 🔴 API key + 全局安装 + 命令执行 |
| `red-teaming/godmode` | 100.0 | 🔴 exec() 动态执行 + base64 混淆 |
| `productivity/google-workspace` | 150.4 | 🟡 OAuth2 token 凭证管理 + HTTPS 网络 |
| `productivity/pdf` | 114.0 | 🟡 pip 安装依赖 |

### 修复方向（待实现）

1. **context-aware 匹配**：只在代码块/命令执行上下文匹配，忽略普通段落
2. **分层扫描**：SKILL.md 正文用低权重权重，scripts/ 目录下的代码用正常权重

---

## 自动化脚本机制

> 详细内容 → `scripts/audit_runner.py`（批量扫描引擎）
> 详细内容 → `scripts/danger_scanner.py`（危险 Pattern 扫描器）
> 详细内容 → `scripts/source_tracker.py`（来源追溯与指标获取）
> 详细内容 → `scripts/evolve.py`（演进引擎）
> 详细内容 → `references/rule_engine.md`（规则引擎与自我演进机制）

---

## 信任层级

| 层级 | 来源 | 审查力度 |
|------|------|----------|
| L1 | `~/.hermes/skills/`（已安装本地） | 全量扫描 |
| L2 | ClawHub（高下载量 1000+，近期更新） | 快速扫描 + 来源验证 |
| L3 | GitHub（高 Stars，知名作者） | 快速扫描 + 代码审查 |
| L4 | skill-cache（待安装） | 全量扫描 + 重点审查 |
| L5 | 未知来源 / 新作者 / 无下载量 | 最高审查 + 人工审批 |

---

*结合 Skill-Vetter 的 checklist、Talent-Mind 的三层递归、Skill-Creator 的自动化框架。*
*恐惧是特征，不是缺陷。* 🔒🦀
