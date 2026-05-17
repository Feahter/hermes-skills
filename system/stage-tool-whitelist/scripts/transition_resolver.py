"""
Transition Resolver — 状态转换解析器（移植自 Statewright crates/engine/src/transition.rs）

功能：
  - resolve_transition()：解析事件，找到目标状态，求值 guard
  - apply_context_patch()：shallow merge event data 到 context
  - resolve_event()：从 state machine definition 解析转换

无 LLM 依赖。
"""

from typing import Any, TypedDict
from dataclasses import dataclass, field

try:
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from guard_engine import evaluate_guards
except ImportError:
    from guard_engine import evaluate_guards  # type: ignore


class TransitionResult(TypedDict, total=False):
    new_state: str
    new_context: dict
    transitioned: bool
    requires_approval: bool
    approval_message: str | None
    error: str | None


class TransitionError(Exception):
    pass


class NoMatchingTransition(TransitionError):
    pass


class GuardFailed(TransitionError):
    pass


class StateNotFound(TransitionError):
    pass


# ------------------------------------------------------------------
# Context patch (shallow merge)
# ------------------------------------------------------------------

def apply_context_patch(context: dict, patch: dict) -> dict:
    """
    Shallow merge patch fields into context.
    来自 Statewright apply_context_patch。
    """
    result = dict(context)
    for k, v in patch.items():
        result[k] = v
    return result


# ------------------------------------------------------------------
# Transition resolution
# ------------------------------------------------------------------

def resolve_transition(
    current_state: str,
    event: str,
    event_data: dict,
    context: dict,
    states: dict[str, dict],
    guards: dict[str, dict] | None = None,
) -> TransitionResult:
    """
    解析状态转换。

    Args:
        current_state: 当前状态名
        event: 触发事件名（如 "PASS", "FAIL", "READY"）
        event_data: 事件携带的数据（会 shallow merge 到 context）
        context: 当前状态机 context
        states: 状态定义 dict，{"state_name": {"on": {...}, ...}}
        guards: 可选的 guard 定义 {"guard_name": {"field": ..., "op": ..., "value": ...}}

    Returns:
        TransitionResult with new_state, new_context, transitioned, requires_approval, approval_message, error

    Raises:
        StateNotFound: 当前状态不在 states 里
        NoMatchingTransition: 事件没有对应的 transition
        GuardFailed: guard 条件求值失败
    """
    guards = guards or {}

    if current_state not in states:
        raise StateNotFound(f"State '{current_state}' not found in definition")

    state_def = states[current_state]
    on_events = state_def.get("on", {})

    # 找 transition
    transition_def = on_events.get(event)

    # fallback: safe_next
    if transition_def is None and state_def.get("safe_next"):
        return {
            "ok": True,
            "new_state": state_def["safe_next"],
            "new_context": apply_context_patch(context, event_data),
            "transitioned": True,
            "requires_approval": False,
            "approval_message": None,
            "error": None,
        }

    if transition_def is None:
        raise NoMatchingTransition(
            f"No transition for event '{event}' in state '{current_state}'"
        )

    # 解析 transition def
    # 支持三种格式：
    # 1. "target_state" (Simple)
    # 2. {"target": "state", "guard": "guard_name", "requires_approval": true, ...}
    # 3. {"guards": [...]} (XState guarded style)

    if isinstance(transition_def, str):
        # Simple: just a target state name
        target = transition_def
        guard_names = []
        requires_approval = False
        approval_message = None

    elif isinstance(transition_def, dict):
        # Full or Guarded
        if "guards" in transition_def and "target" not in transition_def:
            # Guarded array (XState pattern) — first matching branch wins
            branches = transition_def["guards"]
            matched = False
            for branch in branches:
                branch_guard_names = branch.get("guards", [])
                if evaluate_guards(branch_guard_names, guards, context):
                    target = branch["target"]
                    guard_names = []
                    requires_approval = branch.get("requires_approval", False)
                    approval_message = branch.get("approval_message")
                    matched = True
                    break
            if not matched:
                raise GuardFailed(f"No guard matched for event '{event}' in state '{current_state}'")
        else:
            # Full transition
            target = transition_def.get("target", "")
            guard_names = []
            if "guard" in transition_def and transition_def["guard"]:
                guard_names = [transition_def["guard"]]
            if "guards" in transition_def and isinstance(transition_def["guards"], list):
                guard_names = transition_def["guards"]
            requires_approval = transition_def.get("requires_approval", False)
            approval_message = transition_def.get("approval_message")
    else:
        raise NoMatchingTransition(f"Invalid transition def for event '{event}'")

    # 求值 guards
    if guard_names:
        if not evaluate_guards(guard_names, guards, context):
            guard_list = ", ".join(guard_names)
            raise GuardFailed(f"Guard(s) failed: {guard_list} for event '{event}'")

    # 计算新 context
    new_context = apply_context_patch(context, event_data)

    result = {
        "ok": True,
        "new_state": target,
        "new_context": new_context,
        "transitioned": True,
        "requires_approval": requires_approval,
        "approval_message": approval_message,
        "error": None,
    }
    return result


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------
if __name__ == "__main__":
    # Bugfix workflow: planning → implementing → testing → review
    states = {
        "planning": {
            "on": {"READY": "implementing"},
            "safe_next": "implementing",
        },
        "implementing": {
            "on": {"DONE": "testing"},
        },
        "testing": {
            "on": {
                "PASS": {"target": "review", "guard": "tests_passed"},
                "FAIL": "implementing",
            },
        },
        "review": {
            "on": {"APPROVE": "completed"},
        },
        "completed": {"type": "final"},
    }

    guards = {
        "tests_passed": {"field": "test_result", "op": "eq", "value": "pass"},
    }

    # Test 1: simple transition
    r = resolve_transition("planning", "READY", {}, {}, states, guards)
    assert r["new_state"] == "implementing", f"Test1 failed: {r}"
    print("✓ Test1: planning → implementing")

    # Test 2: guarded transition (guard passes)
    r = resolve_transition("testing", "PASS", {}, {"test_result": "pass"}, states, guards)
    assert r["new_state"] == "review", f"Test2 failed: {r}"
    print("✓ Test2: testing → review (guard passes)")

    # Test 3: guarded transition (guard fails)
    try:
        r = resolve_transition("testing", "PASS", {}, {"test_result": "fail"}, states, guards)
        assert False, "Should have raised GuardFailed"
    except GuardFailed:
        print("✓ Test3: testing → review blocked by guard")

    # Test 4: transition with FAIL
    r = resolve_transition("testing", "FAIL", {}, {}, states, guards)
    assert r["new_state"] == "implementing", f"Test4 failed: {r}"
    print("✓ Test4: testing → implementing (FAIL)")

    # Test 5: context patch
    r = resolve_transition("implementing", "DONE", {"file": "main.py"}, {"count": 1}, states, guards)
    assert r["new_context"] == {"count": 1, "file": "main.py"}, f"Test5 failed: {r}"
    print("✓ Test5: context patch works")

    # Test 6: safe_next fallback
    r = resolve_transition("planning", "UNKNOWN_EVENT", {}, {}, states, guards)
    assert r["new_state"] == "implementing", f"Test6 failed: {r}"
    print("✓ Test6: safe_next fallback works")

    # Test 7: no matching transition
    try:
        r = resolve_transition("planning", "RANDOM", {}, {}, states, guards)
        assert False, "Should have raised NoMatchingTransition"
    except NoMatchingTransition:
        print("✓ Test7: NoMatchingTransition raised")

    print("\nAll tests passed!")
