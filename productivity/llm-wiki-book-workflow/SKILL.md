---
name: llm-wiki-book-workflow
description: 内容摄入 Wiki 全流程：书籍 / GitHub仓库 / 论文 / 微信公众号文章 → wiki实体页 + 概念页 + 道法术器分析。触发：书籍入库、repo归档、wiki摄入、内容归档、知识库构建。自动处理下载/提取/wiki写入/索引更新/跨页链接验证。
---

# LLM Wiki 内容摄入工作流

## 触发条件

关键词（任一）：
- "书籍下载摄入wiki" / "把书摄入wiki" / "书籍入库"
- "repo归档" / "克隆到本地并wiki归档" / "GitHub → wiki"
- "wiki摄入" / "归档到wiki" / "内容归档"
- "下载 + 摄入 + 分析" / "下载摄入道法术器"
- "从 epub 到 wiki" / " epub → wiki"
- "我要看书" / "读一下这本书"
- "书单下载" / "下载以下书籍" / "下载书单"

前置动作：**无条件读取** `~/wiki/SCHEMA.md`

---

## 输入

- 书名（中文或英文）
- 作者（可选，有助于定位版本）

---

## 流程

### Phase 1：下载书籍（PDF/EPUB）

**决策顺序**：PDF 书 → 先试 archive.org；EPUB → Anna's Archive

#### 步骤 A：Archive.org（PDF，⚠️ 政策已变）

> **⚠️ 2026-05 变更**：Archive.org 对版权书强制登录认证，直接 curl 下载返回 HTTP 401。公共领域/老书（Thinking Fast and Slow、7 Habits、正义之心等）仍可直接下载；新版商业书需登录或换源。

1. Open Library API 搜索 identifier：
   ```bash
   curl -s "https://openlibrary.org/search.json?q=<书名>&limit=3"
   # 返回的 doc[].ia 字段即为 Archive.org identifier
   ```
2. 用 metadata API 验证 PDF 是否存在（不需认证）：
   ```bash
   curl -s "https://archive.org/metadata/<ia_id>" | python3 -c "
   import sys,json; d=json.load(sys.stdin)
   for f in d['files']:
       if '.pdf' in f['name'].lower():
           print(f['name'], int(f.get('size',0))/1024/1024, 'MB')
   "
   ```
3. 尝试 curl 下载（版权书可能 401）：
   ```bash
   curl -L -o ~/books/<书名>.pdf \
     "https://archive.org/download/<identifier>/<identifier>.pdf"
   ```
4. 失败（401）→ 换源或请用户手动从 archive.org 借阅下载

#### ⚠️ 版权书 401 时的备选策略

IA 直链返回 401 时，不要立即放弃。按以下顺序尝试：

1. **找老版本**：同一书名在 IA 上常有多个版本，逐一尝试 metadata 验证（部分老版本仍可直链）
2. **Anna's Archive**：browser 提取 `fast_download` URL，curl 下载
3. **oceanofPDF**：browser 导航到详情页提取真实文件 URL，curl 下载
4. **z-library / libgen**：需账号，最后手段
5. **请用户手动**：archive.org 免费账号14天借阅

详见 `references/book-sources.md`

**决策规则**：
- 老书/公版（Thinking Fast and Slow、7 Habits、品格的力量、心流等）→ 直接 curl 大概率成功
- 新版商业书（出版5年内）→ 直接 curl 大概率 401，换 Anna's Archive 或请用户手动

#### 步骤 B：Anna's Archive（EPUB 或 archive.org 找不到时）

1. browser 导航到 `https://annas-archive.gl/search?q=<书名+作者>`
2. 点击第一个结果的 md5 链接进入详情页
3. browser_console 执行：`Array.from(document.querySelectorAll('a[href*="fast_download"]')).map(a=>a.href)[0]` 获取第一个下载链接
4. curl 下载：`curl -s --max-time 60 -L -A "Mozilla/5.0" "<url>" -o ~/books/<书名>_<作者>.epub`
5. 失败 → 换 z-library.se（需免费账号）
6. 再失败 → 告知用户手动下载到 `~/books/`

**curl 直接下载 Anna's Archive 的限制**：
- `fast_download/<md5>/0/0` 返回 JS 挑战页（curl 拿到 HTML 而非文件）
- 必须通过 browser 提取真实 URL 后再用 curl

**验证（通用）**：
```bash
# Step 1: magic bytes 检查（必须）
file ~/books/<书名>.pdf
#   ✓ 有效：PDF document, version 1.x
#   ✗ 无效：HTML document text（curl 拿到的是 HTML 错误页）

# Step 2: 大小检查（配合 file 一起判断）
ls -lh ~/books/<书名>.pdf
#   > 100KB + PDF magic bytes → 高可信度有效
#   < 100KB → 大概率无效，即使 magic bytes 碰巧是 PDF
#   某些 HTML 错误页可达 150KB（如 怪诞行为学 128KB 是 HTML）
#   纯文本本书（无图片）通常 1~5MB；扫描版 10~30MB
```
- **必须两步都用**，缺一不可。magic bytes 过滤 HTML，大小过滤空响应。
- 验证失败 → 立即删除 junk 文件，换源重试。不要积攒小文件后再清理。

**多书并行搜索**：一次 `web_search` 最多搜 4 本书，避免触发频率限制

**参考**：`references/book-sources.md`（含各源连通性状态和失败模式）
**GitHub Repo 摄入**：`references/github-repo-ingestion.md`（克隆+raw提取+wiki写入+index更新的完整流程模式）
**微信公众号摄入**：`references/article-ingestion-notes.md`（微信文章抓取+wiki写入流程）

---

### Phase 2：文本提取

#### 2a：Epub 提取为 Markdown

**工具**：`execute_code`（Python）

**依赖**：`pip install ebooklib beautifulsoup4 lxml -q`

**核心逻辑**：
```python
from ebooklib import epub
from bs4 import BeautifulSoup

book = epub.read_epub(epub_path)
chapters = []
for item in book.get_items():
    if item.get_type() == 9:  # HTML
        soup = BeautifulSoup(item.get_content(), 'lxml')
        text = soup.get_text(separator='\n', strip=True)
        if len(text) > 200:
            chapters.append(text)
```

**输出路径**：`~/wiki/raw/books/<书名>_<作者>.md`

**格式要求**：
- 文件第一行：`# <书名>_<作者>.epub`
- 第二行：`> Extracted from EPUB | {char_count} characters | {para_count} paragraphs`
- 纯文本，无 HTML 标签

**验证**：文件行数 > 50 行

#### 2b：PDF 提取为 Markdown

**工具**：Python `pypdf`（系统已安装，无需额外 pip）

**实操流程**（在 `terminal` 中用 heredoc 执行）：
```bash
python3 << 'EOF'
import pypdf, os

books = [
    ("书名.pdf", "输出.md"),
]
for pdf_name, md_name in books:
    path = f"/Users/fuzhuo/books/{pdf_name}"
    out_path = f"/Users/fuzhuo/wiki/raw/books/{md_name}"
    r = pypdf.PdfReader(path)
    total = len(r.pages)
    text = ""
    for p in r.pages[:30]:
        t = p.extract_text()
        if t: text += t + "\n"
    with open(out_path, 'w') as f:
        f.write(f"# {md_name.replace('_', ' ')}\n\n")
        f.write(f"*来源: {pdf_name} | 总页数: {total} | 已提取前30页*\n\n")
        f.write(text[:80000])
    print(f"OK {md_name}: {total}p, {os.path.getsize(out_path)/1024:.0f}KB")
EOF
```

**提取范围**：前30页（覆盖目录、前言、第1-2章，足以提取核心概念和框架）

**⚠️ 扫描版 PDF 检测（必须）**：

下载 PDF 后立即检查：
```python
r = pypdf.PdfReader(path)
total = len(r.pages)
sample = r.pages[0].extract_text()
print(f"总页数: {total}, 第1页字数: {len(sample)}")
```

判断标准：

| 总页数 | 第1页字数 | 结论 | 处理 |
|--------|-----------|------|------|
| >50页 | >100字 | ✅ 文本版 | 正常提取 |
| 1-30页 | 0字 | ❌ 扫描图片版 | 跳过文字提取，记录元数据 |
| >50页 | 0字 | ⚠️ 混合/损坏 | 尝试其他页面，全空则跳过 |

**已知节选/样本版**：08正义之心(8页)、14终身成长(10页)、16象与骑象人章节(29页) — 总页数<30的都是节选，跳过文字提取

---

### Phase 3：Wiki Ingestion

**工具**：`delegate_task`（并行，batch=4 限制）

**前置**：读取 `~/wiki/SCHEMA.md`

**流程**：
1. 从 raw content 提取关键概念（1本书/1仓库 → 1 entity + 1~3 concepts）
2. 按 SCHEMA.md 格式写 frontmatter（type/sources/tags 必填；sources 对 article 填 `raw/articles/`，对 book 填 `raw/books/`）
3. 每页最少 2 个 `[[wikilinks]]`
4. **按序**更新 `~/wiki/index.md`（**entity 区先于 concept 区**）
5. 追加 `~/wiki/log.md`

**Log 格式**（通用）：
```
## [日期] — [来源类型] | [来源标识]
- [实体页] 创建
- [概念页] 创建
- Key insight 1
```

来源类型：`book` / `github` / `arxiv` / `website`。不要硬编码"ingest"。

**Page 类型判断**：
- 人物/书籍/工具 → **entity**
- 方法论/概念/思维框架 → **concept**

**并行策略**：每次 `delegate_task` 最多 4 个子任务，超出则分批

**⚠️ Subagent 超时保护（2026-05-15 强制规则）**：
- 单个 delegate_task 的 task scope **必须小于 5 分钟预期**
- 大任务（article ingestion、book extraction）**不要**塞进单个 delegate_task
- 正确做法：拆分粒度（如 raw article 提取 和 wiki page 创建 分开两步）
- 超时后：subagent 返回 partial result，**主 agent 接手完成**，不重试整个任务
- **禁止**：为超时任务重新 delegate_task（会重复已做的工作）

---

### Phase 4：道法术器分析

**工具**：`read_file`（读取所有新创建的 concept pages）+ LLM 推理

**框架**：

| 层级 | 含义 | 产出 |
|------|------|------|
| **道** | 信念 / Why | 一句话核心信念 |
| **法** | 核心原则 / What | 3~5 条不变原则 |
| **术** | 方法论 / How | 具体操作步骤 |
| **器** | 工具 / Tools | 可用工具清单 |

**输出格式**：
```
## <书名>

### 道
> 核心信念（一句话）

### 法
- 原则1
- 原则2
- ...

### 术
1. 方法A
2. 方法B
...

### 器
- 工具X
- 工具Y
```

**Meta-Skill 对齐**（可选标签）：
- 监控层：刻意练习、批判性思维、认知觉醒
- 自调节层：稀缺心态、原则
- 社会智能层：多元思维模型、逆向思维、非暴力沟通

---

## 文件结构

```
~/books/                    # 原始 epub/pdf
~/wiki/raw/books/           # 提取的 markdown（书籍）
~/wiki/raw/articles/        # 提取的 markdown（文章）
~/wiki/raw/github/          # 提取的 markdown（repo）
~/wiki/entities/            # 实体页面
~/wiki/concepts/            # 概念页面
~/wiki/index.md             # 索引
~/wiki/log.md               # 操作日志（append-only）
```

---

## 注意事项

1. **下载失败**：Anna's Archive 需 browser+curl 组合（不可纯 curl）；libgen.li 需登录；z-library.se 需账号。按 reference/book-sources.md 排查，仍失败则请用户手动下载到 ~/books/
2. **Wiki frontmatter**：type 字段必填，sources 指向 raw/books/，updated 日期必填
3. **并行限制**：delegate_task 每次最多 4 个任务，超出分批
4. **Log 规范**：ingestion 完成必须追加 log.md
5. **Wikilinks**：新建页面至少 2 个外部链接，指向现有 wiki 页面或 raw source
6. **长文本**：提取的 markdown 超过 200KB 时分段处理
7. **网页文章截断**：`web_extract` 对 >5000 字符的文章截断，恢复方法见 `references/article-ingestion-notes.md` Step 1 三步法

---

## 验证清单

- [ ] epub 下载成功（~/books/，>10KB）
- [ ] PDF 元数据检查（总页数>30否？第1页有文字否？）— 扫描版/节选版不提取
- [ ] Markdown 提取成功（~/wiki/raw/books/，>50行）
- [ ] sources frontmatter 更新（道法术器框架-书籍总览.md）
- [ ] Entity page 创建并加入 index.md（**先于** concept page）
- [ ] Concept page(s) 创建并加入 index.md
- [ ] **Wikilink 一致性验证**（见下方详述）
- [ ] log.md 已追加
- [ ] 道法术器分析输出（在对话中，非必须写 wiki）

## Wikilink 一致性验证（批量创建后必须执行）

创建批量页面后，新页面之间的 wikilinks 引用必须逐个验证：

**问题现象**：新创建的 entity 页 A 链接 `[[Entity-B]]`，但 Entity-B 的文件名是 `entity-b.md`，link 无法解析。

**验证命令**：
```bash
# 检查所有新建页面中的 [[wikilinks]] 是否都有对应文件
cd ~/wiki
# 提取所有 wikilink 目标
grep -rho '\[\[[^]]\+\]\]' entities/ concepts/ | sort -u | sed 's/\[\[\([^\]]*\)\]\]/\1/g' > /tmp/wiki_links_needed.txt
# 提取所有已创建的文件名（无后缀）
find entities/ concepts/ -name "*.md" | xargs -I{} basename {} .md | sort -u > /tmp/wiki_files_exist.txt
# 对比
diff /tmp/wiki_links_needed.txt /tmp/wiki_files_exist.txt
```

**快速人工检查**：创建后扫一眼新页面的 Related Concepts / Related Entities 段，确认链接名称与实际文件名完全一致。

**常见错误模式**：
- 创建时用全小写文件名，但 wikilink 用 CamelCase → `[[Claude-Opus-4-7]]` 但文件是 `claude-opus-4-7.md`
- Wikilink 用缩写但文件用完整名 → `[[claude-code]]` 但文件是 `claude-code-system-prompt.md`

**修复方式**：直接 `patch` 错误的 wikilink 为正确的文件名（不含 `.md` 后缀）。

## 已知坑

- **扫描图片版 PDF**：pypdf 提取返回空字符串，但 `file` 命令显示为 PDF，总页数少（<30）。处理：跳过文字提取，不写入 raw/books/
- **节选/样本 PDF**：总页数极少（<30）但文件较大（>1MB），不是完整书。判断：总页数 + 文件大小结合判断
- **curl 返回 HTML**：大小从 1KB 到 150KB 不等，必须同时用 `file` 命令验证 magic bytes
- **kimi.com share URL 的 web_extract 失败**：返回 `{"error": "content too short"}` 或空 content → 使用已有上下文（skill 内容、session memory）补全，不重试 web_extract
