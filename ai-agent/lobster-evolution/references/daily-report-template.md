## 每日模式报告 2026-04-04 10:00
- 最近7天 12 个Session，247条Query

### 高频意图（≤15字）
- 帮我查一下天气 ×6
- 搜索 GitHub ×4
...

### 高频中文词
- 飞书 ×18
- 日历 ×12
- 八字 ×9
...
```

**触发频率**：每天首次心跳必执行

---

### 维度2：自动技能提案生成 ✅ 已部署

**现状**：基于维度1的挖掘结果自动生成提案，存 `proposals/`

**提案生成流程**（`skill-proposer.py`）：
1. 读取 `daily-mining.md`
2. 分析中文高频词，按领域聚合
3. 分析高频短Query，识别重复指令模式
4. 按优先级规则生成提案

**提案类型与优先级规则**：

| 类型 | 触发条件 | 优先级 | 建议动作 |
|------|---------|--------|---------|
| 高频领域 | 中文词累计≥30次/7天 | 🔴 high | 评估是否已有覆盖，提出新建或优化建议 |
| 高频领域 | 中文词累计≥10次/7天 | 🟡 medium | 观察2周再决策 |
| 高频指令 | 短Query≥7次/7天 | 🔴 high | 优化现有Skill触发词或新建Skill |
| 高频指令 | 短Query≥5次/7天 | 🟡 medium | 纳入监控 |
| 意图突增 | 某领域词突增≥3次/天 | 🟡 medium | 关注趋势 |

**当前实际覆盖情况**（来自最新提案报告）：
- 节气 ×73 → `chinese-name-lookup` 已覆盖 ✅
- high_freq_query 多种 → 子Session代码片段优化
- 命理 ×10, 搜索 ×14 → 中频，建议继续观察

**输出位置**：`~/.openclaw/workspace/.state/evolution/proposals/proposals-YYYYMMDD.md`

---

### 维度3：错误自愈循环 🚧 部分已部署（待增强LLM判断）

**现状**：`self-healer.py` 已部署，能识别7种已知错误模式并生成修复建议

**自愈流程**（`self-healer.py`）：
```
读取 .learnings/ERRORS.md
    ↓
遍历所有 status=pending 的错误条目
    ↓
对每个错误尝试匹配 KNOWN_PATTERNS
    ↓
├─ 能匹配 → 标记为"可自愈"，记录修复类型和描述
└─ 不能匹配 → 标记为"需人工"
    ↓
生成 self-healer.md 报告
```

**已实现的7种自愈模式**：

| 错误关键词 | 修复类型 | 动作描述 |
|-----------|---------|---------|
| `path.*not found` | path_fix | 路径不存在，列出正确路径供参考 |
| `command not found` | command_fix | 命令未找到，更新 TOOLS.md 中的路径 |
| `encoding.*error` | encoding_fix | 编码错误，使用 qclaw-text-file 重写 |
| `No such file or directory` | path_fix | 文件不存在，提示可能路径错误 |
| `SyntaxError` | syntax_fix | 语法错误，提取错误行并修复 |
| `json.*decode.*error` | json_fix | JSON 解析错误，检查 JSON 格式 |
| `Permission denied` | permission_fix | 权限问题，建议检查文件权限 |

**当前能力边界**：
- ✅ 能识别已知7种错误模式
- ✅ 能生成结构化自愈报告
- ✅ 能区分"可自动修复"和"需人工介入"
- ❌ **待增强**：LLM无法仅凭规则自动修复未知错误，需要增强为可调用LLM进行推理修复
- ❌ **待实现**：实际执行修复动作（目前只生成报告，尚无自动写入修复）

**待演进方向**：
- 🔜 LLM增强判断（调用LLM分析未知错误）+ 自动执行高置信度修复（需安全边界确认）
- 🔜 自愈学习：将修复成功案例加入 KNOWN_PATTERNS，自动扩充知识库

**输出位置**：`~/.openclaw/workspace/.state/evolution/self-healer.md`

---

### 维度4：行为策略动态调整 🚧 部分已部署（待实现自动应用）

**现状**：`user-preference-profile.py` 已部署，能从 `.learnings/LEARNINGS.md` 提取用户偏好生成画像

**用户偏好提取流程**（`user-preference-profile.py`）：
```
读取 .learnings/LEARNINGS.md
    ↓
按 Category 分类：
  - correction（用户纠正）
  - best_practice（最佳实践）
    ↓
关键词推断行为模式：
  - 包含"太长/简洁" → concise 模式
  - 包含"代码/技术" → technical 模式
  - 包含"创意/有趣" → creative 模式
  - 包含"直接/不要" → direct 模式
    ↓
生成 user-preferences.json
```

**当前能力边界**：
- ✅ 能从 LEARNINGS.md 提取 correction 和 best_practice 条目
- ✅ 能通过关键词推断行为模式
- ✅ 能生成结构化偏好画像并持久化
- ❌ **待实现**：偏好未在实际对话/任务中自动应用
- ❌ **待实现**：correction 条目积累不足，模式推断精度有限

**待演进方向**：
- 🔜 实时偏好应用（在每次回复前检查画像，动态调整输出风格）
- 🔜 偏好置信度过滤（基于更多样本提升识别精度）
- 🔜 偏好时序分析（区分短期/长期偏好，动态调整权重）

**输出位置**：`~/.openclaw/workspace/.state/evolution/user-preferences.json`

```json
{
  "last_updated": "2026-04-04T10:00:00",
  "total_corrections": 5,
  "total_best_practices": 3,
  "patterns": {
    "concise": 1,
    "technical": 1,
    "creative": 0,
    "direct": 1
  },
  "top_corrections": [...],
  "top_practices": [...]
}
```

---

### 维度5：技能健康度监测 🚧 部分已部署（待实现自动动作）

**现状**：`skill-health-monitor.py` 已部署，能扫描所有 Skill 并打分

**技能健康度打分流程**（`skill-health-monitor.py`）：
```
扫描 ~/.openclaw/workspace/skills/ 下所有 Skill
    ↓
对每个 Skill：
  1. 读取 SKILL.md 描述（前80字）
  2. 获取文件最后修改时间
  3. 统计在 daily-mining.md 中的提及次数
    ↓
打分规则（满分10分）：
  - 基础分：5分
  - 提及频率加分：最多+5分（mention_freq × 1，封顶5分）
  - 最近修改加分：30天内修改过 +2分
    ↓
识别低健康度 Skill（health_score < 4 且 mention_freq = 0）
    ↓
生成 skill-health.json + 控制台报告
```

**当前能力边界**：
- ✅ 能扫描所有 Skill 并计算健康度分数
- ✅ 能识别低健康度 Skill 并给出"考虑合并/卸载"建议
- ✅ 能生成 Top10 健康度排名
- ❌ **待实现**：不自动执行任何动作（只报告，不删不停）
- ❌ **待实现**：提及频率统计依赖 daily-mining.md，无法追踪真实调用次数
- ❌ **待实现**：缺少"用户显式抱怨"这一维度的数据采集

**待演进方向**：
- 🔜 真实调用追踪（接入OpenClaw内部日志，替代词频统计）
- 🔜 健康度时序（记录历史，预警下滑趋势）
- 🔜 自动归档（>3个月低健康度 Skill → `.archive/`，保留30天后悔期）

**输出位置**：`~/.openclaw/workspace/.state/evolution/skill-health.json`

```json
{
  "checked_at": "2026-04-04T10:00:00",
  "total_skills": 163,
  "skills": [
    {"name": "feishu", "health_score": 9, "mention_freq": 45},
    ...
  ],
  "low_health_warnings": [
    {"name": "deprecated-skill-x", "reason": "health=2, mentions=0", "suggestion": "考虑合并到通用技能或卸载"}
  ]
}
```

---

