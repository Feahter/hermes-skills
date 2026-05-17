# skill-orchestrator.evals

> Skill: skill-orchestrator
> Description: 技能编排 — 分析需求调用最合适skill。触发：需要多skill协作时。
> Last updated: 2026-05-13

---

## POSITIVE — 应该触发

| # | 触发词 | 预期行为 | 边界条件 |
|---|--------|----------|----------|
| P1 | "帮我处理这个PDF并生成报告" | 触发 skill-orchestrator | 多技能组合（pdf + 生成） |
| P2 | "分析这些数据并可视化" | 触发 skill-orchestrator | 分析 + 可视化双技能 |
| P3 | "优化这段代码并生成文档" | 触发 skill-orchestrator | 优化 + 文档双技能 |
| P4 | "帮我完成这个任务，需要几个skill" | 触发 skill-orchestrator | 用户不确定用什么 |
| P5 | "这个工作流需要哪些skill" | 触发 skill-orchestrator | 技能发现场景 |
| P6 | "处理Excel、分析趋势、生成图表、发邮件" | 触发 skill-orchestrator | 多步骤多技能链 |
| P7 | "帮我规划一下怎么做" | 触发 skill-orchestrator | 规划 = 编排前提 |
| P8 | "这个需求我不知道用什么skill" | 触发 skill-orchestrator | 明确说不知道 |

---

## NEGATIVE — 不应触发

| # | 触发词 | 不触发原因 | 正确路由 |
|---|--------|------------|----------|
| N1 | "帮我读取这个PDF" | 单一技能不需要编排 | pdf skill |
| N2 | "用xlsx处理这个表格" | 用户明确指定了具体技能 | 直接调用 xlsx |
| N3 | "什么是机器学习" | 纯信息查询不需要技能 | 直接回答 |
| N4 | "你好" | 闲聊不需要技能 | 直接回复 |
| N5 | "帮我写一段Python代码" | 单一编码任务不需要编排 | coding-agent |
| N6 | "用pdf skill处理这个文件" | 用户明确指定了 skill | 直接调用 pdf |

---

## BOUNDARY — 边界情况

| # | 触发词 | 边界描述 | 预期行为 |
|---|--------|----------|----------|
| B1 | "帮我处理这个" | 无后缀，任务不明确 | 应追问明确任务，而不是触发编排 |
| B2 | "用skill-orchestrator分析" | 明确指定 orchestrator 但描述模糊 | 触发但需追问具体需求 |
| B3 | "处理文件" (无格式信息) | 无法判断是否多技能 | 先判断文件类型再决定 |
| B4 | "我需要整理一下桌面" | 可能是单技能也可能是多技能 | 判断是否需要多 skill 协作再触发 |