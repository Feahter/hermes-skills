# Model Selection (Tiered, Model-Agnostic)

## Principle
Use the **cheapest capable tier** for the job. Escalate only when:
- the task repeatedly fails at a cheaper tier, or
- correctness materially matters (risk, finance, security), or
- the task requires deep synthesis/architecture.

Avoid naming specific models in guidance. Treat "model" as a **tier**.

---

## Tiers (conceptual)
- **Tier 1 (cheap / frequent):** routine formatting, lightweight summaries, single-script cron runs.
- **Tier 2 (general):** multi-file edits, orchestration, non-trivial debugging.
- **Tier 3 (deep):** architecture, risk analysis, complex planning.

---

## Escalation policy
- Start at Tier 1 for automation.
- Escalate to Tier 2 only after *observed* failure or clear complexity.
- Escalate to Tier 3 only with justification.

If you need user approval to change a global default, ask. Otherwise prefer local overrides per job.

---

## Anti-patterns
- Using Tier 3 for simple cron/heartbeat tasks.
- Re-running the same expensive analysis every schedule tick.
- Asking the user to choose a model for routine tasks (choose the cheapest tier that works).

---

## OpenRouter 模型推荐（动态更新）

> ⚠️ 以下为静态快照，实际以 cron 自动更新为准。上次更新：2026-05-11
> 自动更新 cron：`openrouter-model-refresh`（每周一 09:00 Asia/Shanghai）

### 推荐分层（按场景）

| 层级 | 场景 | 推荐模型 | 理由 |
|------|------|----------|------|
|  **免费主力** | 通用 Agent、编程、推理 | `inclusionai/ring-2.6-1t:free` | 564B tokens验证（总榜#5），262K context，高效响应，MoE 1T/63B active |
| **免费备选** | 需要更大 context | `nvidia/nemotron-3-super-120b-a12b:free` | 564B tokens验证（总榜#1），262K/1M context，AIME/SWE-Bench SOTA |
| **免费编程** | 代码生成/调试 | `minimax/minimax-m2.5:free` | SWE-Bench 80.2%，197K context，编程 SOTA，新晋 |
| **免费大context** | 长文档/视觉 | `openrouter/owl-alpha:free` | 1.05M context（免费最高），工具调用，Agentic 兼容 Claude Code/OpenClaw |
| **免费综合** | Router自动选最优 | `openrouter/free` | 根据请求类型自动路由 |
| **付费旗舰** | 高难度推理/架构 | `openai/gpt-5.5` 或 `anthropic/claude-opus-4.7` | GPT-5.5: 1.05M context；Claude: 复杂代码库/多阶段调试 |
| **付费性价比** | 编程+Agent | `deepseek/deepseek-v4-flash` | $0.14/$0.28 per 1M tokens，MoE 284B |

### 价格参考（美元/百万Tokens）

| 模型 | Input | Output | Notes |
|------|-------|--------|-------|
| ring-2.6-1t | $0 (免费) | $0 (免费) | 免费主力，MoE 1T/63B active |
| nemotron-3-super | $0 | $0 | 免费备选，NVIDIA开源 |
| minimax-m2.5 | $0 | $0 | 免费编程，SWE-Bench 80.2% |
| owl-alpha | $0 | $0 | 免费大context，1.05M context |
| deepseek-v4-flash | $0.14 | $0.28 | 付费性价比首选 |
| gpt-5.5 | $5 | $30 | 付费旗舰，1.05M context |
| claude-opus-4.7 | $5 | $25 | 旗舰，全能 |

### 快速选型决策树

```
任务类型 = 轻量任务(cron/heartbeat/format)?
└→ openrouter/free 或 ring-2.6-1t:free

任务类型 = 编程/Agent?
├─ 需要最高性价比 → minimax-m2.5:free
├─ 需要1M+ context → gpt-5.5
└─ 需要最高正确率 → claude-opus-4.7

任务类型 = 长文档/大context(>200K)?
├─ 需要最高免费context → owl-alpha:free (1.05M)
└→ nemotron-3-super:free (1M context)

任务类型 = 高难度推理/架构?
└→ gpt-5.5 或 claude-opus-4.7

任务类型 = 追求性价比(付费)?
└→ deepseek-v4-flash ($0.14/$0.28)
```

### 禁用规则
- 🚫 不要用 claude-opus-4.* / gpt-5.5 做 cron/heartbeat（成本 $5-30 per 1M）
- 🚫 不要在免费模型返回 429 时盲目重试（rate limit），等1分钟或换模型
- 🚫 不要用 GPT-OSS 120B 做长对话（131K context，容易超限）
- 🚫 不要用 owl-alpha 做简单格式化任务（1.05M context 预热慢，适合复杂任务）
- ⚠️ ling-2.6-flash 已下线（免费期结束），请切换到 ring-2.6-1t:free

---

*此文件由 cron job 自动更新，修改会自动覆盖*
