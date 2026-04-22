# 规则引擎与自我演进机制

## 规则版本化

```
v1.0.0 (2026-04-20) — 初始规则集
├── credential: 7 rules
├── network: 5 rules
├── permission: 6 rules
└── code: 6 rules
```

## 演进流程

```
每次扫描
    ↓
Layer 3 元认知分析
    ↓
┌─────────────────────────────────────────────┐
│ 新 Pattern 发现？ → 添加到 RULES 列表        │
│ False Positive 过多？ → 调整 severity        │
│ 漏检率高？ → 增加覆盖维度                     │
└─────────────────────────────────────────────┘
    ↓
生成 rules_v{N+1}.md 增量文件
    ↓
skill-audit update-rules 合并增量
```

## 演进触发条件

| 触发 | 条件 | 动作 |
|------|------|------|
| 新增规则 | 扫描中发现未覆盖危险模式 | 添加新 DangerRule |
| 降级规则 | False Positive > 30% | severity -1 |
| 升级规则 | 漏检导致安全事故 | severity +1 |
| 合并规则 | 多规则检测同一问题 | 合并并标注 |

## 危险分类维度

| Category | 说明 | 覆盖维度 |
|----------|------|----------|
| credential | 凭证/密钥访问 | 读取敏感文件、请求API key |
| network | 网络行为 | HTTP传输、数据外传、IP直连 |
| permission | 系统权限 | sudo、shell配置、全局安装 |
| code | 代码执行 | eval、subprocess、混淆代码 |

## 分数计算

```
raw_score = Σ(severity × match_count) for all triggered rules
trust_penalty = 1.5 - (trust_score - 1) × 0.225
final_score = raw_score × trust_penalty

风险阈值:
- final >= 5.0 → ⛔ BLOCK
- final >= 3.0 → 🚨 DANGER
- final >= 1.0 → ⚠️ WARNING
- final < 1.0 → ⚪ CLEAN
```
