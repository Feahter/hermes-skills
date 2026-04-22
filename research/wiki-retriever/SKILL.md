---
name: wiki-retriever
description: |
  Wiki BM25 + wikilink 混合检索服务。LightRAG 的零依赖替代方案，基于 rank-bm25 实现，
  无需 PyTorch，已在 ~/wiki 验证可用（75 页索引）。
triggers:
  - "wiki 检索"
  - "wiki 搜索"
  - "wiki knowledge base"
  - "wiki retriever"
  - "wiki bm25"
metadata:
  wiki: {}
  py: {}
---

## 背景

为 ~/wiki 构建 RAG 向量检索时遇到 PyTorch 2.2.2（conda 锁定无法升级）和 embedding 服务卡死问题。
改用纯 Python 的 rank-bm25 + wikilink 图关系混合检索，无需 PyTorch，75 页 wiki 索引用时 <1s。

## 服务已部署

- **运行中**：`/opt/anaconda3/bin/python3 /Users/fuzhuo/.hermes/scripts/wiki_retriever.py`（端口 8021）
- **索引路径**：`~/wiki`（75 页 .md 文件）
- **检索方法**：BM25 + wikilink 图关系混合

## API

```bash
# 健康检查
curl http://127.0.0.1:8021/health

# 状态
curl http://127.0o.com:8021/stats

# 检索（POST）
curl -X POST http://127.0.0.1:8021/search \
  -H "Content-Type: application/json" \
  -d '{"query": "your query", "top_k": 3}'
```

## 响应格式

```json
{
  "results": [
    {"path": "concepts/XXX.md", "title": "Title", "snippet": "...", "score": 5.27}
  ],
  "total": 3
}
```

## 如果需要重启

```bash
kill $(lsof -ti:8021) 2>/dev/null
/opt/anaconda3/bin/python3 /Users/fuzhuo/.hermes/scripts/wiki_retriever.py &
```

## 架构

```
~/wiki/*.md → Markdown loader → BM25 tokenization
                                     ↓
wikilink graph (from [[link]] refs)  → 混合排序
                                     ↓
                              API /search
```

## 依赖

- `rank-bm25`（pip install）
- `fastapi` + `uvicorn`（已装在 anaconda）

## 可改进方向

1. **混合向量检索**：加入 sentence-transformers + ChromaDB（需要先升级 PyTorch）
2. **多跳推理**：将 wikilink 图展开为子图查询
3. **增量索引**：watch ~/wiki 变化，实时更新 BM25 索引
4. **摘要召回**：query 相关性高时返回完整页面而非 snippet
