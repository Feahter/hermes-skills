---
name: jina-reader
description: Convert any URL to clean, readable Markdown using Jina Reader API
version: 1.0.0
tags:
  - web-extraction
  - markdown
  - article-archiving
  - research
  - content-extraction
trigger_keywords:
  - extract article
  - convert to markdown
  - save article
  - page to markdown
  - article content
  - read article
  - article archiving
  - research material
  - web page content
  - extract content from url
skill_category: productivity
---

# Jina Reader Skill

## Overview

Jina Reader converts any URL into clean, readable Markdown. It's the fastest way to extract article content, save web pages for offline reading, or prepare content for AI processing.

**Endpoint:** `https://r.jina.ai/<url>`

**Free tier:** 1M characters/month (no API key required)

---

## When to Use

Use Jina Reader when the user asks to:

- **Extract article content** from a single URL
- **Convert a web page to Markdown** for reading or processing
- **Save an article for later** — get clean text without ads/nav
- **Collect research material** — extract content from articles, docs, blogs
- **Feed content to an AI** — get clean text without HTML noise
- **Get just the article text** — no screenshots, no browsing needed

Trigger phrases: *"extract article from"*, *"convert to markdown"*, *"save article"*, *"get article content"*, *"read this page"*, *"article archiving"*, *"extract content from url"*

---

## Positioning

**Primary → `jina-reader`**: When you need clean, readable Markdown from a single URL (article, blog, doc). No HTML noise, direct content extraction.

**Fallback → `web_extract`**: When `jina-reader` fails (network error, rate limit, non-article page), fall back to `web_extract` which auto-summarizes and has browser-level fallback.

```
jina-reader (primary) → web_extract (fallback on failure)
```

## Comparison Table

| Feature | `jina-reader` | `web_extract` |
|---------|--------------|---------------|
| Output cleanliness | ✅ Clean markdown | ⚠️ Contains noise |
| Multi-URL support | ❌ Single URL | ✅ Batch |
| Failure recovery | ❌ None | ✅ Browser fallback |
| API key required | ❌ Optional | ❌ No |
| Free tier | 1M chars/month | Unlimited |

---

## How to Call

### curl

```bash
# Basic — just prepend the URL
curl -s https://r.jina.ai/https://example.com

# With Markdown accept header
curl -s -H "Accept: text/markdown" https://r.jina.ai/https://example.com

# With API key for higher limits
curl -s -H "Authorization: Bearer $JINA_API_KEY" https://r.jina.ai/https://example.com

# Pagination (Next)
curl -s "https://r.jina.ai/?next=https://example.com&url=https://page2-url.com"
```

### Node.js

```javascript
// Basic fetch
const response = await fetch(`https://r.jina.ai/${encodeURIComponent(url)}`, {
  headers: { 'Accept': 'text/markdown' }
});
const markdown = await response.text();

// With API key
const response = await fetch(`https://r.jina.ai/${encodeURIComponent(url)}`, {
  headers: {
    'Authorization': `Bearer ${process.env.JINA_API_KEY}`,
    'Accept': 'text/markdown'
  }
});
```

### Python

```python
import requests

# Basic
resp = requests.get(f"https://r.jina.ai/{url}")
print(resp.text)

# With headers
resp = requests.get(
    f"https://r.jina.ai/{url}",
    headers={
        "Accept": "text/markdown",
        "Authorization": f"Bearer {api_key}"
    }
)
print(resp.text)
```

---

## API Reference

### Endpoint

```
GET https://r.jina.ai/<url-to-extract>
GET https://r.jina.ai/?next=<pagination-url>&url=<target-url>
```

### Query Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `url` | Target URL to extract (when using `?next=`) | `url=https://example.com` |
| `next` | Pagination — URL of next page to fetch | `next=https://example.com/page2` |
| `target` | Specify content type preference | `target=markdown` |
| `width` | Content width for readability | `width=800` |
| `height` | Content height | `height=1200` |
| `from` | Source format hint | `from=html` |

### Headers

| Header | Description | Example |
|--------|-------------|---------|
| `Authorization` | Bearer token for API key | `Bearer jina_xxxxxxxx` |
| `x-return-format` | Override return format | `markdown`, `text` |
| `Accept` | Response content type | `text/markdown` (recommended) |
| `Jina-Embedding` | Request embeddings | `Jina-Embedding: true` |
| `Jina-Rerank` | Request reranking | `Jina-Rerank: true` |

### Response Headers (x-)

The API returns metadata in response headers:

| Header | Description |
|--------|-------------|
| `x-ttl` | Time-to-live for the cached result |
| `x-truncate` | Whether content was truncated |
| `x-title` | Page title |
| `x-description` | Page description |
| `x-author` | Author (if detected) |
| `x-date` | Publication date |
| `x-image` | Main image URL |
| `x-keywords` | Page keywords |
| `x-source` | Source domain |
| `x-og-title` | OpenGraph title |
| `x-og-description` | OpenGraph description |

---

## Pricing Tiers

| Tier | Price | Characters/Month | Limits |
|------|-------|------------------|--------|
| **Free** | $0 | 1M | Rate limited |
| **Pro** | $5/mo | 10M | Higher rate limits |
| **Pro Plus** | $15/mo | 50M | Highest rate limits |

### Getting an API Key

1. Go to https://jina.ai/reader/
2. Sign up / log in
3. Navigate to API settings
4. Copy your `jina_xxxxxxxx` API key

Set as environment variable:
```bash
export JINA_API_KEY=jina_xxxxxxxxxxxxx
```

---

## Examples

### 1. Basic Article Extraction

```bash
curl -s https://r.jina.ai/https://example.com/article
```

### 2. Extract with Markdown Header

```bash
curl -s -H "Accept: text/markdown" https://r.jina.ai/https://example.com/article
```

### 3. With API Key (Pro Tier)

```bash
curl -s -H "Authorization: Bearer $JINA_API_KEY" \
     https://r.jina.ai/https://example.com/long-article
```

### 4. Pagination (Multi-page Article)

```bash
# Page 1
curl -s https://r.jina.ai/https://example.com/article-part-1

# Page 2 — use next param
curl -s "https://r.jina.ai/?next=https://example.com/article-part-2&url=https://example.com/article"
```

### 5. Content Type Selection

```bash
# Force markdown output
curl -s -H "x-return-format: markdown" https://r.jina.ai/https://example.com

# Force plain text
curl -s -H "x-return-format: text" https://r.jina.ai/https://example.com
```

### 6. Article Archiving Workflow

```bash
# Extract article
ARTICLE=$(curl -s -H "Accept: text/markdown" https://r.jina.ai/https://example.com/blog/interesting-post)

# Save to file with metadata
curl -s -D - -H "Accept: text/markdown" https://r.jina.ai/https://example.com/blog/interesting-post > article.md
```

---

## Integration with Other Skills

### Jina Reader + web_extract

- **Jina Reader:** Best for single articles, docs, blog posts — fast, clean Markdown
- **web_extract:** Better for general link previews, multi-format (PDF, HTML), quick summaries

**Use Jina Reader when:** User explicitly wants Markdown, needs article content, or web_extract fails

### Jina Reader + Crawl4AI

- **Jina Reader:** Single URL, quick extraction, no JavaScript needed
- **Crawl4AI:** Batch URLs, multi-page sites, JavaScript rendering, structured data

**Use Jina Reader when:** It's a single article and speed matters

### Jina Reader + browser

- **Jina Reader:** Fast text extraction, no rendering needed
- **browser:** JavaScript-heavy SPAs, interactive content, screenshots

**Use Jina Reader when:** The page is static content (articles, docs, blogs)

---

## Quick Comparison

| Feature | Jina Reader | web_extract | Crawl4AI |
|---------|-------------|-------------|----------|
| **Use case** | Single URL → Markdown | Link previews, quick extracts | Batch/multi-page |
| **JavaScript** | ✗ No | ✗ No | ✓ Yes |
| **Batch** | ✗ Single | ✗ Limited (5) | ✓ Yes |
| **Speed** | ⚡ Fast | ⚡ Fast | 🐢 Slower |
| **API key** | Optional | Built-in | Self-hosted |
| **Free tier** | 1M chars/mo | Unlimited | Self-host |
| **Output** | Markdown | Markdown/summary | Structured/JSON |
| **Best for** | Article archiving, AI input | Quick previews | Deep crawls |

---

## Notes

- Always URL-encode the target URL when it contains query parameters: `encodeURIComponent(url)`
- For very long content, consider pagination with the `next` parameter
- The `x-` response headers contain valuable metadata — parse them for title, author, date
- No API key needed for basic use; add `JINA_API_KEY` for higher rate limits
- The endpoint `r.jina.ai` is the production-ready, fast edge endpoint
