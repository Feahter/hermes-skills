# OpenRouter + MiniMax 模型路由发现

**日期**：2026-05-04

## 当前配置

- **Provider**：`minimax-cn`（Hermes 主对话）
- **主对话模型**：`MiniMax-M2.7` via `minimax-cn` provider
- **OpenRouter API Key**：免费版（`is_free_tier: true`，0 消费）

## OpenRouter 上的 MiniMax 模型（2026-05-04 快照）

```
minimax/minimax-m2.7
minimax/minimax-m2.5:free
minimax/minimax-m2.5
minimax/minimax-m2-her
minimax/minimax-m2.1
minimax/minimax-m2
minimax/minimax-m1
minimax/minimax-01
```

**注意**：没有 `minimax-m2.7-highspeed`，没有 `minimax-m2.1-highspeed`。

## Highspeed 型号

| 型号 | 存在位置 | 输出速度 |
|------|----------|---------|
| `MiniMax-M2.7-highspeed` | MiniMax 官方 `api.minimaxi.com` | ~100 tps |
| `MiniMax-M2.5-highspeed` | MiniMax 官方 `api.minimaxi.com` | ~100 tps |
| `MiniMax-M2.1-highspeed` | MiniMax 官方 `api.minimaxi.com` | ~100 tps |
| OpenRouter | **均不提供** | — |

## 用量查询

### OpenRouter 余额
```bash
curl -s -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  "https://openrouter.ai/api/v1/auth/key"
```
返回：`{"usage": 0, "is_free_tier": true, "limit_remaining": null}`

### MiniMax 官方（需 Cookie 认证，API Key 不够）
```
GET https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains
```
需要登录态，API Key 直连会报 `cookie is missing`。

## Subagent 模型指定问题

调用 `delegate_task` 时指定 `model: {"provider": "minimax", "model": "minimax-8b"}`：

- **结果**：静默降级，未报错，实际使用了默认的 `MiniMax-M2.7`
- **根因**：Hermes 的 delegate_task 不校验 model ID 是否存在于 provider
- **影响**：无法通过此方式测试高速型号
- **解决**：需要先确认 provider 配置中确实存在该 model ID

## 建议

若要使用 highspeed 模型，需：
1. 配置 `minimax` provider（API Key 直连 `api.minimaxi.com`），显式注册 `MiniMax-M2.7-highspeed` 等型号
2. 或接受 OpenRouter 的 60 tps（普通 M2.7），不追求 100 tps
