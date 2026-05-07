---
name: hermes-agent-tool-authoring
description: Create self-registering tools for hermes-agent. Covers the real registration pattern (registry.register vs @register decorator), schema format, toolset setup, and discovery mechanism.
triggers:
  - create a tool for hermes-agent
  - add a new tools/*.py file
  - tool not registering properly
---

# hermes-agent Tool Authoring

Create new tools for hermes-agent that auto-register and auto-discover.

## Tool Registration Pattern (CRITICAL)

**Docstrings show `@register` decorator — IGNORE THIS.** The actual pattern is direct `registry.register()` call at module level.

### Correct Pattern

```python
from tools.registry import registry

def my_tool_handler(arg1: str, arg2: int = 0) -> str:
    """Tool implementation — returns JSON string."""
    import json
    return json.dumps({"result": "ok"})

registry.register(
    name="my_tool",           # tool name as called by LLM
    toolset="my_toolset",     # must match a key in toolsets.py TOOLSETS dict
    schema={
        "description": "One-line description for the LLM.",
        "type": "object",
        "properties": {
            "arg1": {"type": "string", "description": "Description."},
            "arg2": {"type": "integer", "description": "Optional, defaults to 0."},
        },
        "required": ["arg1"],
    },
    handler=my_tool_handler,
    description="Short description shown in listings.",  # separate from schema
    emoji="🔧",  # optional
)
```

### Common Mistakes

| Mistake | Correction |
|---------|------------|
| `@register(...)` decorator | Use `registry.register(...)` at module level |
| `parameters={...}` inside register() | Use `schema={...}` with OpenAPI-style object |
| `description` inside schema dict | `description` goes in `schema["description"]` AND as separate `description=` kwarg |
| Tool not appearing after creation | AST scanner only detects `registry.register(...)` at **module body level** (not inside functions/classes) |

### Tool Discovery Mechanism

`tools/registry.py` uses AST scanning (`_module_registers_tools`) to find tools at import time:
- Only top-level statements in the module are scanned
- `registry.register(...)` must appear directly in the module body
- Helper functions that call `registry.register()` inside them are NOT discovered

## Steps

1. **Create file**: `tools/<tool_name>_tool.py`
2. **Implement handler**: function that takes typed params, returns JSON string
3. **Register**: `registry.register(...)` at module top-level
4. **Add to toolset**: Add entry in `toolsets.py` `TOOLSETS` dict, e.g.:
   ```python
   "my_toolset": {
       "description": "...",
       "tools": ["my_tool"],
       "includes": [],
   },
   ```
5. **Verify**:
   ```python
   from tools.registry import registry, discover_builtin_tools
   discover_builtin_tools()
   entry = registry._tools.get('my_tool')
   assert entry is not None, "Tool not registered!"
   ```

## Integration Points

- **run_agent.py `_invoke_tool()`**: Unified tool dispatch for sequential + concurrent paths. Tool hooks here apply to all tools automatically.
- **model_tools.py `handle_function_call()`**: Legacy per-tool dispatch, quiet_mode path.
- **tools/registry.py**: Tool discovery and `ToolEntry` metadata.
