# skill-evolution-manager.evals

> Skill: skill-evolution-manager
> Description: 基于对话反馈持续改进 Skills 的核心工具。在对话结束时总结优化并迭代现有 Skills，将用户反馈和经验转化为结构化数据并持久化。
> Last updated: 2026-05-13

---

## POSITIVE — 应该触发

| # | 触发词 | 预期行为 | 边界条件 |
|---|--------|----------|----------|
| P1 | "/evolve" | 触发 skill-evolution-manager | 明确命令 |
| P2 | "复盘一下刚才的对话" | 触发 skill-evolution-manager | 复盘请求 |
| P3 | "记录一下刚才的问题" | 触发 skill-evolution-manager | 记录问题 |
| P4 | "把这个经验保存到 Skill 里" | 触发 skill-evolution-manager | 经验持久化 |
| P5 | "复盘并记录" | 触发 skill-evolution-manager | 复盘 + 记录 |
| P6 | "这个 skill 变好了吗" | 触发 skill-evolution-manager | 检查 skill 改进 |
| P7 | "把刚才的反馈更新到 skill" | 触发 skill-evolution-manager | 反馈更新 |
| P8 | "所有 skills 更新后还原用户偏好" | 触发 skill-evolution-manager | 批量对齐 |

---

## NEGATIVE — 不应触发

| # | 触发词 | 不触发原因 | 正确路由 |
|---|--------|------------|----------|
| N1 | "帮我进化一下代码" | 代码进化 ≠ skill 进化 | coding-agent |
| N2 | "解释一下 skill 是什么" | 概念解释不需要 evolution | 直接回答 |
| N3 | "创建个新 skill" | 创建 ≠ 进化 | skill-creator |
| N4 | "检查 skill 的风险" | 风险检查是 boundary_detector | boundary_detector / experiment-logger |
| N5 | "这个任务用什么 skill 好" | skill 推荐是 orchestrator 的活 | skill-orchestrator |

---

## BOUNDARY — 边界情况

| # | 触发词 | 边界描述 | 预期行为 |
|---|--------|----------|----------|
| B1 | "复盘" (单独一字，无上下文) | 极短，无对话历史上下文 | 应确认是复盘哪个 skill 或哪段对话 |
| B2 | "保存这个经验" | 未指明哪个 skill | 应追问哪个 skill |
| B3 | "/evolve coding-agent" | 命令 + skill 名但无反馈内容 | 触发并等待用户提供反馈内容 |
| B4 | "这个 skill 最近表现怎么样" | 表现查询 vs 主动进化 | 触发，但只是查询不需要写入 |