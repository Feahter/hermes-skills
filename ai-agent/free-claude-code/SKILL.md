---
name: free-claude-code
description: |
  Claude Code 零成本路由代理 — 将 Claude Code 的 Anthropic API 调用路由到免费/低成本后端。
  触发：安装/启动/配置 free-claude-code、Claude Code 零成本、API 路由代理
triggers:
  - "free-claude-code"
  - "Claude Code 零成本"
  - "API 路由代理"
  - "nvidia nim claude"
---

# free-claude-code

## 状态

✅ **已安装** — `~/free-claude-code`，服务运行在 `http://localhost:8082`

## 快速启动

```bash
cd ~/free-claude-code
./start.sh 8082
```

健康检查：
```bash
curl http://localhost:8082/health
# → {"status":"healthy"}
```

## 配置

`~/free-claude-code/.env` — 当前配置：

```env
MODEL_HAIKU="open_router/stepfun/step-3.5-flash:free"
MODEL_OPUS="open_router/anthropic/claude-sonnet-4.5:free"
MODEL_SONNET="open_router/anthropic/claude-haiku-3.5:free"
ENABLE_MODEL_THINKING=true
```

OPENROUTER_API_KEY 从 `~/.zshrc` 继承，**无需重复填入 .env**。

## 使用方式

### Claude Code CLI 套代理

```bash
ANTHROPIC_BASE_URL="http://localhost:8082" ANTHROPIC_AUTH_TOKEN="freecc" claude
```

### 多 Provider 路由（需 NVIDIA NIM key）

拿到 NVIDIA NIM key 后，修改 `.env`：

```env
NVIDIA_NIM_API_KEY="nvapi-..."
MODEL_OPUS="nvidia_nim/moonshotai/kimi-k2.5"
MODEL_SONNET="nvidia_nim/z-ai/glm4.7"
MODEL_HAIKU="nvidia_nim/stepfun-ai/step-3.5-flash"
```

NVIDIA NIM 免费 40 req/min，远超 OpenRouter 每日 50 次限制。

## 架构

```
Claude Code CLI → Proxy (:8082) → OpenAI-compatible Provider
Anthropic SSE               NVIDIA NIM / OpenRouter / DeepSeek / LM Studio
```

**Provider 前缀格式：** `provider_prefix/model/name`

| Provider | 前缀 | API Key |
|----------|------|---------|
| NVIDIA NIM | `nvidia_nim/...` | NVIDIA_NIM_API_KEY |
| OpenRouter | `open_router/...` | OPENROUTER_API_KEY |
| DeepSeek | `deepseek/...` | DEEPSEEK_API_KEY |
| LM Studio | `lmstudio/...` | 无（本地） |
| llama.cpp | `llamacpp/...` | 无（本地） |

## 核心文件

- `server.py` — Uvicorn 入口
- `api/app.py` — FastAPI 应用
- `providers/` — 各 Provider 实现
- `core/anthropic/` — Anthropic→OpenAI 协议转换
- `start.sh` — 启动脚本

## 已知问题

- `ENABLE_THINKING` 在 v2.0.0 已移除，改用 `ENABLE_MODEL_THINKING` / `ENABLE_OPUS_THINKING` 等细粒度字段
