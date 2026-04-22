---
name: lightrag-anthropic-setup
description: Deploy LightRAG as FastAPI HTTP service using Anthropic Claude for LLM plus embedded backends. Triggers include deploying LightRAG, adding RAG to wiki or knowledge base, and multi-hop reasoning over local documents.
version: 0.1
tags: [lightrag, rag, anthropic, fastapi, knowledge-base]
---

# LightRAG + Anthropic HTTP Service Setup

## Architecture

LightRAG as HTTP API via FastAPI and uvicorn. Hermes queries via HTTP POST.
Data stored in `lightrag_data/` directory.

## Prerequisites

```bash
pip install "lightrag-hku[api]"
pip install anthropic voyageai aiohttp
```

## Core Initialization Pattern

```python
from lightrag import LightRAG
from lightrag.llm.anthropic import anthropic_complete
from lightrag.utils import wrap_embedding_func_with_attrs

llm_fn = anthropic_complete

embed_fn = wrap_embedding_func_with_attrs(
    embedding_dim=1024,
    max_token_size=8192,
    model_name="voyage-3"
)(anthropic_embed)

rag = LightRAG(
    working_dir="./lightrag_data",
    llm_model_func=llm_fn,
    llm_model_name="claude-sonnet-4-7-202570",
    embedding_func=embed_fn,
)
```

Critical: embedding_func MUST be wrapped with wrap_embedding_func_with_attrs. Raw functions cause AttributeError.

## Embedding Backend Options

| Backend | Dim | API Key | Notes |
|---------|-----|---------|-------|
| anthropic_embed (voyage-3) | 1024 | VOYPAGE_API_KEY | voyageai SDK breaks if PyTorch < 2.4 |
| jina_embed | 2048 | JINA_API_KEY | Free tier works |
| HuggingFace sentence-transformers | varies | free | Needs PyTorch >= 2.4 |

## HTTP Endpoints

POST /query with {"query": str, "mode": "mix|local|global|hybrid|dev"}
POST /insert with {"text": str}
GET /health and GET /stats

## Known Blockers

hermes-agent venv has no pip — use anaconda python
PyTorch 2.2.2 in anaconda too old for sentence-transformers — pip cannot upgrade torch from conda env
voyageai SDK imports langchain which needs PyTorch >= 2.4
Dynamic pip install at import time — pre-install packages to avoid 30s hangs

## Fallback

Use mode="dev" to bypass vector retrieval when embedding is blocked.
