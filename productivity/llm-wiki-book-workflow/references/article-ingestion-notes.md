# Article Ingestion Reference

> Session-specific notes for wiki article ingestion. Add new learnings here.

## 微信公众号文章摄入流程

### Step 1: 获取内容
- `web_extract` 对微信文章无效（返回 401/403）
- 正确方式: `browser_navigate` → `browser_snapshot({"full": true})`
- 若内容不完整: 多次 `browser_scroll` 至底部

### Step 2: 归档 raw 文件
```
~/wiki/raw/articles/<slug>-<YYYY-MM-DD>.md
```
Frontmatter 格式:
```yaml
# <文章标题>

> 原文: <url>
> 作者: <author>
> 来源: <publication>
> 日期: <YYYY-MM-DD>
```

### Step 3: Wiki 页面判断
| 文章类型 | Page 类型 |
|---------|---------|
| 作者介绍/人物 | **entity** |
| 方法论/框架/概念 | **concept** |
| 对比分析 | **comparison** |
| 书/工具的详细笔记 | **entity** 或 **concept** 视核心度决定 |

### Step 4: Entity vs Concept 判定规则
- 出现 2+ 次核心概念 → concept
- 人物/书籍/工具 → entity
- 单纯概念（方法论/思维框架）→ concept

### Step 5: Index.md 更新顺序
1. Entity pages **先于** Concept pages 加入 index.md
2. 添加到正确的 section（Entities / Concepts）
3. 更新 header 元数据行: `Last updated` + `Total pages`
4. 删除重复条目（index.md 有时会积攒重复）

---

## 普通网页文章摄入流程

### Step 1: 获取内容

**首选**：`web_extract`（快速，返回 Markdown 格式）

**⚠️ 截断问题**：`web_extract` 对长文章（>5000 字符）会截断摘要。判断方法：
- 返回 content 约 5000 chars 且末尾是 `...`
- 或出现 `... summary truncated for context management`

**截断恢复三步法**：

1. **获取 total length**：
   ```python
   result = web_extract(["https://example.com/article"])
   content = result["results"][0]["content"]
   print(f"Total length: {len(content)}")
   ```

2. **定位目标 section**：找到起始 marker（如 `### 3. Baton` 或 `## Tool Reviews`）
   ```python
   idx = content.find("### 3. Baton")
   print(f"Section starts at: {idx}")
   ```

3. **提取剩余内容**：
   ```python
   print(content[idx:idx+3000])  # 指定 section，往后取 3000 chars
   print(content[-2500:])        # 或最后 2500 字符
   ```

**综合策略**：
- 第一轮 `web_extract` → 通常包含 TL;DR + 前 2-3 个工具
- 第二轮切片提取 → 用 `find` 定位后续 section，用 `content[marker:]` 补全
- 第三轮仍不完整 → 换 `browser_navigate` + `browser_snapshot`

### Step 2: 归档 raw 文件

路径格式：`~/wiki/raw/articles/<slug>-<YYYY-MM-DD>.md`

Frontmatter：
```yaml
# <文章标题>

> 原文: <url>
> 作者: <author>
> 来源: <publication>
> 日期: <YYYY-MM-DD>
```

### Step 3: Wiki 页面判断

| 文章类型 | Page 类型 |
|---------|---------|
| 人物/书籍/工具 | **entity** |
| 方法论/框架/概念 | **concept** |
| 对比分析 | **comparison** |
| 书/工具详细笔记 | **entity** 或 **concept** |

### Step 4: Entity vs Concept 判定规则

- 出现 2+ 次核心概念 → concept
- 人物/书籍/工具 → entity
- 单纯概念（方法论/思维框架）→ concept

### Step 5: Index.md 更新

1. Entity pages **先于** Concept pages
2. Entity 在 Entities section 按字母序插入（找前一个字母和后一个字母的条目）
3. Concept 在 Concepts section 按字母序插入
4. 更新 header: `Last updated` + `Total pages`（+6 因为本次创建了 4 entities + 2 concepts）
5. 完成后检查重复条目

---

## 已知坑

- **index.md patch 顺序**：多个条目插入时，先读完整文件确认当前内容，避免 patch 位置错误或重复条目累积
- **微信文章 `web_extract` 失败** → 使用 browser 工具组合
- **web_extract 截断** → 用 `execute_code` + 字符串切片恢复（见上方 Step 1 三步法）
- **kimi.com share URL `web_extract` 失败** → 返回 `content too short` 或 0 content，fallback 到 skill/session 已有上下文补全，不重试

## Subagent 超时处理（2026-05-15 新增）

当使用 `delegate_task` 摄入 wiki 时：

1. **预估时间**：单次 article ingestion（含 raw + 2-4 wiki pages）≈ 3-5 分钟内
2. **超时表现**：subagent 报 `status: timeout` 且 `api_calls` 数远低于预期
3. **正确处理**：
   - 从 `api_calls` 数量判断完成进度
   - 手动接手未完成的步骤（raw 文件通常已创建）
   - 检查 index.md 和 log.md 是否已更新
   - **不重新 delegate_task**（会重复已完成工作）
4. **预防**：大任务（>4 wiki pages）拆成多个 delegate_task，或主 agent 自己执行
