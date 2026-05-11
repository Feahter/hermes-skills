---
name: skill-evolution-manager
description: 基于对话反馈持续改进 Skills 的核心工具。在对话结束时总结优化并迭代现有 Skills，将用户反馈和经验转化为结构化数据并持久化。
---

# Skill 进化管理器

整个 AI Skills 系统的"进化中枢"。

## 核心职责

| 职责 | 说明 |
|------|------|
| **复盘诊断** | 分析对话中 Skills 的表现 |
| **经验提取** | 将用户反馈转化为结构化 JSON |
| **智能缝合** | 将经验写入 `SKILL.md`，持久化 |

## 使用场景

**触发词**：
- `/evolve`
- "复盘一下刚才的对话"
- "记录一下刚才的问题"
- "把这个经验保存到 Skill 里"

## 工作流程

### 1. 经验复盘

当触发复盘时：

1. **扫描上下文**：找出用户不满意的地方（报错、风格不对）或满意的点
2. **定位 Skill**：确定是哪个 Skill 需要进化
3. **生成 JSON 结构**：
   ```json
   {
     "preferences": ["用户偏好，如：默认静音下载"],
     "fixes": ["修复项，如：Windows 下 ffmpeg 路径需转义"],
     "custom_prompts": "用户特定要求，如：执行前先打印预估耗时"
   }
   ```

### 2. 经验持久化

```bash
python scripts/merge_evolution.py <skill_path> <json_string>
```
将 JSON 增量写入目标 Skill 的 `evolution.json`

### 3. 文档缝合

```bash
python scripts/smart_stitch.py <skill_path>
```
将 `evolution.json` 转化为 Markdown，追加到 `SKILL.md` 末尾

### 4. 跨版本对齐

```bash
python scripts/align_all.py
```
一键遍历所有 Skills，将经验重新缝合到新版 `SKILL.md`

**使用时机**：`skill-manager` 批量更新后

## 核心脚本

| 脚本 | 功能 |
|------|------|
| `scripts/merge_evolution.py` | 增量合并：读取旧 JSON → 去重合并新数据 → 保存 |
| `scripts/smart_stitch.py` | 文档生成：读取 JSON → 生成 Markdown → 追加到 SKILL.md |
| `scripts/align_all.py` | 全量对齐：遍历所有 Skills → 还原经验 |

## 使用示例

### 简单复盘

```
你: "/evolve"
AI: 回顾对话...
    → 发现 yt-dlp 下载时用户抱怨需要手动静音
    → 生成 JSON：{"preferences": ["默认添加 --no-mtime"]}
    → 执行 merge_evolution.py
    → 执行 smart_stitch.py
    → 完成
```

### 指定 Skill 复盘

```
你: "复盘一下 ffmpeg-tool"
AI: → 扫描对话历史
    → 发现 Windows 路径处理有问题
    → 生成 fix：{"fixes": ["Windows 路径需用双引号包裹"]}
    → 持久化
```

### 批量对齐

```
你: "所有 Skills 更新后还原用户偏好"
AI: → 运行 align_all.py
    → 遍历所有 evolution.json
    → 逐一缝合到对应 SKILL.md
    → 完成
```

## 最佳实践

| 原则 | 说明 |
|------|------|
| **不直接修改正文** | 所有修正通过 `evolution.json`，避免升级丢失 |
| **多 Skill 协同** | 一次对话涉及多个 Skill，依次复盘 |
| **及时复盘** | 发现问题立即复盘，不要等到对话结束 |
| **小 bug 立即修** | 在实现过程中发现 bug（如 word boundary 误匹配），当场修掉，不需要单独开 issue 或 TODO |
| **立即执行优于事后归档** | 当用户说"做"时，直接 patch + 验证，复杂的 evolution.json 流程适合多人协作，单 agent 自己进化时直接 in-place 更新更高效 |

## 经验 JSON Schema

```json
{
  "preferences": ["用户偏好列表"],
  "fixes": ["已知问题修复"],
  "custom_prompts": "特定提示词",
  "updated_at": "2024-02-03T23:00:00Z"
}
```

## 与 experiment-logger 的联动 (Phase 2)

skill-evolution-manager 负责"经验提炼 + 写入 SKILL.md"，experiment-logger 负责"数据采集 + 质量追踪"。

### 联动流程

```
用户反馈
    ↓
skill-evolution-manager: 分析反馈，提取经验
    ↓
experiment-logger: 记录 quality_signals
    ↓
fail_cases 积累 → 触发 regression_generator
    ↓
回归测试失败 → skill-evolution-manager 提示需要进化
```

### 联动触发词

- "复盘并记录" - 同时调用两者
- "生成本 skill 的回归测试" - experiment-logger 生成，evolution-manager 审核
- "这个 skill 变好了吗" - experiment-logger 对比回归测试结果

## Phase 0: 冷启动 - 种子数据生成

当 skill 调用记录 < 5 条时，boundary 签名无法可靠生成（数据不足）。此时需要主动注入种子数据，而非等待真实使用积累。

### 冷启动流程

```
新 skill 或数据不足
    ↓
扫描 SKILL.md 的触发场景关键词
    ↓
基于触发场景生成真实格式的调用记录
    ↓
写入 invocations/ 目录
    ↓
boundary_detector.scan() 从种子数据学习边界
    ↓
后续真实使用覆盖种子数据（无侵入）
```

### 种子生成脚本

`~/.hermes/skills/.experiment_log/scripts/seed_generator.py`（由 experiment-logger Phase 3 提供）：

```bash
# 生成单个 skill 的种子数据（默认5条）
python3 ~/.hermes/skills/.experiment_log/skills_feedback.py --seed <skill_name>

# 批量生成所有无数据 skills 的种子
python3 ~/.hermes/skills/.experiment_log/skills_feedback.py --seed-all

# 查看当前数据状态
python3 ~/.hermes/skills/.experiment_log/skills_feedback.py --stats
```

### 触发条件

- 新安装 skill 且无调用记录
- 现有 skill 调用记录 < 5 条
- boundary 签名缺失（`boundary_detector.check_risk()` 返回 `"boundary_data": false`）

### 注意事项

- 种子数据是"保底"而非"真实"，用于冷启动
- 真实使用数据会自然覆盖种子（通过 `query_hash` 去重）
- 不要对种子数据做 A/B 测试（mock executor 无法执行业务逻辑）

## 与 experiment-logger 的联动 (Phase 3)

Phase 3 将 boundary_detector 集成到 skill-orchestrator 的路由层，形成预防性反馈回路：

```
用户请求
    ↓
skill-orchestrator 选 skill
    ↓
boundary_detector.check_risk(skill, query)  ← 前置拦截
    ↓
HIGH 风险 → 跳过 + 切换备选 skill
MEDIUM 风险 → 警告 + 用户确认
LOW 风险 → 直接执行
    ↓
执行结果 → experiment-logger 记录
    ↓
boundary_detector.scan() 从新数据中更新边界签名
    ↓
下次请求时使用更准确的边界
```

**关键区别：**
- Phase 2：被动反应（失败后复盘）
- Phase 3：主动预防（失败前拦截）

### Phase 3 联动触发词

- "检查这个 skill 的风险" → boundary_detector.check_risk
- "扫描 skill 的边界" → boundary_detector.scan
- "完整闭环" → skills_feedback.py --full-loop

## 与其他 Skill 配合

| 场景 | 流程 |
|------|------|
| 创建 → 管理 → 进化 | `github-to-skills` → `skill-manager` → `skill-evolution-manager` |
| 更新后还原偏好 | `skill-manager update` → `skill-evolution-manager align` |
| 持续改进 | 每次对话后 `/evolve` |

## 注意事项

- `evolution.json` 独立于原仓库，不被 `skill-manager` 更新覆盖
- `align_all.py` 用于版本升级后的经验还原
- 保持 JSON 结构简洁，避免过度定制

## Pitfalls

- **Hygiene 误判（本次最大教训）**：名称/描述表面相似 ≠ 实际重叠。talent-mind 分析常发现大量"潜在合并/删除项"，但读文件后发现多数是误判——如 create vs modify（角色不同）、纵向钻取 vs 横向分析（目的不同）、中文 vs 英文（触发场景不同）。** Hygiene 工作流必须强制读文件验证，不能跳过直接执行分析结果。**
- **推断误差**：自动推断不准确时，在 SKILL.md 加显式声明
- **反馈噪声**：`~/.hermes/.skill_combinator_feedback.json` 长期积累后 task_key 前缀匹配可能不准，可定期清理
- **Subagent 模型路由不验证**：`delegate_task` 的 `model` 参数不校验模型 ID 是否存在于 provider，指定无效 model ID 时静默降级到默认模型
