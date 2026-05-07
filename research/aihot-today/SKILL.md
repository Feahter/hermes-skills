---
name: aihot-today
description: "Fetch and summarize AI hot topics from aihot.today — aggregates TechCrunch, 36Kr, GitHub Trending, Hacker News, MIT, A16Z, OpenAI, Anthropic, HuggingFace, arXiv, 量子位, 极客公园 and 20+ more sources in real-time. Use when user asks for AI news, AI hot topics, daily AI updates, AI industry trends, or mentions aihot, AI热榜, AI热点, 36氪AI, TechCrunch AI. NOT for coding with DeepSeek models, writing articles, or general tech news without AI focus."
---

# AI热点搜索 - aihot.today 实时热榜

## 触发条件

用户想要：今日AI热榜 / AI热点新闻 / 某来源的AI资讯 / 关键词搜索AI热点

## 执行命令

```bash
# 全部来源 Top20（默认）
python3 ~/.hermes/skills/research/aihot-today/scripts/aihot_fetch.py --limit 20

# 指定来源
python3 ~/.hermes/skills/research/aihot-today/scripts/aihot_fetch.py --source techcrunch --limit 10
python3 ~/.hermes/skills/research/aihot-today/scripts/aihot_fetch.py --source 36kr --limit 10

# 关键词过滤
python3 ~/.hermes/skills/research/aihot-today/scripts/aihot_fetch.py --keyword DeepSeek --limit 10

# JSON格式
python3 ~/.hermes/skills/research/aihot-today/scripts/aihot_fetch.py --json
```

## 支持来源

| 标识 | 来源 |
|------|------|
| `techcrunch` | TechCrunch |
| `36kr` | 36Kr |
| `github` | GitHub Trending |
| `hackernews` | Hacker News |
| `mit` | MIT News |
| `a16z` | A16Z |
| `openai` | OpenAI |
| `anthropic` | Anthropic |
| `huggingface` | Hugging Face |
| `arxiv` | arXiv |
| `量子位` | 量子位 |
| `极客公园` | 极客公园 |
| `producthunt` | Product Hunt |
| `cnbc` | CNBC |
| `geekpark` | 极客网 |

## 示例输出

```markdown
# 🔥 AI今日热榜 - 2026-05-07 10:27

## TechCrunch (05月07日 10:17)
1. 巴里·迪勒信任山姆·奥特曼... — 莎拉·佩雷斯
2. Snap称其与Perplexity的4亿美元交易... — 艾莎·马利克

## 36Kr (05月07日 10:13)
1. 他用DeepSeek-V4手搓Agent... — 法学生跨界开发...
...
```

## 前置依赖

```bash
pip install requests beautifulsoup4
```

## 注意事项

- 数据来源于 aihot.today，实时抓取
- 默认每来源 20 条，`--limit` 可调整
- 关键词过滤：`--keyword 关键词`
- 请求间隔可设：`--delay 2`（秒）

> 解析细节（CSS 选择器、来源域名映射）→ `references/parsing-notes.md`
