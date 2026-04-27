# Jina Reader API Reference

## Base URL

```
https://r.jina.ai
```

## Endpoints

### Read (Extract Content from URL)

```
GET https://r.jina.ai/<url-to-extract>
GET https://r.jina.ai/?next=<pagination-url>&url=<target-url>
```

Extracts content from any URL and returns clean Markdown or plain text.

---

## Request

### URL Construction

**Method 1: Direct prefix (recommended)**
```
https://r.jina.ai/https://example.com/article
```

**Method 2: Query parameters**
```
https://r.jina.ai/?url=https://example.com/article
```

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes (if not using direct prefix) | The target URL to extract content from. Must be URL-encoded. |
| `next` | string | No | URL of the next page for pagination. Used for multi-page articles. |
| `target` | string | No | Content type preference: `markdown` or `text`. |
| `width` | integer | No | Content width hint for readability formatting. |
| `height` | integer | No | Content height hint for readability formatting. |
| `from` | string | No | Source format hint (e.g., `html`). |

### Headers

| Header | Required | Description | Example |
|--------|----------|-------------|---------|
| `Authorization` | No | Bearer token for authenticated requests (higher limits) | `Bearer jina_xxxxxxxxxxxx` |
| `Accept` | No | Desired response content type | `text/markdown` (recommended) |
| `x-return-format` | No | Override response format | `markdown` or `text` |
| `x-target-language` | No | Translate output to specified language | `en`, `zh`, `de`, etc. |
| `Jina-Embedding` | No | Request content embeddings | `true` |
| `Jina-Rerank` | No | Request reranking results | `true` |

---

## Response

### Success (200 OK)

Returns the extracted content as raw Markdown or plain text.

**Content-Type:** `text/plain` or `text/markdown` (depending on Accept header and availability)

### Response Headers

The API returns important metadata in response headers:

| Header | Description |
|--------|-------------|
| `x-ttl` | Time-to-live for the cached result in seconds |
| `x-truncate` | Whether the content was truncated (`true`/`false`) |
| `x-title` | Detected page title |
| `x-description` | Page meta description |
| `x-author` | Detected author (if available) |
| `x-date` | Publication date (if detected) |
| `x-image` | Main image URL |
| `x-keywords` | Page keywords (comma-separated) |
| `x-source` | Source domain name |
| `x-og-title` | OpenGraph title |
| `x-og-description` | OpenGraph description |
| `x-og-image` | OpenGraph image URL |
| `x-final-url` | Final URL after redirects |
| `x-content-tokens` | Number of tokens in the content |

### Error Responses

| Status | Meaning | Cause |
|--------|---------|-------|
| `400` | Bad Request | Invalid URL format |
| `403` | Forbidden | Access denied to the target |
| `404` | Not Found | Target page doesn't exist |
| `429` | Rate Limited | Too many requests (upgrade or wait) |
| `500` | Server Error | Jina Reader internal error |
| `502` | Bad Gateway | Target site is unreachable |
| `503` | Service Unavailable | Jina Reader is down |

### Error Body

```json
{
  "error": true,
  "code": "RATE_LIMITED",
  "message": "Rate limit exceeded. Please try again later."
}
```

---

## Pagination

For multi-page articles, use the `next` parameter:

```
GET https://r.jina.ai/?next=https://page2-url.com&url=https://original-url.com
```

**Note:** Use the direct prefix method for the first page, then switch to query params for subsequent pages.

### Example

```bash
# First page
curl -s https://r.jina.ai/https://example.com/article

# Second page
curl -s "https://r.jina.ai/?next=https://example.com/page2&url=https://example.com/article"
```

---

## Rate Limits

### Without API Key

- ~100 requests/minute (approximate)
- 1M characters/month

### With API Key (Pro - $5/mo)

- Higher rate limits
- 10M characters/month

### With API Key (Pro Plus - $15/mo)

- Highest rate limits
- 50M characters/month

---

## Code Examples

### cURL

```bash
# Basic extraction
curl -s https://r.jina.ai/https://example.com

# With headers
curl -s -D - -H "Accept: text/markdown" https://r.jina.ai/https://example.com

# With API key
curl -s -H "Authorization: Bearer $JINA_API_KEY" https://r.jina.ai/https://example.com

# Pagination
curl -s "https://r.jina.ai/?next=https://example.com/page2&url=https://example.com"
```

### Python

```python
import requests

# Basic
response = requests.get(f"https://r.jina.ai/{url}")
print(response.text)

# With API key and headers
response = requests.get(
    f"https://r.jina.ai/{url}",
    headers={
        "Accept": "text/markdown",
        "Authorization": f"Bearer {api_key}"
    }
)
print(response.text)

# With response headers
response = requests.get(
    f"https://r.jina.ai/{url}",
    headers={"Accept": "text/markdown"}
)
print(response.text)
print(f"Title: {response.headers.get('x-title')}")
print(f"Author: {response.headers.get('x-author')}")
```

### Node.js

```javascript
// Basic fetch
const response = await fetch(`https://r.jina.ai/${encodeURIComponent(url)}`);
const markdown = await response.text();

// With API key
const response = await fetch(`https://r.jina.ai/${encodeURIComponent(url)}`, {
  headers: {
    'Authorization': `Bearer ${process.env.JINA_API_KEY}`,
    'Accept': 'text/markdown'
  }
});
const markdown = await response.text();

// Parse headers
const title = response.headers.get('x-title');
const author = response.headers.get('x-author');
```

### Java

```java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

// Basic
HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://r.jina.ai/" + url))
    .header("Accept", "text/markdown")
    .build();
HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
System.out.println(response.body());
```

### Go

```go
package main

import (
    "fmt"
    "io"
    "net/http"
    "net/url"
)

func main() {
    targetURL := url.QueryEscape("https://example.com")
    resp, err := http.Get("https://r.jina.ai/" + targetURL)
    if err != nil {
        panic(err)
    }
    defer resp.Body.Close()
    body, _ := io.ReadAll(resp.Body)
    fmt.Println(string(body))
}
```

---

## Best Practices

1. **Always URL-encode** the target URL when it contains special characters
2. **Use the `Accept: text/markdown`** header for consistent output
3. **Check response headers** for metadata (title, author, date)
4. **Handle rate limits** gracefully with retry-after logic
5. **Store API key in environment** — never hardcode
6. **For long content**, implement pagination with `next` parameter
7. **Verify target URL accessibility** before extraction

---

## Links

- **Dashboard:** https://jina.ai/reader/
- **Pricing:** https://jina.ai/reader/
- **Documentation:** https://jina.ai/reader/docs
