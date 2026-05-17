# Sub-Agent Swarm Schema（归档自主动路由记忆系统）

> 来源：DeepSeek Chat / 2026-05-07
> 状态：归档，不立即落地，仅作参考
> 决策：子代理 Schema 和触发条件有价值，LLM拆词+聚合器暂缓

---

## 子代理任务输入 Schema

```json
{
  "sub_agent_id": "string",        // 唯一标识，如 "frontend_search_01"
  "domain_filter": "string",       // 领域标签，如 "frontend"
  "query_intents": ["string"],     // 查询意图列表
  "max_results": 5,                // 最大召回数
  "output_format": "summary_list", // 输出格式
  "token_budget_per_result": 150,  // 每条结果的 token 上限
  "instruction_hint": "string"     // 补充指令，如"返回可直接执行的步骤和常见错误"
}
```

---

## 子代理输出 Schema

```json
{
  "status": "success | no_match | error",
  "findings": [
    {
      "source_id": "string",           // 来源标识，如 "wiki://frontend-dark-mode"
      "relevance_score": 0.95,          // 0-1 相关性分数
      "summary": "string",              // 可消化的摘要
      "key_actions": ["string"],        // 关键动作列表
      "caveats": ["string"]             // 注意事项
    }
  ],
  "no_more_relevant": false          // true = 已无更多相关内容
}
```

---

## 并发拆分触发条件

满足任一即触发并发子代理：

| 条件 | 说明 |
|------|------|
| 多领域 | 路由返回 2+ 不同领域 |
| 多子查询 | 拆词器生成 ≥ 3 个高权重独立意图 |
| 深度分析 | 需要全文精读并对比（如方案对比） |
| 大范围 | 需遍历大量条目，可按时间/标签分片 |

简单单一查询走串行，节省资源。

---

## Hermes 当前映射

| 组件 | Hermes 现状 | 行动 |
|------|------------|------|
| 子代理输入 Schema | 无 | 参考归档，待需要时启用 |
| 子代理输出 Schema | 无 | 同上 |
| 并发触发条件 | 无 | 同上 |
| LLM 拆词器 | 无（直接检索） | **暂缓**，收益不明确 |
| 聚合器 | 无 | **暂缓**，需额外 LLM 调用 |
