"""
Guard Engine — 确定性条件求值器（移植自 Statewright crates/engine/src/guard.rs）

支持的操作：
  Eq, Neq, Gt, Gte, Lt, Lte, Exists, NotExists, In, Contains

无 LLM 依赖，纯函数。
"""

from typing import Any, TypedDict

try:
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
except ImportError:
    pass


class GuardOp:
    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"
    IN = "in"
    CONTAINS = "contains"


class GuardDef(TypedDict, total=False):
    field: str
    op: str
    value: Any


def _get_field(context: dict, field: str) -> Any:
    """从嵌套 context dict 中按 dot-notation 取值。"""
    keys = field.split(".")
    val = context
    for k in keys:
        if isinstance(val, dict):
            val = val.get(k)
        else:
            return None
    return val


def _compare_numbers(a: Any, b: Any, cmp: callable) -> bool:
    """比较两个值作为数字。无法解析为数字返回 False。"""
    try:
        a_num = float(a)
        b_num = float(b)
        return cmp(a_num, b_num)
    except (TypeError, ValueError):
        return False


def evaluate_guard(guard: GuardDef, context: dict) -> bool:
    """
    求值单个 guard 条件。

    Args:
        guard: {"field": "...", "op": "eq", "value": ...}
        context: 状态机 context dict（shallow merge 后的结果）

    Returns:
        True if condition satisfied, False otherwise
    """
    field = guard.get("field", "")
    op = guard.get("op", "").lower()
    expected = guard.get("value")
    field_value = _get_field(context, field)

    # Exists / NotExists
    if op == GuardOp.EXISTS:
        return field_value is not None
    if op == GuardOp.NOT_EXISTS:
        return field_value is None

    # Null context field treated as absent
    if field_value is None:
        return False

    # Eq / Neq
    if op == GuardOp.EQ:
        return field_value == expected
    if op == GuardOp.NEQ:
        return field_value != expected

    # Numeric comparisons
    if op == GuardOp.GT:
        return _compare_numbers(field_value, expected, lambda a, b: a > b)
    if op == GuardOp.GTE:
        return _compare_numbers(field_value, expected, lambda a, b: a >= b)
    if op == GuardOp.LT:
        return _compare_numbers(field_value, expected, lambda a, b: a < b)
    if op == GuardOp.LTE:
        return _compare_numbers(field_value, expected, lambda a, b: a <= b)

    # In
    if op == GuardOp.IN:
        if isinstance(expected, list):
            return field_value in expected
        return False

    # Contains (substring match)
    if op == GuardOp.CONTAINS:
        if isinstance(field_value, str) and isinstance(expected, str):
            return expected in field_value
        return False

    # Unknown op
    return False


def evaluate_guards(guard_names: list[str], guards: dict[str, GuardDef], context: dict) -> bool:
    """
    求值多个 guard（AND 逻辑：所有必须通过）。

    Args:
        guard_names: guard 定义名列表
        guards: {"guard_name": GuardDef, ...}
        context: 状态机 context

    Returns:
        True if ALL guards pass
    """
    for name in guard_names:
        guard_def = guards.get(name)
        if guard_def is None:
            # Unknown guard = fail
            return False
        if not evaluate_guard(guard_def, context):
            return False
    return True


# ------------------------------------------------------------------
# Tests (run with: python guard_engine.py)
# ------------------------------------------------------------------
if __name__ == "__main__":
    import json

    test_cases = [
        # Eq
        ({"field": "status", "op": "eq", "value": "draft"}, {"status": "draft"}, True),
        ({"field": "status", "op": "eq", "value": "draft"}, {"status": "published"}, False),
        # Neq
        ({"field": "status", "op": "neq", "value": "draft"}, {"status": "published"}, True),
        # Gt
        ({"field": "count", "op": "gt", "value": 5}, {"count": 10}, True),
        ({"field": "count", "op": "gt", "value": 5}, {"count": 5}, False),
        # Gte
        ({"field": "count", "op": "gte", "value": 5}, {"count": 5}, True),
        # Lt
        ({"field": "count", "op": "lt", "value": 10}, {"count": 3}, True),
        # Lte
        ({"field": "count", "op": "lte", "value": 5}, {"count": 5}, True),
        # Exists
        ({"field": "email", "op": "exists"}, {"email": "a@b.com"}, True),
        ({"field": "email", "op": "exists"}, {}, False),
        ({"field": "email", "op": "exists"}, {"email": None}, False),
        # NotExists
        ({"field": "deleted_at", "op": "not_exists"}, {"deleted_at": None}, True),
        ({"field": "deleted_at", "op": "not_exists"}, {"deleted_at": "2024-01-01"}, False),
        # In
        ({"field": "status", "op": "in", "value": ["draft", "pending"]}, {"status": "draft"}, True),
        ({"field": "status", "op": "in", "value": ["draft", "pending"]}, {"status": "published"}, False),
        # Contains
        ({"field": "name", "op": "contains", "value": "foo"}, {"name": "foobar"}, True),
        ({"field": "name", "op": "contains", "value": "foo"}, {"name": "barbaz"}, False),
        # Nested field
        ({"field": "user.email", "op": "eq", "value": "a@b.com"}, {"user": {"email": "a@b.com"}}, True),
        # Numeric as strings
        ({"field": "count", "op": "gt", "value": 5}, {"count": "10"}, True),
        ({"field": "count", "op": "gt", "value": 5}, {"count": "abc"}, False),
    ]

    passed = 0
    for guard, context, expected in test_cases:
        result = evaluate_guard(guard, context)
        status = "✓" if result == expected else "✗"
        if result == expected:
            passed += 1
        print(f"{status} {guard['op']:12} | ctx={json.dumps(context)[:40]:40} | expected={expected} | got={result}")

    print(f"\n{passed}/{len(test_cases)} passed")
