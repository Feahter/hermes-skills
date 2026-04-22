# Coding-Agent Learnings

*每次执行后追加记录*

---

## 验证过的有效模式

### Claude Code -p 非交互模式
```bash
claude -p "task description" \
  --output-format stream-json \
  --no-session-persistence \
  --permission-mode bypassPermissions
```
- ✅ 单次任务，不需要 TTY
- ✅ 输出到 stdout，可以重定向
- ⚠️ 需要明确指定 `--permission-mode bypassPermissions` 否则会卡住

### 工作目录隔离
- `cd $WORKDIR && claude -p ...` — 进程在正确目录启动
- 绝对路径隔离：不同项目的 agent 不会互相干扰

---

## 踩过的坑

### Claude Code -p 模式没有 TTY 时的权限问题
- **现象**：`Permission to use tool Bash is required` 卡住
- **解法**：`--permission-mode bypassPermissions`
- **注意**：仅限可信目录（`/tmp`、`~/project/`）

### JSON 输出格式不稳定
- `--output-format json` 有时返回的不是合法 JSON（夹杂 ANSI color codes）
- **解法**：用 `--output-format text` 或管道处理 ANSI

### opencode run 非交互模式
- `opencode run "task"` — 有效，但需要检查版本
- 当前版本 1.3.0，测试可用

---

## 待验证

- [ ] OpenCode 非交互模式 vs Claude Code 的质量对比
- [ ] 多模型路由：何时用 Claude，何时用 OpenCode
- [ ] 子 session 的上下文保留效果

---

## 使用统计

| 日期 | Session数 | Agent | 任务类型 | 状态 |
|------|---------|-------|---------|------|

---

## 2026-04-17 · AionUI Patterns 研究

**来源**: https://github.com/aionui/aionui (Apache-2.0)
**路径**: `~/.openclaw/workspace/code/aionui-patterns/`

### 核心发现

| 模式 | 解决的问题 | 关键设计 |
|------|-----------|---------|
| StreamingBuffer | 流式 LLM 写库性能 | 双触发条件（时间+数量）批量写 |
| ThinkTagDetector | 国产模型推理标签过滤 | MiniMax 特殊格式：无开标签 |
| ShellEnv | Electron PATH 缺失 | 白名单继承+干扰变量清理 |
| StructuredCommandParser | 替代 Function Calling | 标签格式比 JSON 更 LLM 容错 |
| AgentResponsePipeline | 可组合后处理 | 单步失败不中断管道 |

### 最重要的一条
**MiniMax M2.5 格式**：`</think>` 前所有内容都是推理 → 用 `/^[\s\S]*?<\/\s*think(?:ing)?\s*>/i` 匹配

### OpenClaw 直接可用
- `think-tag-detector.ts`: MiniMax M2 模型输出过滤
- `structured-command-parser.ts`: 飞书消息指令解析框架
- 报告: `memory/research/aionui-patterns-2026-04-17.md`

---

## 2026-04-19 · Understand-Anything 研究

**来源**: https://github.com/anthropics/understand-anything
**路径**: `~/.openclaw/workspace/Understand-Anything/`
**报告**: `research/understand-anything-analysis.md`

### 核心发现（Agent/知识图谱方向最值得借鉴）

| 模式 | 应用场景 | 关键设计 |
|------|---------|---------|
| **Tree-Sitter WASM** | 本地代码解析 | `createRequire(import.meta.url)` 解决 WASM 路径；`init()` 时并行预加载所有语言 |
| **知识图谱 Schema** | 代码库结构化 | 节点5类 + 边18种 + Zod 验证 + Layers/Tours 双轨导航 |
| **Context 构建器** | LLM prompt 模板 | `buildChatContext()` 从 query 扩展1-hop 节点 + 边 |
| **渐进增强搜索** | 功能分级 | fuzzy search 先上，semantic (embedding) 可选激活 |
| **磁盘中间结果** | 大任务 context 管理 | Agent 结果写入 `.understand-anything/intermediate/`，不堆砌 context |
| **Zustand Store** | React 状态 | 轻量，比 Redux 简洁；`tourActive` + `currentTourStep` + `tourHighlightedNodeIds` 三字段协同 |
| **模型分级路由** | 成本优化 | sonnet 处理简单任务（project-scanner），opus 处理复杂（architecture-analyzer） |

### 最重要的一条
**图谱 + LLM Prompt 模板是理解任意代码库的通用范式**：将静态分析结果（AST、依赖图）建模为知识图谱，用 context builder 动态构建 LLM prompt，支持 explain/onboard/diff/chat 多场景。feZ 的八字引擎或 Autoresearch 也可以用类似思路：把分析结果固化为结构化图谱，而非每次重新推理。

### feZ 项目可直接用的
- **Tree-Sitter 集成模式**：`createRequire` + WASM 预加载 → 本地代码解析不依赖 API
- **渐进增强架构**：先 fuzzy 搜索，再加 embedding → 先跑通再升级
- **Context 构建分离**：每个 skill 有独立的 `buildXxxContext()` → 职责单一、易测试
