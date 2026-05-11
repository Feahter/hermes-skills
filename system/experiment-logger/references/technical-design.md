# experiment-logger 技术细节

## 设计决策备忘录

### 为什么用 JSONL 而不是 SQLite

- **简单性**：grep 即可查，无需额外依赖
- **append-only**：天然日志语义，无并发写冲突
- **缺点**：大量小文件，查询需全表扫描

### 为什么失败案例用 skill 名 + 日期命名

```python
# 文件命名格式
{failed_skill}__{YYYY-MM-DD}.jsonl

# 示例
coding-agent__2026-05-11.jsonl
```

好处：按 Skill + 日期聚合，失败案例积累后按文件名过滤即可快速定位。

### invocation_id 用 UUID 的理由

- 并发写入不冲突
- 可追溯
- 代价：文件名不好记（但有 CLI 可查）

### boundary 签名的质量衰减曲线

```python
quality_decay_curve = {
    "0-100": 0.95,    # 短 query 质量高
    "100-300": 0.88,
    "300-500": 0.75,
    "500-1000": 0.60,
    "1000-2000": 0.41,
    "2000+": 0.23,
}
```

这是被动扫描从历史数据推断的，不是先验的。随着数据积累，曲线会修正。

### 对抗性探测的局限

`--probe` 目前使用 mock executor，实际使用时需要替换为真实 Skill 执行器。框架是对的，但具体阈值需要调优。

### 与 skill-evolution-manager 的边界

| 组件 | 职责 |
|------|------|
| experiment-logger | 数据采集、质量信号、边界探测 |
| skill-evolution-manager | 经验提炼、写入 SKILL.md |

两者通过 fail_cases 间接联动：experiment-logger 积累失败案例 → skill-evolution-manager 读取并提炼经验。
