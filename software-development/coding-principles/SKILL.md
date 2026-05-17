---
name: coding-principles
description: 编码原则与补丁规范。触发：编码任务、代码修改、bug修复。自动注入，零废话。
trigger: "编码任务、修改代码、修复bug、创建/更新代码文件。AGENTS.md 规则：编码任务自动装载，无须询问。"
language: 中文
---

# coding-principles

## Trigger
当用户发起编码任务、要求修改代码、修复 bug、或创建/更新文件时，自动注入此原则。无须请求，直接装载。

## Principles

**目标**：产出像人写的代码补丁。

### 铁律
1. 最小改动，最直观方案。
2. 不引入回归，兼容现有调用方。
3. 可读 > 健壮 > 性能 > 扩展。
4. 能复用不造轮子。

### 开工前
- 不确定就问，不猜。假设必须显式说出。
- 需求多解读时列出选项让用户选。
- 必须反问：多种可行方案、接口/Schema模糊、调用方影响不明、代码与需求矛盾。
- 卡壳就停，指出哪里不清。

### 改代码
- 每行改动对应需求。
- 严格模仿现有命名、缩进、括号、错误处理模式，哪怕它不优雅。
- 不改动区域代码绝不动，除非：
  * ±3行内明显废弃/注释代码且相关，可删并注"相邻清理"；
  * ±3行内笔误，可修并注"修正笔误"。
- 只清自己改动产生的孤儿import/变量，无关死代码只提不动。
- 大段简化必须先提案，同意再做。

### 简洁第一
- 不加没要的功能，不抽象单次使用逻辑，不做无要求的"灵活性"。
- 不为不可能场景加错误处理。
- 过度设计就简化。

### 反AI痕迹
- 不升级语法风格（循环不转函数式，命令式不转声明式，除非要求）。
- 不主动补类型注解、日志、埋点、监控注释。
- 不起长名，不拆单层函数为多层。

## §Absorbed: Karpathy 编码原则

`karpathy-coding-principles/` has been absorbed here as `references/karpathy-coding-principles.md`.

> Karpathy 编码四原则 — Think Before Coding / Simplicity First / Surgical Changes / Goal-Driven Execution

### Summary of Karpathy's 4 Principles

| Principle | Core Idea |
|-----------|-----------|
| **Think Before Coding** | Don't assume, don't hide confusion. Present tradeoffs before acting. |
| **Simplicity First** | Minimum code to solve the problem. No add-ons未被要求的功能。 |
| **Surgical Changes** | Only touch what must be touched. Clean up orphans from your own changes. |
| **Goal-Driven Execution** | Translate requests into verifiable success criteria first, then iterate. |

### When Karpathy Principles Add Value
- **Plan before coding**: present assumptions + tradeoffs before touching code
- **Evaluate a change**: is this minimal or is it over-engineered?
- **Multi-step task**: define success criteria before executing

### Quick Workflow (from Karpathy)
```
用户开发请求
  → 原则1: 编码前（假设清单 + 方案选择）
  → 用户确认
  → 原则2: 设计方案（最小实现路径）
  → 开始执行
  → 原则3: 手术式修改（每行追溯到原始请求）
  → 原则4: 目标驱动（可验证标准 + 循环验证）
  → 交付
```

For full Karpathy content with examples, triggers, and limitations → `references/karpathy-coding-principles.md`

### 执行
- 读代码→规划→实现→验证，一步一清。
- 多步任务先列"步骤→验证结果/用例→代码位置"，打勾闭环。
- 修bug先写复现测试。
- 最小成本验证：跑几条用例、对应语言编译/解释器检查、肉眼diff。改动牵涉签名则快速搜引用确认兼容。

### 输出
- 思考对话中文，注释跟随文件现有风格（无注释则中文写"为什么"）。
- 只贴改动区+≤3行上下文，不重复未改代码。
- 多方案标推荐，简要对比。
- 不主动加新依赖，除非必须并说明代价。
