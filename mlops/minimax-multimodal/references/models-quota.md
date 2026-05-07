# MiniMax 文本模型 & 用量查询参考

## 官方 API（Token Plan / Pay-as-you-go）

**Base URL**: `https://api.minimaxi.com/anthropic`（Anthropic 兼容协议）

### 可用模型

| 模型 | 输出速度 | Token Plan 支持 | 按量付费支持 |
|------|---------|----------------|-------------|
| `MiniMax-M2.7` | ~60 tps | ✅ | ✅ |
| `MiniMax-M2.7-highspeed` | ~100 tps | ❌ 需高级套餐 | ✅ |
| `MiniMax-M2.5` | ~60 tps | ✅ | ✅ |
| `MiniMax-M2.5-highspeed` | ~100 tps | ❌ 需高级套餐 | ✅ |
| `MiniMax-M2.1` | ~60 tps | ✅ | ✅ |
| `MiniMax-M2.1-highspeed` | ~100 tps | ❌ 需高级套餐 | ✅ |

### 高速度模型错误

如果套餐不支持 highspeed，API 返回：
```json
{"type":"error","error":{"type":"api_error","message":"your current token plan not support model, MiniMax-M2.7-highspeed (2061)"}}
```

**解法**：升级 Token Plan 或切换按量付费

---

## OpenRouter 访问

**Base URL**: `https://openrouter.ai/api/v1`

OpenRouter 上的 minimax 模型（**无 highspeed**）：
- `minimax/minimax-m2.7`
- `minimax/minimax-m2.5`
- `minimax/minimax-m2.5:free`
- `minimax/minimax-m2.1`
- `minimax/minimax-m2`
- `minimax/minimax-m2-her`
- `minimax/minimax-m1`
- `minimax/minimax-01`

### 查询 OpenRouter 余额

```bash
curl -s -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  "https://openrouter.ai/api/v1/auth/key"
```

返回字段：`usage`（已用）、`is_free_tier`、limit 相关字段

---

## 官方用量查询

### Coding Plan（Token Plan 独立端点）

```bash
curl -s -H "Authorization: Bearer <API_KEY>" \
  "https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains"
```

返回：`model_remains[]` 数组，含 `current_interval_total_count` 和 `current_interval_usage_count`

> ⚠️ 通用大模型余额接口和 Coding Plan 接口是**独立的**，不通用。

### 通用余额（需登录）

网页端：[platform.minimaxi.com](https://platform.minimaxi.com) → 账户管理 → 余额

---

## 配置注意

Hermes/OpenClaw 配置中的 provider name：
- 官方 API → `minimax`（不是 `minimax-cn`）
- provider `minimax-cn` 不在标准 providers 列表中，会导致静默 fallback

OpenClaw minimax provider 配置：
```json
"minimax": {
  "baseUrl": "https://api.minimaxi.com/anthropic",
  "apiKey": "sk-cp-...",
  "api": "anthropic-messages",
  "models": ["MiniMax-M2.1", "MiniMax-M2.5", "MiniMax-M2.7"]
}
```

---

## 关键发现（2026-05-04）

1. **Token Plan 不支持 highspeed** — 订阅的是基础 Token Plan，`MiniMax-M2.7-highspeed` 返回错误码 2061
2. **官方 API 直连返回 500** — 可能需检查 API Key 权限或账户状态
3. **hermes config provider 应为 `minimax`** — 当前配置 `minimax-cn` 需核实是否有意为之
