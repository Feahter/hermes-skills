---
name: experiment-logger
description: Skills 可观测性系统 - Phase 1（日志）+ Phase 2（回归/A/B）+ Phase 3（边界探测）。为 Skills 生态提供调用日志、失败追踪、质量闭环和风险路由能力。
---

# Skill Experiment Logger

Phase 1 + 2 + 3 完整系统 - Skills 生态的可观测性基础设施。

## 核心能力

| Phase | 能力 | 状态 |
|-------|------|------|
| Phase 1 | 调用日志 (invocations) | ✅ 完成 |
| Phase 1 | 失败案例采集 (fail_cases) | ✅ 完成 |
| Phase 2 | 回归测试生成/运行 | ✅ 完成 |
| Phase 2 | A/B 测试框架 | ✅ 完成 |
| Phase 3 | 边界签名扫描 (被动) | ✅ 完成 |
| Phase 3 | 对抗性探测 (主动) | ✅ 完成 |
| Phase 3 | 路由风险检查 | ✅ 完成 |

## 存储结构

```
~/.hermes/skills/.experiment_log/
├── invocations/           # 调用记录 (JSONL)
├── fail_cases/           # 失败案例 (按 Skill 名组织)
├── regression_tests/      # 回归测试集
└── ab_tests/             # A/B 测试记录
```

## 使用方式

### 方式 1: execute_code 调用（推荐）

```python
from hermes_tools import terminal
import json

# 记录调用开始
result = terminal(command="""python3 -c \"
import sys
sys.path.insert(0, '~/.hermes/skills/.experiment_log')
from skill_logger import get_logger
logger = get_logger()
inv_id = logger.log_invocation_start(
    skill_name='coding-agent',
    query=\\\\\\"帮我写一个快速排序\\\\\\",
    channel='weixin'
)
print(inv_id)
\"""")

inv_id = result["output"].strip()

# ... 执行 Skill ...

# 记录调用结束
terminal(command=f"""python3 -c \"
import sys
sys.path.insert(0, '~/.hermes/skills/.experiment_log')
from skill_logger import get_logger
logger = get_logger()
logger.log_invocation_end(
    invocation_id='{inv_id}',
    success=True,
    output={{'latency_ms': 1234, 'tokens_used': 567}}
)
\"""")
```

### 方式 2: 批量查询

```bash
# 查询最近调用
python3 ~/.hermes/skills/.experiment_log/skill_logger.py --query --limit 10

# 查询失败案例
python3 ~/.hermes/skills/.experiment_log/skill_logger.py --failures --skill coding-agent

# 统计信息
python3 ~/.hermes/skills/.experiment_log/skill_logger.py --stats
```

## 数据结构

### invocations 记录

```json
{
  "invocation_id": "uuid",
  "timestamp": "ISO8601",
  "query_hash": "MD5前12位",
  "user_id": "o9cq80yOfK3MM...",
  "channel": "weixin",
  "skill_selected": "coding-agent",
  "skill_version": "v2.3.1",
  "input": {
    "query": "帮我写一个快速排序",
    "context_snapshot": "..."
  },
  "output": {
    "result": "...",
    "tool_calls": [],
    "latency_ms": 1234,
    "tokens_used": 567
  },
  "quality": {
    "explicit_rating": null,
    "implicit_signal": "success",
    "followup_same_skill": false,
    "followup_refined": true
  },
  "error": null
}
```

### fail_cases 记录

```json
{
  "case_id": "uuid",
  "timestamp": "ISO8601",
  "original_query": "用Python写一个异步爬虫",
  "failed_skill": "coding-agent",
  "failure_reason": "timeout",
  "skill_version": "v2.3.1",
  "regression_test_created": false
}
```

## 嵌入到 Skill 的模板

在 Skill 执行的关键节点插入日志调用：

```
## 执行流程

### 1. 日志开始
[调用 skill_logger.log_invocation_start]

### 2. 执行业务逻辑
...

### 3. 日志结束
[调用 skill_logger.log_invocation_end]
```

## 失败案例 → 回归测试

失败案例积累后，可用以下命令生成回归测试：

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '~/.hermes/skills/.experiment_log')
from skill_logger import get_logger
logger = get_logger()

# 获取 coding-agent 的失败案例
failures = logger.query_failures(skill_name="coding-agent", limit=50)

# 转换为回归测试格式
regression_tests = [
    {
        "query": f["original_query"],
        "expected_skill": f.get("recommended_alternative") or f["failed_skill"],
        "failure_mode": f["failure_reason"],
    }
    for f in failures
    if f.get("original_query")
]

# 写入回归测试
logger.log_regression_test(
    skill_name="coding-agent",
    skill_version="auto",
    test_cases=regression_tests,
)

print(f"生成了 {len(regression_tests)} 条回归测试")
EOF
```

## 与 skill-evolution-manager 的联动

skill-evolution-manager 的反馈收集流程：
1. 用户反馈 → 触发 skill-evolution-manager
2. skill-evolution-manager 调用 experiment-logger 记录质量信号
3. 失败案例自动积累到 fail_cases/
4. 回归测试定期更新

## 触发词

- "查看 skill 调用日志"
- "查看失败案例"
- "生成本 Skill 的回归测试"
- "做 A/B 测试"
- "skill 统计"
- "运行完整闭环"
- "查看 Skill 边界"
- "检查查询风险"

---

## ⚠️ 常见陷阱

### `--probe --dry-run` 无实际效果

`boundary_detector.run_adversarial_probe()` 依赖传入的 `executor` 函数执行真实 skill。传入 mock_executor 时 dry-run 返回全部 skipped，数据无意义。

**正确做法：**
- 有真实执行路径 → 传入真实 executor，用 `--probe skill --dry-run=false` 探测
- 冷启动（无历史数据）→ 使用 seed 数据注入（见下方）

### 冷启动：boundary 签名从 0 开始

新 skill 没有调用记录时，`--scan` 和 `--probe` 都无法工作。需要手动 Seed Data Injection：

**步骤：**

1. 在 `~/.hermes/skills/.experiment_log/invocations/` 下创建 `seed_<skill>.jsonl`
2. 每条记录格式（见下方模板）
3. 每 skill 生成 5 条代表性触发查询
4. 运行 `--scan <skill>` 生成边界签名

**JSONL 格式模板：**

```json
{"invocation_id": "uuid", "timestamp": "ISO8601", "query_hash": "seed_N", "user_id": null, "channel": "seed", "skill_selected": "<skill>", "input": {"query": "<trigger phrase>", "context_snapshot": null}, "output": {}, "quality": {"explicit_rating": null, "implicit_signal": "success", "followup_same_skill": false, "followup_refined": false}, "error": null}
```

**何时使用：**
- 新安装的 skill 没有任何调用记录
- Cron job 发现某 skill boundary 缺失
- 初始化实验环境时批量 bootstrapping

```python
# Seed 数据注入模板（见 references/seed-data-injection.md）
# 扫描 SKILL.md → 提取 description + 触发场景 → 生成 5 条代表性调用记录
```

## Phase 3 详解 - Boundary Detector

### 核心概念

```
边界签名 = Skill 的表达能力地图

{
  "max_query_length": 2000,      # 最大支持长度
  "quality_decay_curve": {...},  # 质量随长度衰减
  "known_failure_modes": [...],  # 已知失败模式
  "unsupported_patterns": [...]   # 不支持的模式
}
```

### 被动扫描（从历史数据学习）

```bash
python3 ~/.hermes/skills/.experiment_log/boundary_detector.py \
  --scan coding-agent
```

从已有调用日志中提取：
- 查询长度分布
- 质量衰减曲线
- 失败模式统计
- 支持的 query 类型

### 主动探测（对抗性探测）

```bash
python3 ~/.hermes/skills/.experiment_log/boundary_detector.py \
  --probe coding-agent
```

探测边界案例类型：
- **长度边界**：空、超短、超长
- **格式边界**：纯 emoji、纯数字、无意义内容
- **矛盾指令**：逻辑冲突的请求
- **多语言混合**：中英混杂
- **敏感内容**：需要拒绝的请求

### 风险检查（路由增强）

```bash
python3 ~/.hermes/skills/.experiment_log/boundary_detector.py \
  --check coding-agent --query "你的超长query..."
```

返回：
- 风险等级（low/medium/high）
- 风险原因
- 替代方案建议

### 完整闭环（三阶段合一）

```bash
python3 ~/.hermes/skills/.experiment_log/skills_feedback.py \
  --full-loop coding-agent
```

一键执行：
1. 调用统计
2. 失败案例检查
3. 回归测试生成/更新
4. 边界签名扫描
5. 风险检查示例

## 统一 CLI

推荐使用 `skills_feedback.py` 统一入口：

```bash
# 全局统计
python3 ~/.hermes/skills/.experiment_log/skills_feedback.py --stats

# 扫描边界
python3 ~/.hermes/skills/.experiment_log/skills_feedback.py --scan coding-agent

# 风险检查
python3 ~/.hermes/skills/.experiment_log/skills_feedback.py \
  --check coding-agent --query "你的query"

# 完整闭环
python3 ~/.hermes/skills/.experiment_log/skills_feedback.py \
  --full-loop coding-agent
```

## Phase 3 与 skill-orchestrator 联动

```
用户请求
    ↓
skill-orchestrator 选 skill
    ↓
boundary_detector.check_risk(skill, query)
    ↓
风险高 → 提示用户 或 切换替代 skill
风险低 → 直接执行
    ↓
执行结果 → experiment-logger 记录
    ↓
下次请求时使用更新的边界
```

**触发时机：** skill-orchestrator 执行前自动调用边界检查

## 技术细节

> 详见 `references/technical-design.md` - 设计决策备忘录
> 详见 `references/three-phase-pattern.md` - 三阶段渐进实现模式
> 详见 `references/hl-theory.md` - HL 理论笔记（灵感来源）
> 详见 `references/seed-data-injection.md` - 冷启动边界签名的正确路径
> 详见 `references/query-api.md` - 新增查询 API（get_real_invocation_stats / get_skill_cooccurrence / skill_combinator 字段）

### 回归测试生成

```bash
# 方式 1: 使用 phase2.py（推荐）
python3 ~/.hermes/skills/.experiment_log/phase2.py \
  --generate-regression --skill coding-agent

# 方式 2: 使用 regression_generator.py
python3 ~/.hermes/skills/.experiment_log/regression_generator.py \
  --generate --skill coding-agent

# 运行回归测试
python3 ~/.hermes/skills/.experiment_log/regression_generator.py \
  --run --skill coding-agent
```

### A/B 测试

```bash
# 快速 A/B 测试
python3 ~/.hermes/skills/.experiment_log/phase2.py \
  --ab-test --skill-a coding-agent --skill-b claude-code

# 使用 ab_tester.py
python3 ~/.hermes/skills/.experiment_log/ab_tester.py \
  --create --name "coding对比" \
  --skill-a coding-agent --skill-b claude-code \
  --queries "帮我写排序" "分析代码性能" "优化SQL"

# 运行测试
python3 ~/.hermes/skills/.experiment_log/ab_tester.py \
  --run --test-id <ID>

# 列出测试
python3 ~/.hermes/skills/.experiment_log/ab_tester.py --list
```

### 完整闭环

```bash
# 一键检查某 Skill 的完整状态
python3 ~/.hermes/skills/.experiment_log/phase2.py \
  --full-loop --skill coding-agent

# 查看全局状态
python3 ~/.hermes/skills/.experiment_log/phase2.py --status
```

## Phase 2 与 skill-evolution-manager 联动

```
用户反馈 → skill-evolution-manager 分析
    ↓
experiment-logger 记录 quality_signals
    ↓
失败案例 → 回归测试生成
    ↓
回归测试失败 → skill-evolution-manager 提示需要进化
    ↓
进化后 → 重新运行回归测试验证
```

**触发联动：** "复盘并记录"、"这个 skill 变好了吗"、"运行完整闭环"
