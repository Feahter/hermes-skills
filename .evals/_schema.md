# Skill Evals — 行为契约测试

> **核心原则：** Skill Eval 测的是「路由正确性」，不是「执行正确性」
> 核心问题：这个触发词在什么边界条件下会路由错误？

## 目录结构

```
~/.hermes/skills/.evals/
├── _schema.md              # 本文件 — 格式定义
├── _index.md               # 索引 — 所有 skill evals 列表
├── coding-agent.eval.md    # 每个 skill 一个文件
├── skill-orchestrator.eval.md
├── browser.eval.md
├── git.eval.md
├── deep-research.eval.md
└── ...                     # 后续扩展
```

## Eval Case 格式

每个 skill 文件包含三类 eval：

```markdown
## POSITIVE — 应该触发

| # | 触发词 | 预期行为 | 边界条件 |
|---|--------|----------|----------|
| P1 | "帮我写一个快速排序" | 触发 coding-agent | — |
| P2 | "写段Python代码处理这个" | 触发 coding-agent | 短 query 也应触发 |

## NEGATIVE — 不应触发

| # | 触发词 | 不触发原因 | 正确路由 |
|---|--------|------------|----------|
| N1 | "解释一下快速排序的原理" | 纯解释不需要写代码 | 无需 skill 或选其他 |
| N2 | "coding-agent 是什么" | 查询定义不是调用 | 无需 skill |

## BOUNDARY — 边界情况

| # | 触发词 | 边界描述 | 预期行为 |
|---|--------|----------|----------|
| B1 | "写" (单独一字) | 极短 query | 应触发但需追问补充 |
| B2 | "帮我写代码/帮我写脚本" | 重复触发词 | 应合并处理 |
```

## 字段说明

### POSITIVE（正向触发）

| 字段 | 说明 |
|------|------|
| 触发词 | 实际用户query，真实场景 |
| 预期行为 | 这个 query 应该触发哪个 skill |
| 边界条件 | 可选 — 触发词在什么额外条件下有效 |

### NEGATIVE（负向触发）

| 字段 | 说明 |
|------|------|
| 触发词 | 会误触发但实际不该触发的 query |
| 不触发原因 | 为什么这个 query 不该触发此 skill |
| 正确路由 | 正确的 skill 或 无需 skill |

### BOUNDARY（边界情况）

| 字段 | 说明 |
|------|------|
| 触发词 | 边界 case query |
| 边界描述 | 什么使它成为边界（极短/极长/歧义/多义） |
| 预期行为 | skill 应该怎么处理（触发+特殊处理/拒绝+提示/降级） |

## 编写规范

1. **至少 3 条 POSITIVE + 2 条 NEGATIVE + 1 条 BOUNDARY**
2. **触发词必须来自真实 query，禁止臆造**
3. **每条 eval 必须有具体触发词，不是抽象描述**
4. **更新时机：** skill 修改后 / 用户反馈路由错误时

## 使用方式

```
skill-creator 创建/修改 skill → 编写/更新 .evals/{skill}.eval.md
                                               ↓
experiment-logger 运行边界探测 → 对比 eval vs 实际路由行为
                                               ↓
路由偏差 → 更新 skill description 或 eval
```

## 验证

```bash
# 查看某 skill 的 evals
cat ~/.hermes/skills/.evals/coding-agent.eval.md

# 更新索引
python3 ~/.hermes/skills/.experiment_log/skills_feedback.py --scan <skill>
```