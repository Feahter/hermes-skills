# Memory Palace — 三层记忆路由系统

## 架构概览

```
session 启动
  └─ MemoryStore.load_from_disk()
       ├─ memory/_index.md 存在？→ Memory Palace Mode
       │    ├─ Layer 1 (always): SOUL.md + AGENTS.md + USER.md + _index.md → _system_prompt_snapshot
       │    └─ 路由表 → _routing_table
       └─ 无 _index.md？→ 传统 entry 模式（MEMORY.md entries 逐条加载）

per-turn prefetch
  └─ MemoryManager.prefetch_all(query)
       ├─ 外部 provider.prefetch()  (Honcho/Mem0等)
       └─ MemoryStore.prefetch(query)  ← 关键词路由核心
            ├─ 匹配 OFTEN/ON-DEMAND 路由条目（keyword in query）
            ├─ 读取对应 memory/*.md 文件
            └─ 拼接为 recall 文本 → 注入用户消息
```

## 关键文件

| 文件 | 作用 |
|------|------|
| `tools/memory_tool.py` | `MemoryStore` 类，同时是 memory tool 实现 + MemoryProvider 接口 |
| `agent/memory_manager.py` | `MemoryManager` — 管理多个 MemoryProvider，统一调用 prefetch/sync_turn |
| `run_agent.py` | 将 `MemoryStore` 注册为 MemoryProvider 的调用点（行 ~1930） |
| `agent/memory_provider.py` | MemoryProvider 抽象基类接口定义 |
| `memory/_index.md` | 路由表入口 |

## MemoryStore 新增字段

```python
self._is_memory_palace: bool    # 是否启用 palace 模式
self._routing_table: Dict       # section → {keywords, policy, path}
self._loaded_layers: set         # 已加载的 Layer 2/3 文件路径
```

## MemoryProvider 接口（MemoryStore 已实现）

```python
@property name(self) → "builtin"
is_available(self) → True
initialize(self, session_id, **kwargs) → no-op (load_from_disk 已完成初始化)
system_prompt_block(self) → ""  (frozen snapshot 走 format_for_system_prompt)
prefetch(self, query, session_id) → str  # 关键词路由，核心方法
get_tool_schemas(self) → []
handle_tool_call(self, tool_name, args) → raise
sync_turn(self, user_content, assistant_content) → no-op
```

## _index.md 格式

```markdown
# 记忆宫殿索引 — 路由表

| Section | Keywords | Load Policy | File Path |
|---------|---------|------------|-----------|
| Skills Knowledge | skill, 三层, gotcha, description, trigger | OFTEN | evolution/skills-knowledge.md |
| Key Learnings | openclaw, cron, 死锁, 两个openclaw.json | ON-DEMAND | evolution/key-learnings.md |
```

## 改动记录

### run_agent.py memory 初始化逻辑（2026-05-13）

**改动前：** 只有配置了 `memory.provider` 时才创建 MemoryManager
**改动后：** 始终创建 MemoryManager（当 MemoryStore 存在时），外部 provider 和 MemoryStore 并存

```python
# 旧逻辑
if _mem_provider_name:
    self._memory_manager = _MemoryManager()
    _mp = _load_mem(_mem_provider_name)
    ...

# 新逻辑
self._memory_manager = _MemoryManager()
if _mem_provider_name:
    _mp = _load_mem(_mem_provider_name)
    if _mp and _mp.is_available():
        self._memory_manager.add_provider(_mp)
# MemoryStore 注册为 Provider（启用 palace prefetch 路由）
if self._memory_store is not None:
    self._memory_manager.add_provider(self._memory_store)
```
