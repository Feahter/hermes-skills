"""
Workflow Manager — StateWright 风格状态机加载和管理

功能：
  - 从 JSON 文件或 dict 加载 workflow 定义
  - 管理当前状态、context、step count
  - 提供工具 restriction 信息
  - 解析 transition，支持 guard 条件
"""

import json
import threading
import time
import os
from typing import Any, TypedDict

try:
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from guard_engine import evaluate_guard, evaluate_guards
    from transition_resolver import (
        resolve_transition, apply_context_patch,
        StateNotFound, NoMatchingTransition, GuardFailed
    )
except ImportError:
    from guard_engine import evaluate_guard, evaluate_guards  # type: ignore
    from transition_resolver import (
        resolve_transition, apply_context_patch,
        StateNotFound, NoMatchingTransition, GuardFailed
    )


# ------------------------------------------------------------------
# State / Workflow types (mirrors Statewright types.rs)
# ------------------------------------------------------------------

class StateDef(TypedDict, total=False):
    allowed_tools: list[str] | None
    allowed_commands: list[str] | None
    max_edit_lines: int | None
    max_files_per_state: int | None
    context_budget_bytes: int | None
    blocked_env: list[str] | None
    env_overrides: dict[str, str] | None
    safe_next: str | None
    instructions: str | None
    max_iterations: int | None
    on: dict[str, Any]


class WorkflowDef(TypedDict, total=False):
    id: str
    initial: str
    context: dict
    states: dict[str, StateDef]
    guards: dict[str, dict]
    meta: dict | None


# ------------------------------------------------------------------
# Workflow session state (thread-safe, per-session)
# ------------------------------------------------------------------

_workflow_lock = threading.Lock()
_workflow_sessions: dict[str, dict] = {}


def _get_key(session_id: str, task_id: str) -> str:
    return session_id or task_id or "default"


def _get_or_create_workflow(
    session_id: str,
    task_id: str,
    workflow_def: WorkflowDef | None = None,
) -> dict:
    key = _get_key(session_id, task_id)
    with _workflow_lock:
        if key not in _workflow_sessions:
            if workflow_def is None:
                return {}
            _workflow_sessions[key] = {
                "definition": workflow_def,
                "current_state": workflow_def.get("initial", ""),
                "context": dict(workflow_def.get("context", {})),
                "step_count": 0,
                "files_edited": [],
                "total_edit_lines": 0,
            }
        return _workflow_sessions[key]


def clear_workflow_session(session_id: str, task_id: str) -> None:
    key = _get_key(session_id, task_id)
    with _workflow_lock:
        _workflow_sessions.pop(key, None)


# ------------------------------------------------------------------
# Workflow loading
# ------------------------------------------------------------------

def load_workflow(source: str | dict) -> WorkflowDef:
    """
    加载 workflow 定义。

    Args:
        source: JSON 文件路径 或 dict

    Returns:
        WorkflowDef dict

    Raises:
        FileNotFoundError: 文件不存在
        json.JSONDecodeError: JSON 解析失败
    """
    if isinstance(source, dict):
        return source

    with open(source) as f:
        return json.load(f)


def load_workflow_from_path(path: str) -> WorkflowDef:
    """从文件加载 workflow。"""
    return load_workflow(path)


# ------------------------------------------------------------------
# State query
# ------------------------------------------------------------------

def get_current_state(session_id: str, task_id: str) -> str | None:
    """获取当前状态名。"""
    wf = _get_or_create_workflow(session_id, task_id)
    return wf.get("current_state")


def get_state_def(session_id: str, task_id: str, state_name: str | None = None) -> StateDef | None:
    """获取指定状态的定义。"""
    wf = _get_or_create_workflow(session_id, task_id)
    definition = wf.get("definition", {})
    states = definition.get("states", {})
    target = state_name or wf.get("current_state")
    return states.get(target)


def get_allowed_tools(session_id: str, task_id: str) -> list[str] | None:
    """获取当前状态的 allowed_tools。"""
    state_def = get_state_def(session_id, task_id)
    if state_def is None:
        return None
    return state_def.get("allowed_tools")


def get_allowed_commands(session_id: str, task_id: str) -> list[str] | None:
    """获取当前状态的 allowed_commands。"""
    state_def = get_state_def(session_id, task_id)
    if state_def is None:
        return None
    return state_def.get("allowed_commands")


def get_max_edit_lines(session_id: str, task_id: str) -> int | None:
    """获取当前状态的 max_edit_lines。"""
    state_def = get_state_def(session_id, task_id)
    if state_def is None:
        return None
    return state_def.get("max_edit_lines")


def get_max_files_per_state(session_id: str, task_id: str) -> int | None:
    """获取当前状态的 max_files_per_state。"""
    state_def = get_state_def(session_id, task_id)
    if state_def is None:
        return None
    return state_def.get("max_files_per_state")


def get_blocked_env(session_id: str, task_id: str) -> list[str] | None:
    """获取当前状态的 blocked_env。"""
    state_def = get_state_def(session_id, task_id)
    if state_def is None:
        return None
    return state_def.get("blocked_env")


def get_state_instructions(session_id: str, task_id: str) -> str | None:
    """获取当前状态的自定义指令。"""
    state_def = get_state_def(session_id, task_id)
    if state_def is None:
        return None
    return state_def.get("instructions")


# ------------------------------------------------------------------
# Transition
# ------------------------------------------------------------------

def transition(
    session_id: str,
    task_id: str,
    event: str,
    event_data: dict | None = None,
) -> dict:
    """
    执行状态转换。

    Args:
        session_id: 会话 ID
        task_id: 任务 ID
        event: 事件名（如 "PASS", "FAIL", "READY"）
        event_data: 事件携带的数据

    Returns:
        {"ok": True, "new_state": ..., "context": ..., "requires_approval": bool, "error": None}
        或 {"ok": False, "error": "..."}
    """
    wf = _get_or_create_workflow(session_id, task_id)
    if not wf:
        return {"ok": False, "error": "No active workflow"}

    definition = wf.get("definition", {})
    states = definition.get("states", {})
    guards = definition.get("guards", {})

    current_state = wf.get("current_state", "")
    context = wf.get("context", {})
    event_data = event_data or {}

    try:
        result = resolve_transition(
            current_state=current_state,
            event=event,
            event_data=event_data,
            context=context,
            states=states,
            guards=guards,
        )

        # Update session state
        wf["current_state"] = result["new_state"]
        wf["context"] = result["new_context"]

        return {
            "ok": True,
            "new_state": result["new_state"],
            "context": result["new_context"],
            "requires_approval": result.get("requires_approval", False),
            "approval_message": result.get("approval_message"),
            "error": None,
        }

    except (NoMatchingTransition, GuardFailed, StateNotFound) as e:
        return {"ok": False, "error": str(e)}


# ------------------------------------------------------------------
# Edit tracking (for max_files_per_state enforcement)
# ------------------------------------------------------------------

def record_file_edit(session_id: str, task_id: str, file_path: str, lines_changed: int) -> dict:
    """
    记录一次文件编辑，用于 max_files_per_state 追踪。

    Returns:
        {"ok": True} 或 {"ok": False, "reason": "..."}
    """
    wf = _get_or_create_workflow(session_id, task_id)
    if not wf:
        return {"ok": False, "reason": "No active workflow"}

    state_def = get_state_def(session_id, task_id)
    if state_def is None:
        return {"ok": False, "reason": "Unknown state"}

    max_files = state_def.get("max_files_per_state")
    max_lines = state_def.get("max_edit_lines")

    # Check file count
    if max_files is not None:
        current_files = set(wf.get("files_edited", []))
        if file_path not in current_files and len(current_files) >= max_files:
            return {
                "ok": False,
                "reason": f"max_files_per_state exceeded ({max_files} files max in state '{wf['current_state']}')",
            }

    # Check line count
    if max_lines is not None:
        total = wf.get("total_edit_lines", 0) + lines_changed
        if lines_changed > max_lines:
            return {
                "ok": False,
                "reason": f"edit exceeds max_edit_lines ({lines_changed} > {max_lines})",
            }
        wf["total_edit_lines"] = total

    # Record edit
    if file_path not in wf.get("files_edited", []):
        wf.setdefault("files_edited", []).append(file_path)

    return {"ok": True}


def reset_edit_tracking(session_id: str, task_id: str) -> None:
    """重置编辑追踪（进入新状态时调用）。"""
    wf = _get_or_create_workflow(session_id, task_id)
    if wf:
        wf["files_edited"] = []
        wf["total_edit_lines"] = 0


# ------------------------------------------------------------------
# Workflow activation
# ------------------------------------------------------------------

def activate_workflow(session_id: str, task_id: str, workflow_source: str | dict) -> dict:
    """
    激活一个 workflow。

    Returns:
        {"ok": True, "initial_state": "...", "context": {...}}
        或 {"ok": False, "error": "..."}
    """
    try:
        wf_def = load_workflow(workflow_source)
    except Exception as e:
        return {"ok": False, "error": f"Failed to load workflow: {e}"}

    if "states" not in wf_def:
        return {"ok": False, "error": "Workflow has no 'states' definition"}

    initial = wf_def.get("initial", "")
    if initial not in wf_def["states"]:
        return {"ok": False, "error": f"Initial state '{initial}' not in states"}

    key = _get_key(session_id, task_id)
    with _workflow_lock:
        _workflow_sessions[key] = {
            "definition": wf_def,
            "current_state": initial,
            "context": dict(wf_def.get("context", {})),
            "step_count": 0,
            "files_edited": [],
            "total_edit_lines": 0,
        }

    state_def = wf_def["states"][initial]
    return {
        "ok": True,
        "id": wf_def.get("id", "unknown"),
        "initial_state": initial,
        "context": wf_def.get("context", {}),
        "instructions": state_def.get("instructions"),
        "allowed_tools": state_def.get("allowed_tools"),
        "allowed_commands": state_def.get("allowed_commands"),
    }


# ------------------------------------------------------------------
# Built-in workflow templates
# ------------------------------------------------------------------

WORKFLOW_BUGFIX: WorkflowDef = {
    "id": "bugfix",
    "initial": "planning",
    "context": {"test_result": ""},
    "states": {
        "planning": {
            "instructions": "分析问题，只读文件，不要修改任何代码",
            "allowed_tools": ["Read", "Grep", "Glob"],
            "max_iterations": 8,
            "on": {"READY": "implementing"},
            "safe_next": "implementing",
        },
        "implementing": {
            "instructions": "实现修复，最多改 20 行，文件数不超过 3 个",
            "allowed_tools": ["Read", "Edit", "Write"],
            "max_edit_lines": 20,
            "max_files_per_state": 3,
            "allowed_commands": ["patch", "sed -i"],
            "on": {"DONE": "testing"},
            "safe_next": "testing",
        },
        "testing": {
            "instructions": "运行测试，验证修复是否成功",
            "allowed_tools": ["Read", "Bash"],
            "allowed_commands": ["pytest", "cargo test", "npm test"],
            "on": {
                "PASS": {"target": "review", "guard": "tests_passed"},
                "FAIL": "implementing",
            },
        },
        "review": {
            "instructions": "审查代码，确认没有引入新问题",
            "allowed_tools": ["Read", "Bash"],
            "on": {"APPROVE": "completed"},
        },
        "completed": {"type": "final", "instructions": "任务完成"},
    },
    "guards": {
        "tests_passed": {"field": "test_result", "op": "eq", "value": "pass"},
    },
}

WORKFLOW_TDD: WorkflowDef = {
    "id": "tdd",
    "initial": "write_test",
    "context": {},
    "states": {
        "write_test": {
            "instructions": "先写测试（必须是 failing test），不要写实现代码",
            "allowed_tools": ["Read", "Write"],
            "max_files_per_state": 2,
            "on": {"TEST_WRITTEN": "implementing"},
            "safe_next": "implementing",
        },
        "implementing": {
            "instructions": "实现代码让测试通过，不要做测试范围以外的重构",
            "allowed_tools": ["Read", "Edit", "Write"],
            "max_edit_lines": 30,
            "max_files_per_state": 3,
            "on": {"IMPLEMENTED": "testing"},
            "safe_next": "testing",
        },
        "testing": {
            "instructions": "运行测试，确保全部通过",
            "allowed_tools": ["Read", "Bash"],
            "allowed_commands": ["pytest", "cargo test", "npm test", "make test"],
            "on": {
                "PASS": {"target": "review", "guard": "all_tests_pass"},
                "FAIL": "implementing",
            },
        },
        "review": {
            "instructions": "审查代码，可做必要的重构",
            "allowed_tools": ["Read", "Edit", "Write"],
            "max_edit_lines": 15,
            "on": {"REFACTORED": "write_test"},
        },
        "completed": {"type": "final"},
    },
    "guards": {
        "all_tests_pass": {"field": "test_result", "op": "eq", "value": "pass"},
    },
}


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------
if __name__ == "__main__":
    import uuid
    sid = str(uuid.uuid4())
    tid = "test"

    # Activate bugfix workflow
    result = activate_workflow(sid, tid, WORKFLOW_BUGFIX)
    assert result["ok"], f"Failed to activate: {result}"
    print(f"✓ Activated workflow '{result['id']}' at state '{result['initial_state']}'")
    print(f"  allowed_tools: {result['allowed_tools']}")
    print(f"  instructions: {result['instructions']}")

    # Check initial state
    state = get_current_state(sid, tid)
    assert state == "planning", f"Expected planning, got {state}"
    print(f"✓ Current state: {state}")

    # Check restrictions
    cmds = get_allowed_commands(sid, tid)
    assert cmds is None, f"planning should have no commands, got {cmds}"
    tools = get_allowed_tools(sid, tid)
    assert tools == ["Read", "Grep", "Glob"], f"Got {tools}"
    print(f"✓ allowed_tools: {tools}")

    # Transition to implementing
    r = transition(sid, tid, "READY", {})
    assert r["ok"], f"Transition failed: {r}"
    assert r["new_state"] == "implementing"
    print(f"✓ Transition READY: planning → implementing")

    # Check command allowlist in implementing
    cmds = get_allowed_commands(sid, tid)
    assert cmds == ["patch", "sed -i"], f"Got {cmds}"
    max_lines = get_max_edit_lines(sid, tid)
    assert max_lines == 20
    print(f"✓ allowed_commands: {cmds}, max_edit_lines: {max_lines}")

    # Test edit tracking
    r = record_file_edit(sid, tid, "main.py", 5)
    assert r["ok"], f"edit recording failed: {r}"
    r = record_file_edit(sid, tid, "utils.py", 10)
    assert r["ok"], f"edit recording failed: {r}"
    print(f"✓ record_file_edit: 2 files, 15 lines")

    # Test max_files exceeded
    r = record_file_edit(sid, tid, "extra.py", 1)
    assert not r["ok"], "Should have been rejected"
    assert "max_files" in r["reason"].lower()
    print(f"✓ max_files_per_state enforced: {r['reason']}")

    # Test max_edit_lines exceeded
    r = record_file_edit(sid, tid, "main.py", 25)
    assert not r["ok"], "Should have been rejected"
    assert "max_edit_lines" in r["reason"].lower()
    print(f"✓ max_edit_lines enforced: {r['reason']}")

    # Transition to testing
    r = transition(sid, tid, "DONE", {})
    assert r["ok"], f"Transition failed: {r}"
    assert r["new_state"] == "testing"
    print(f"✓ Transition DONE: implementing → testing")

    # Test guard (test_result = pass)
    r = transition(sid, tid, "PASS", {"test_result": "pass"})
    assert r["ok"], f"Transition failed: {r}"
    assert r["new_state"] == "review"
    print(f"✓ Guard 'tests_passed' passed: testing → review")

    # Test guard failure (test_result = fail)
    r = transition(sid, tid, "PASS", {"test_result": "fail"})
    assert not r["ok"], "Should have failed guard"
    assert "Guard" in r["error"] or "failed" in r["error"].lower()
    print(f"✓ Guard 'tests_passed' blocked: {r['error']}")

    # Clear
    clear_workflow_session(sid, tid)
    print(f"✓ Session cleared")

    print(f"\nAll workflow tests passed!")
