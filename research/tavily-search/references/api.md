# Tavily API Reference

## Base URL

```
https://api.tavily.com
```

## Authentication

All endpoints require:

```
Authorization: Bearer <TAVILY_API_KEY>
Content-Type: application/json
```

## Endpoints

### POST `/search`

Structured web search with optional answer synthesis.

**Endpoint:** `POST https://api.tavily.com/search`

#### Request Body

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | **required** | Search query (max ~500 chars) |
| `search_depth` | string | `"basic"` | `"basic"` or `"advanced"` |
| `max_results` | integer | `10` | Number of results (1–20) |
| `include_answer` | boolean | `false` | Return LLM-generated answer with citations |
| `include_raw_content` | boolean | `false` | Include full article text |
| `include_images` | boolean | `false` | Include image results |
| `days` | integer | `None` | Recency filter: limit to past N days |
| `exclude_domains` | array[string] | `[]` | Domains to exclude |

#### Request Example

```json
{
  "query": "latest AI coding tools comparison",
  "search_depth": "advanced",
  "max_results": 10,
  "include_answer": true,
  "include_raw_content": false,
  "include_images": false,
  "days": 30,
  "exclude_domains": []
}
```

#### Response

```json
{
  "query": "string",
  "results": [
    {
      "url": "string",
      "title": "string",
      "description": "string",
      "published_date": "string | null",
      "score": "number (0-1)",
      "raw_content": "string | null"
    }
  ],
  "answer": "string | null",
  "images": [
    {
      "url": "string",
      "description": "string"
    }
  ],
  "inference_time": "number (seconds)"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `query` | string | Echo of the search query |
| `results` | array | Array of search result objects |
| `results[].url` | string | Source URL |
| `results[].title` | string | Page title |
| `results[].description` | string | Page snippet/description |
| `results[].published_date` | string \| null | Publication date (ISO 8601) |
| `results[].score` | number | Relevance score (0–1) |
| `results[].raw_content` | string \| null | Full article text (if `include_raw_content=true`) |
| `answer` | string \| null | LLM-generated answer with citations (if `include_answer=true`) |
| `images` | array | Image results (if `include_images=true`) |
| `inference_time` | number | Processing time in seconds |

---

### POST `/search_rag`

Deep research mode — returns a structured research report synthesized from multiple sources.

**Endpoint:** `POST https://api.tavily.com/search_rag`

#### Request Body

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | **required** | Research query |
| `max_sources` | integer | `10` | Max sources to analyze (1–20) |
| `search_depth` | string | `"basic"` | `"basic"` or `"advanced"` |
| `max_results` | integer | `10` | Max raw results to fetch before synthesis |

#### Request Example

```json
{
  "query": "Impact of LLMs on software development",
  "max_sources": 15,
  "search_depth": "advanced",
  "max_results": 20
}
```

#### Response

```json
{
  "query": "string",
  "answer": "string (markdown-formatted research report)",
  "sources": [
    {
      "title": "string",
      "url": "string",
      "content": "string (relevant snippet)"
    }
  ],
  "inference_time": "number (seconds)"
}
```

---

## Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| `400` | `INVALID_REQUEST` | Missing or invalid parameters |
| `401` | `UNAUTHORIZED` | Invalid or missing API key |
| `402` | `QUOTA_EXCEEDED` | Monthly credit limit reached |
| `429` | `RATE_LIMITED` | Too many requests (tier-dependent) |
| `500` | `INTERNAL_ERROR` | Server error — retry with backoff |

### Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description"
  }
}
```

---

## Credit Costs

| Operation | Credits |
|-----------|---------|
| Basic search | 1 |
| Advanced search (`search_depth="advanced"`) | 2 |
| Deep research (`search_rag`) | 3 |

**Free tier:** 1,000 credits/month

---

## Python Client Reference

```python
from tavily import TavilyClient

client = TavilyClient(api_key="tvly-XXXXX")

# Search
client.search(
    query: str,
    search_depth: Literal["basic", "advanced"] = "basic",
    max_results: int = 10,
    include_answer: bool = False,
    include_raw_content: bool = False,
    include_images: bool = False,
    days: Optional[int] = None,
    exclude_domains: Optional[List[str]] = None
) -> dict

# Deep research
client.search_rag(
    query: str,
    max_sources: int = 10,
    search_depth: Literal["basic", "advanced"] = "basic",
    max_results: int = 10
) -> dict

# Get API usage info
client.get_api_usage() -> dict
```

---

## Rate Limits

| Tier | Limit |
|------|-------|
| Free | 2 req/min |
| Pro ($5/mo) | 60 req/min |
| Pro+ ($25/mo) | 120 req/min |

---

## Notes

- `published_date` may be `null` for pages without detectable date
- `raw_content` availability depends on site crawlability
- Deep research (`search_rag`) uses LLM synthesis — response time may be higher
- Results are deduplicated by domain
