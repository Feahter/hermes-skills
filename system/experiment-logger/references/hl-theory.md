# Heuristic Learning 理论笔记

来源：https://trinkle23897.github.io/learning-beyond-gradients/

## 核心顿悟

> "学习" = 维护一个可进化的反馈回路

这个定义把"学习"从"优化方法"的范畴拉到了"系统设计"的范畴。

## 对 Hermes Skills 的关键洞察

### 当前 Skills 生态缺少的三层基础设施

```
✗ experiment_log     — 每次调用的输入/输出/质量记录
✗ trial_replay       — Skill A 在 case X 失败，能回放并测试 Skill B 吗？
✗ boundary_detect    — 当前 Skill 在什么输入上会失效？有没有自动探测？
```

### HL vs Deep RL 的本质区别

| | Deep RL | Heuristic Learning |
|--|---------|-------------------|
| Policy | 神经网络参数 | 代码（规则、状态机） |
| Update | 梯度下降 | 直接代码编辑 |
| Memory | Replay buffer | 显式 trial 记录 |
| 泛化能力 | 强 | 弱（但可解释性强） |

### HL 真正 work 的场景

- 低熵 + 可描述几何 + 反馈明确
- 例如：Breakout（几何规则清晰）、Ant（物理仿真可描述）

### Montezuma 暴露的失败边界

- 长期记忆需求
- 宏动作组合爆炸
- 可恢复搜索状态需求

Plain `if-else` 无法胜任。

## 天才思维视角下的 HL

用 talent-mind 三层递归审视：

### STEP 1: 矛盾探测器

- **原始结论**：Coding Agent 让 HL 的维护成本下降，HL > Deep RL
- **反例**：当规则系统膨胀到 10 万行时，Agent 本身成为维护对象
- **张力**：HL work 的场景恰好是 Hermes 所在的场景（低熵 + 明确反馈）

### STEP 2: 表征转换

- **工程视角**：用 Coding Agent 替代梯度下降
- **数学视角**：HL 是离散搜索，Deep RL 是凸优化
- **关键差集**：不是优化方法的选择，而是"学习到底在优化什么"

### STEP 3: 元认知钩子

- "HL vs Deep RL" 二元对立本身就是错误分类
- 真正的问题是：**你的 agent 系统是否拥有"持续迭代"的基础设施？**
