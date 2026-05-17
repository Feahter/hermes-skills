# TencentDB-Agent-Memory 研究归档

**日期：** 2026-05-16
**结论：** 主动模式意图识别压缩，暂不适合 Hermes 体系，与其系统设计哲学违背

---

## 一、研究背景

目标：评估 TencentDB Mermaid Canvas 对 Hermes 的参考价值。

**TencentDB Mermaid Canvas 核心机制：**
- Tool call 后实时写文件，Mermaid 图维护
- Pipeline L1→L3 自动提取（需要外部 LLM）
- Short-term context offloading
- Agent 可通过 ref marker 召回历史信息

---

## 二、架构差异分析（致命问题）

| 维度 | TencentDB | Hermes |
|------|-----------|--------|
| 压缩模式 | **主动推送**（每次 tool call 后实时写文件）| **被动拉取**（threshold 超才 compress）|
| Offloading 触发 | 工具调用后立即 | 必须 compress() 被调用 |
| 召回触发 | LLM pipeline 自动判断 | Agent 自觉展开 |

**本质差异：** Hermes 的 tool results 先入 messages，再等待 should_compress() 检查。TencentDB 的 offloading 在 tool call 和 LLM 之间就已经发生。

---

## 三、方案评估

| 方案 | 可行性 | 风险 | 结论 |
|------|--------|------|------|
| A: ContextCompressor 加 offloading | 被动触发效果打折 | 改既有逻辑 | 不推荐 |
| B: CanvasContextEngine 插件 | 插件隔离 | 召回触发机制未解决 | 暂缓 |
| C: Prefetch 增强 | 价值依赖方案 B | - | 依赖 B |
| D: 改 run_agent.py 加 hook | 架构上不可行 | Core 改动 15k LOC | 不推荐 |

---

## 四、实验验证（T1-T5）

| 测试 | 输入 | 结果 |
|------|------|------|
| T1 | 有 summary 的 ref marker | ✓ agent 直接回答正确 |
| T2 | 无 summary 的 ref marker | 承认无法回答 |
| T3 | 描述 canvas_expand（未注册）| "tool doesn't exist in my actual toolset" |
| T4 | 直接给文件路径 | ✓ agent 正确召回 |
| T5 | 让 agent 从 node_id 推导路径 | ✗ 超时 |

**关键发现：**
- Summary 够好 → agent 不需要召回（上行）
- canvas_expand 必须在 tools schema 真实注册，描述无效
- Agent 无法从 node_id 自行推导文件路径

---

## 五、核心假设未验证

**召回触发机制未解决：**
- TencentDB：LLM pipeline 自动判断"需要召回"
- Hermes 方案 B：如果靠 agent 自觉 → summary 不好时 agent 不知道要召回；如果靠压缩逻辑判断 → 需要语义分析，接近 LLM 任务，违背本地优先原则

**最坏情况比现状差：**
- 不 offload → compress 时统一丢
- 方案 B → 需要时也可能丢（agent 不展开）

---

## 六、结论

**主动模式意图识别压缩，暂不适合 Hermes 体系，与其系统设计哲学违背。**

理由：
1. Hermes 是被动压缩架构，无主动推送的架构基础
2. 召回触发机制依赖外部 LLM 或 agent 自觉，两者在本地优先原则下均不可行
3. 最坏情况比现状差（信息在需要时也丢失）
4. 等效替代存在：优化 summary 质量效果等同，风险更低

**未来如果 Hermes 引入 active compression 机制（而非被动 threshold），可重新评估。**

---

## 七、相关文件

- `run_agent.py` — 核心 agent loop（15k LOC）
- `agent/context_compressor.py` — 现有压缩引擎（1556 行）
- `plugins/context_engine/` — 引擎插件目录（已有 lcm 引擎）
