# 去AI味深度润色指南

## 去AI味深度润色 v5.0融合chinese-novelist

> 来源：chinese-novelist-skill/references/flows/phase3-writing.md

### 深度润色（去除AI味）检查清单

重点检查并修改：

1. **去除过度修饰的形容词** — 删除"璀璨"、"瑰丽"、"绚丽多彩"等AI常用词堆砌
2. **减少抽象陈述** — 把"心中涌起复杂的情感"改为具体动作/对话
3. **打破四字格律** — 避免"心潮澎湃、热血沸腾"等陈词滥调
4. **增加口语化表达** — 人物对话要有个性，不要都是播音腔
5. **优化节奏感** — 长句短句交替，不要全是同等长度的句子
6. **细节具象化** — 用具体细节替代笼统描述
7. **动作代替形容** — "他老了"不如"他扶着墙站起来"

### 章节字数标准

| 章节类型 | 字数要求 | 不足时 |
|----------|---------|--------|
| 日常章 | 2000-3000字 | 使用 content-expansion 扩充技巧 |
| 普通章 | 3000-4000字 | 使用 content-expansion 扩充技巧 |
| 关键章 | 4000-6000字 | 必须达标，高潮需要充分展开 |

> 字数检查必须使用脚本：`python scripts/check_chapter_wordcount.py <章节文件路径>`

---



---

## 自动校验与3轮重写 v5.0融合chinese-novelist

### 校验流程

1. **字数检查** — 每章必须达到目标字数
2. **连贯性检查** — 人物一致性、情节连贯、节奏控制
3. **不合格章节自动重写** — 最多3轮

### 重写规则

| 轮次 | 条件 | 操作 |
|------|------|------|
| 第1次 | 字数<3000 或 连贯性差 | 记录问题，重新生成 |
| 第2次 | 仍不合格 | 分析失败原因，调整策略 |
| 第3次 | 仍不合格 | 记录错误到 QA 报告，跳过本章 |

---

## 📝 进度文件格式（v5.0更新）

```json
{
  "novel": {
    "title": "小说名",
    "chapter_count": 120,
    "current_level": "L4"
  },
  "writing_mode": "serial",
  "L1_种子层": { "status": "completed", "完成时间": "2026-01-01" },
  "L2_萌芽层": { "status": "completed", "完成时间": "2026-01-02" },
  "第一卷": { "总章节": 30, "已完成": 30, "进度": "100%" },
  "chapters": {
    "ch001": { "status": "completed", "wordCount": 3500, "retries": 0 },
    "ch002": { "status": "completed", "wordCount": 3800, "retries": 0 },
    "ch003": { "status": "in_progress", "wordCount": 0, "retries": 0 }
  },
  "current_chapter": "ch003",
  "chapter_status": "in_progress",
  "last_update": "2026-04-21 12:00:00"
}
```

> 章节状态：`pending` | `in_progress` | `completed` | `failed`（最多重写3次后标记 failed）

---

