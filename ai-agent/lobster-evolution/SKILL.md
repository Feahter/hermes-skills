---
name: lobster-evolution
description: >
  龙虾（OpenClaw）自动进化引擎——观察→判断→执行→验证闭环。
  【单向架构】lobster-evolution 是唯一主控，读取其他组件的数据输出（单向数据流）：
  session-miner（观察数据）、skill-proposer（提案数据）、self-healer（自愈数据）、
  skill-health-monitor（健康数据）、user-preference-profile（偏好数据）。
  不形成循环依赖，每次心跳按顺序执行各层。
  实现无需外部训练管道的能力自动增长。
triggers:
  - keywords:
      - "自动进化"
      - "龙虾进化"
      - "session挖掘"
      - "技能提案"
      - "进化诊断"
      - "检查进化"
      - "lobster evolution"
    load: true
    priority: high
  - keywords:
      - "模式发现"
      - "能力成长"
      - "进化状态"
    load: true
    priority: medium
  - keywords:
      - "健康度"
      - "技能健康"
    load: false
    priority: low
    note: 与weather-advisor等技能重叠，优先触发其他技能
---

# 🦞 Lobster Evolution — 龙虾自动进化引擎

*让龙虾自己变强*

## 核心理念

**进化的上限是行为适应，进化的深度是自动化程度。**

在"不能改模型权重"的硬约束下，最大化进化 = **最大化自动化适应循环的闭环程度**。

龙虾不靠重新训练，而是在每次心跳中观察自己的行为模式、发现不足、提出改进、执行修复、验证效果——像生物进化一样，小步迭代，累积优势。

---

## 进化闭环架构（单向数据流，无循环依赖）

```
[观察层] lobster 读取 session-miner 输出（单向）
    ↓
[判断层] lobster 读取 skill-proposer 输出 → 生成技能提案（单向）
    ↓
[执行层] lobster 执行文件写入/skill安装（单向输出）
    ↓
[验证层] 下次心跳读取执行结果验证（单向）
    ↓
[自愈层] lobster 读取 self-healer 结果并执行修复（单向）
    ↓
[偏好层] lobster 读取 user-preference-profile 并应用策略（单向）
    ↓
[监测层] lobster 读取 skill-health-monitor 结果（单向）
```

**关键原则**：lobster-evolution 是唯一的主控脚本，其他组件都是**数据生产者**， lobster-evolution 单向读取它们的结果，不形成循环。

---

## 核心组件一览

| 组件 | 脚本位置 | 职责 |
|------|---------|------|
| session-miner | `scripts/evolution/session-miner.py` | 跨Session Query提取+统计 |
| skill-proposer | `scripts/evolution/skill-proposer.py` | 模式分析+技能提案生成 |
| self-healer | `scripts/evolution/self-healer.py` | 已知错误模式自动修复 |
| skill-health | `scripts/evolution/skill-health-monitor.py` | 技能健康度打分+预警 |
| user-profile | `scripts/evolution/user-preference-profile.py` | 用户偏好提取+画像 |
| daily-mining | `.state/evolution/daily-mining.md` | 当日挖掘结果 |
| proposals | `.state/evolution/proposals/` | 待审批技能提案 |
| skill-health | `.state/evolution/skill-health.json` | 技能健康度快照 |
| user-preferences | `.state/evolution/user-preferences.json` | 用户偏好画像 |

---

## 快速检查命令（心跳用）

```bash
# ============================================
# 一键全维度检查（推荐）
# ============================================

# 维度1+2：Session挖掘 + 提案生成
python3 ~/.openclaw/workspace/scripts/evolution/session-miner.py 7
python3 ~/.openclaw/workspace/scripts/evolution/skill-proposer.py

# 维度3：错误自愈检查
python3 ~/.openclaw/workspace/scripts/evolution/self-healer.py

# 维度4：用户偏好提取
python3 ~/.openclaw/workspace/scripts/evolution/user-preference-profile.py

# 维度5：技能健康度检查
python3 ~/.openclaw/workspace/scripts/evolution/skill-health-monitor.py

# ============================================
# 快速状态查看（无需运行任何脚本）
# ============================================

# 查看最近挖掘报告
cat ~/.openclaw/workspace/.state/evolution/daily-mining.md

# 查看最新提案
ls -t ~/.openclaw/workspace/.state/evolution/proposals/ | head -1 | xargs cat

# 查看自愈报告
cat ~/.openclaw/workspace/.state/evolution/self-healer.md 2>/dev/null || echo "暂无自愈报告"

# 查看技能健康度
cat ~/.openclaw/workspace/.state/evolution/skill-health.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'总技能数:{d[\"total_skills\"]}'); [print(f'  ⚠️ {s[\"name\"]}: {s[\"reason\"]}') for s in d.get('low_health_warnings',[])]" 2>/dev/null || echo "暂无健康度数据"

# 查看用户偏好摘要
cat ~/.openclaw/workspace/.state/evolution/user-preferences.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'纠正次数:{d[\"total_corrections\"]}, 最佳实践:{d[\"total_best_practices\"]}'); [print(f'  ✅ {p}') for p,v in d['patterns'].items() if v]" 2>/dev/null || echo "暂无偏好数据"

# 查看进化状态总览
cat ~/.openclaw/workspace/.state/evolution/evolution-state.json 2>/dev/null || echo '{"status":"未初始化"}'
```

---

## 五大进化维度详解

### 维度1：跨Session模式挖掘 ✅ 已部署

**现状**：每日心跳自动执行，结果存 `daily-mining.md`

**数据源**：`~/.openclaw/agents/main/sessions/*.jsonl`

**挖掘流程**（`session-miner.py`）：
1. 扫描最近N天（默认7天）修改过的 session JSONL 文件
2. 提取所有 `role=user` 的消息内容，按句子切分
3. 去重（以句首40字符为key）
4. 分类统计：
   - **高频意图（≤15字）**：短小精确的指令模式，如"帮我查天气"×5
   - **描述性请求（16-40字）**：较长的描述性需求
   - **高频中文词**：连续2个以上中文字的词频统计，识别领域热点

**输出格式**：
```markdown

## 每日模式报告

> 详细内容 → `references/daily-report-template.md`

## 依赖关系

### 脚本组件（内置，执行层工具）

| 脚本 | 路径 | 职责 | 调用方式 |
|------|------|------|---------|
| session-miner | `scripts/evolution/session-miner.py` | 跨Session Query挖掘 | 心跳自动调用 |
| skill-proposer | `scripts/evolution/skill-proposer.py` | 高频模式→技能提案 | 心跳自动调用 |
| self-healer | `scripts/evolution/self-healer.py` | 已知错误→修复建议 | 心跳自动调用 |
| skill-health-monitor | `scripts/evolution/skill-health-monitor.py` | 技能健康度打分+预警 | 心跳自动调用 |
| user-preference-profile | `scripts/evolution/user-preference-profile.py` | 用户偏好提取+画像 | 心跳自动调用 |

### 外部 Skill（按需调用）

| Skill | 触发时机 | 进化效果 |
|------|---------|---------|
| `skillhub_install` | 执行层需安装新技能时 | 安装提案中的新 Skill |
| `skill-creator` | 提案通过，需创建新 Skill 时 | 生成新 Skill 代码 |
| `basal-ganglia-memory` | 长期偏好沉淀 | 习惯层自动化（跨会话偏好） |
| `qclaw-openclaw` | 定时任务集成 | 驱动心跳执行进化闭环 |

---

## HEARTBEAT 集成

在心跳中执行，按顺序执行以下步骤：

```python
# Step 1: Session挖掘（维度1）
# 运行 session-miner.py 7，自动写入 daily-mining.md
run("python3 ~/.openclaw/workspace/scripts/evolution/session-miner.py 7")

# Step 2: 提案生成（维度2）
# 读取 daily-mining.md，如有新高频模式则生成提案
run("python3 ~/.openclaw/workspace/scripts/evolution/skill-proposer.py")

# Step 3: 自愈检查（维度3）
# 读取 .learnings/ERRORS.md，匹配已知模式，生成报告
run("python3 ~/.openclaw/workspace/scripts/evolution/self-healer.py")

# Step 4: 偏好提取（维度4）
# 读取 .learnings/LEARNINGS.md，更新用户偏好画像
run("python3 ~/.openclaw/workspace/scripts/evolution/user-preference-profile.py")

# Step 5: 健康度检查（维度5）
# 扫描所有 Skills，打分并预警低健康度
run("python3 ~/.openclaw/workspace/scripts/evolution/skill-health-monitor.py")

# Step 6: 状态汇总
# 如有任何 high 优先级提案 → 主动告知用户
# 如有自愈报告 → 更新 evolution-state.json
# 如有低健康度警告 → 告知用户
```

---

## 进化状态追踪

文件：`.state/evolution/evolution-state.json`

```json
{
  "lastMining": "2026-04-04",
  "lastProposal": "2026-04-04",
  "lastSelfHeal": "2026-04-04",
  "lastProfileUpdate": "2026-04-04",
  "lastHealthCheck": "2026-04-04",
  "activeProposals": [
    {"domain": "节气", "priority": "high", "status": "已有chinese-name-lookup覆盖"}
  ],
  "resolvedFeedback": 3,
  "selfHealedErrors": 0,
  "lowHealthSkills": []
}
```

---

## 安全边界

**允许**（文件级操作，无需审批）：
- 读写 `.state/evolution/` 目录
- 读写 `.learnings/` 目录
- 读写 `memory/` 目录
- 调用 `skillhub_install`
- 执行 `self-healer.py`（只读+建议，不自动修改）
- 执行 `skill-health-monitor.py`（只读+报告，不自动删除）
- 执行 `user-preference-profile.py`（只读+画像，不自动调整行为）

**需审批**（高风险操作，必须用户确认）：
- 创建新 Skill（调用 skill-creator）
- 修改核心配置（SOUL.md, IDENTITY.md）
- 删除 Skill（无论是否低健康度）
- 修改 `MEMORY.md`
- 自动执行 self-healer 的修复动作（待实现）

**禁止**：
- 修改模型权重
- 修改 OpenClaw 核心代码
- 绕过审批机制
- 未确认前自动删除任何文件

---

## 使用示例

### 龙虾，我需要什么新技能？

```
我：帮我看看最近有什么进化信号
龙虾：
🦞 进化诊断报告（2026-04-04）

🔴 高频信号（维度1+2）：
- 节气 ×73（7天）→ chinese-name-lookup 已覆盖 ✅
- high_freq_query ×多种 → 子Session代码优化
  - "do not busy-poll" ×12
  - "month" ×7

🟡 维度3-5 状态：
- 错误自愈：已部署7种模式，上次运行 2026-04-03
  - 待增强：LLM判断未知错误 + 自动执行修复
- 用户偏好：提取到3个行为模式
  - 待实现：实时应用偏好到对话输出
- 技能健康度：总技能163个，低健康度0个
  - 待实现：真实调用追踪 + 自动建议推送

💡 技能提案：
- 暂无高优先级新提案

✅ 系统状态：维度1+2完全部署，维度3-5部分部署
🚧 维度3 增强项：LLM自愈判断 + 自动修复执行
🚧 维度4 增强项：偏好实时应用
🚧 维度5 增强项：真实调用追踪 + 自动归档
```

### 龙虾，检查一下技能健康度

```
🦞 技能健康度报告（2026-04-04）

总技能数：163

🏥 健康度TOP10：
  feishu                    █████████░ 9/10  (提及45次)
  coding-agent              █████████░ 9/10  (提及38次)
  lobster-evolution         ████████░░ 8/10  (提及22次)
  ...

⚠️ 低健康度技能（需关注）：
  - deprecated-skill-x: health=2, mentions=0 → 考虑合并到通用技能或卸载

📄 详细报告：~/.openclaw/workspace/.state/evolution/skill-health.json
```

### 龙虾，发生了什么错误需要自愈？

```
🦞 错误自愈报告（2026-04-04）

✅ 可自愈: path-not-found-in-skill-x
   类型: path_fix - 路径不存在，尝试修正路径
   错误: path /wrong/path/to/skill not found

⚠️ 需人工: unknown-api-error
   错误: Unexpected API response format...

📊 自愈统计：自动修复1项，需人工1项
📄 报告：~/.openclaw/workspace/.state/evolution/self-healer.md
```

### 龙虾，我的行为偏好是什么？

```
🦞 用户偏好画像（2026-04-04）

更新时间：2026-04-04T10:00:00
累计纠正：5次
累计最佳实践：3次

行为模式：
  ✅ concise（简洁模式）：用户多次提到"太长"
  ✅ direct（直接模式）：用户不喜欢废话铺垫

最近纠正：
  - 回复太长 → 已学习，输出更简洁
  - 缺少代码示例 → 已学习，技术问题附代码

最近最佳实践：
  - 先自助再求助 → 已内化为行为准则
  - 谋定而后动 → 遇重大决策先分析后执行
```
