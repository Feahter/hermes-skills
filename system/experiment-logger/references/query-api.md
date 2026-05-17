# experiment-logger 查询 API 与 skill-combinator 联动

## 新增查询方法（Plan A, 2026-05-15）

### `get_real_invocation_stats(min_samples=1) -> dict`

返回所有有真实调用的 skill 统计，格式：

```python
{
  "skill_name": {
    "total": 5,           # 总调用次数
    "success": 4,         # 成功次数
    "partial": 0,         # 部分成功
    "fail": 1,            # 失败次数
    "success_rate": 0.8,  # 成功率 (0.0-1.0)
    "avg_latency_ms": 1234.5,
    "top_query_keywords": {"python": 3, "代码": 2, ...},  # top 20
    "was_correct_rate": None,  # 回填后才有值
  }
}
```

**用途**：skill-combinator 的 `stage1_search_index()` 在 scoring 后调用此方法，用真实成功率对候选做 boost：

```python
boost = (success_rate - 0.5) * 4
# 成功 100% → +2.0,  成功 50% → 0,  成功 0% → -2.0
```

**调用路径**（从 `skill-combinator/scripts/pipeline.py`）：

```python
exp_dir = Path(__file__).parent.parent.parent.parent / ".experiment_log"
sys.path.insert(0, str(exp_dir))
from skill_logger import SkillLogger
logger = SkillLogger()
stats = logger.get_real_invocation_stats(min_samples=1)
```

**注意**：`skills/.experiment_log` 固定在 `~/.hermes/skills/.experiment_log`，与 skill 的嵌套层级无关。

---

### `get_skill_cooccurrence() -> dict`

返回同一 query 的多次调用（协作链）：

```python
{
  "markdown-prettier": ["neat-freak"],
  "neat-freak": ["markdown-prettier"],
}
```

**用途**：co-occurring skills 之间互相 +0.5 boost。

---

## skill_combinator 选择上下文字段

Plan A 新增于 `log_invocation_start()` 的参数：

```python
logger.log_invocation_start(
    skill_name="coding-agent",
    query="帮我写排序",
    skill_combinator_candidates=[{"name": "coding-agent", "score": 8.5}, ...],
    skill_combinator_top_score=8.5,
)
```

对应记录结构：

```json
{
  "skill_combinator": {
    "candidates": [...],
    "top_score": 8.5,
    "was_correct": null,
    "selection_error": null
  }
}
```

- `was_correct`：事后由 skill-combinator 回填（True/False）
- `selection_error`：归因类型：`"wrong_skill"` | `"timeout"` | `None`

---

## Python 环境注意

`skill_logger.py` 依赖 `jieba`（中文分词）。`jieba` 不在 hermes-agent venv 中，在系统 anaconda：

```bash
# 可用
/opt/anaconda3/bin/python3 -c "import jieba"  # ✅

# 不可用
~/.hermes/hermes-agent/venv/bin/python -c "import jieba"  # ❌ ModuleNotFoundError
```

调试时使用 `/opt/anaconda3/bin/python3`，或在脚本内加 `sys.path` 切换。

---

## 数据 Null 安全模式

invocation 记录中部分字段可能为 `None`（尤其是 seed 数据或未完成的记录），读取时需防御：

```python
# ✅ 正确
latency = (record.get("output") or {}).get("latency_ms")
query = (record.get("input") or {}).get("query", "")
sc = (record.get("skill_combinator") or {})

# ❌ 错误（假设 dict 默认值）
latency = record.get("output", {}).get("latency_ms")  # AttributeError: 'NoneType'
```
