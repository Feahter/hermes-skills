---
name: "tavily-search"
description: |
  Tavily AI 搜索 API — 提供结构化搜索结果与引用来源标注的深度研究工具。

  触发词：tavily、AI搜索、结构化搜索、cited answer、research-grade search、带来源的搜索

  核心能力：
  - 结构化搜索结果：url、title、description、score、published_date、raw_content
  - 引用答案：include_answer=true 返回 LLM 合成的带引用的答案
  - 深度研究模式：search_rag 返回完整研究摘要报告（3 credits/次）
  - 高级搜索：search_depth=advanced（2 credits），支持更深入的结果
  - 时间窗口控制：days 参数聚焦近期结果
  - 图片搜索：include_images=true

  对比 DuckDuckGo：Tavily 提供确定性 JSON 输出 + citations，适合程序化调用
  对比直接爬虫：Tavily 过滤噪音、提取实体、去重，质量更高
---

# Tavily Search v1.0.0

> AI-powered search API with structured results and citations. Best for research-grade queries where source verification matters.

## When to Use Tavily

| Scenario | Recommended Mode |
|----------|-----------------|
| Need cited answers | `include_answer=true` on `/search` |
| Multi-source synthesis | `/search_rag` (deep research) |
| Fact-checking with sources | `/search` + `include_raw_content=true` |
| Recent news/context | `days=7` to recency-filter |
| Programmatic search pipeline | `/search` with JSON response |
| Image search | `include_images=true` |
| Quick lookup (fallback) | DuckDuckGo or multi-search-engine |

## Positioning

**Primary → `tavily-search`**: When you need structured search results, cited answers, or deep research synthesis. Best for research tasks where quality and source verification matter.

**Fallback → `multi-search-engine`**: When Tavily is unavailable (no API key, rate limit reached, or quota exhausted), fall back to `multi-search-engine` which has 17 engines and zero API requirements.

```
tavily-search (primary, quality) → multi-search-engine (fallback, zero-config)
```

## Comparison Table

| Feature | `tavily-search` | `multi-search-engine` |
|---------|----------------|-----------------------|
| Output | ✅ Structured JSON + citations | ⚠️ HTML, needs parsing |
| Research synthesis | ✅ `/search_rag` full report | ❌ None |
| API key required | ✅ Yes (1000 credits/mo free) | ❌ No |
| Engines | 1 (curated index) | 17 engines |
| Freshness control | ✅ `days=` parameter | ⚠️ Via time filters |
| Programmatic | ✅ Clean JSON API | ⚠️ Regex/HTML parsing |

| Feature | `/search` (basic) | `/search` (advanced) | `/search_rag` |
|---------|------------------|---------------------|--------------|
| Credits per call | 1 | 2 | 3 |
| Results | Up to 20 | Up to 20 | Up to 20 |
| Answer synthesis | Optional | Optional | Full report |
| Citations | Via `include_answer` | Via `include_answer` | Built-in |
| Use case | Quick structured search | Deeper crawling | Deep research |

## Quick Examples

### Python Client (Recommended)

```python
from tavily import TavilyClient

client = TavilyClient(api_key="tvly-XXXXXXXX")

# Basic search
results = client.search(
    query="最新 AI 编程工具 2025",
    search_depth="basic",
    max_results=5
)
for r in results["results"]:
    print(f"[{r['score']:.2f}] {r['title']}")
    print(f"  {r['url']}")
    print(f"  {r['description']}")

# With answer (cited synthesis)
results = client.search(
    query="什么是 RAG 技术",
    include_answer=True,
    include_raw_content=False
)
print(results["answer"])  # LLM-generated answer with citations

# Advanced search (2 credits)
results = client.search(
    query="Claude Code vs Copilot 对比",
    search_depth="advanced",
    max_results=10,
    days=30
)

# Deep research (3 credits) — full report
report = client.search_rag(
    query="AI Agent 发展历史与未来趋势",
    max_sources=10,
    search_depth="advanced"
)
print(report["answer"])  # Structured research report
print(report["sources"])  # Source list with citations

# Image search
results = client.search(
    query="Tesla Cybertruck",
    include_images=True,
    max_results=5
)
for img in results.get("images", []):
    print(img["url"])
```

### curl

```bash
# Basic search
curl -X POST https://api.tavily.com/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TAVILY_API_KEY" \
  -d '{
    "query": "Python asyncio tutorial",
    "search_depth": "basic",
    "max_results": 5
  }'

# With answer
curl -X POST https://api.tavily.com/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TAVILY_API_KEY" \
  -d '{
    "query": "how does RAG work",
    "include_answer": true
  }'

# Deep research
curl -X POST https://api.tavily.com/search_rag \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TAVILY_API_KEY" \
  -d '{
    "query": "future of AI agents",
    "max_sources": 10,
    "search_depth": "advanced"
  }'
```

## API Key Setup

### 1. Get API Key

Sign up at https://tavily.com (free tier: 1000 credits/month)

### 2. Install Client

```bash
pip install tavily-python
```

### 3. Configure Key

**Option A — Environment variable (recommended for scripts)**

```bash
# Add to ~/.zshrc
export TAVILY_API_KEY="tvly-XXXXXXXXXXXXXXXX"

# Reload
source ~/.zshrc
```

**Option B — Direct in code (dev only)**

```python
client = TavilyClient(api_key="tvly-XXXXXXX")
```

**Option C — `.env` file with python-dotenv**

```bash
pip install python-dotenv
```

```bash
# .env
TAVILY_API_KEY=tvly-XXXXXXXX
```

```python
from dotenv import load_dotenv
load_dotenv()
client = TavilyClient()  # reads TAVILY_API_KEY from env
```

## Tier Comparison

| Feature | Free | Pro ($5/mo) | Pro+ ($25/mo) |
|---------|------|-------------|---------------|
| Credits/month | 1,000 | 5,000 | 20,000 |
| Basic search | ✅ | ✅ | ✅ |
| Advanced search | ✅ | ✅ | ✅ |
| Deep research | ✅ | ✅ | ✅ |
| API access | ✅ | ✅ | ✅ |
| Rate limit | 2 req/min | 60 req/min | 120 req/min |
| Max results | 20 | 20 | 20 |

**Credit costs:**
- Basic search: 1 credit
- Advanced search: 2 credits
- Deep research (search_rag): 3 credits

## Layered Search Strategy

Use **DuckDuckGo** (multi-search-engine skill) as quick/fallback search, **Tavily** as primary research tool:

```
┌─────────────────────────────────────────────┐
│              Research Query                   │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────▼──────────┐
        │  DuckDuckGo / Brave │  ← Quick check, < 30 sec
        │  (no API key needed)│
        └──────────┬──────────┘
                   │ Need more?
        ┌──────────▼──────────┐
        │     Tavily Search   │  ← Structured results + citations
        │    (basic, 1 cred) │
        └──────────┬──────────┘
                   │ Deep dive?
        ┌──────────▼──────────┐
        │  Tavily Deep Res.   │  ← Full research report
        │   (search_rag)      │     (3 credits)
        └─────────────────────┘
```

**When to escalate from DuckDuckGo to Tavily:**
1. Results needed in structured JSON format
2. Source citations required
3. Answer synthesis needed (LLM-generated summary)
4. Programmatic pipeline / repeatable results
5. Research topic requires cross-verification

## Response Shape

### `/search` Response

```json
{
  "query": "Python asyncio tutorial",
  "results": [
    {
      "url": "https://realpython.com/async-python/",
      "title": "Async Python Tutorial",
      "description": "Learn async/await in Python...",
      "published_date": "2024-03-15",
      "score": 0.95,
      "raw_content": "Full article text..."
    }
  ],
  "answer": "Async Python allows...",
  "images": [],
  "inference_time": 1.23
}
```

### `/search_rag` Response

```json
{
  "query": "future of AI agents",
  "answer": "## Research Summary\n\nBased on analysis of 10 sources...",
  "sources": [
    {
      "title": "AI Agents in 2025",
      "url": "https://...",
      "content": "..."
    }
  ],
  "inference_time": 12.45
}
```

## References

- `references/api.md` — Full endpoint documentation, error codes, response schemas
