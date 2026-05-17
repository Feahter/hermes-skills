"""
pre_llm_call hook for stage-tool-whitelist (增强版 with StateWright).

Injects stage context + StateWright guardrails into the model prompt.
Returns {"context": str, "tools": list[str]]} to restrict tools.

State is shared with post_tool_call via module-level session state.
"""

import threading
import time
import os

try:
    from .whitelist_config import STAGE_WHITELISTS, get_stage_allowed_commands, get_stage_max_edit_lines, get_stage_max_files, get_stage_blocked_env
    from .stage_machine import detect_stage, get_stage_tools
    from .workflow import (
        activate_workflow, get_current_state, get_state_def,
        get_allowed_commands as get_workflow_allowed_commands,
        get_allowed_tools as get_workflow_allowed_tools,
        get_state_instructions, transition as workflow_transition,
        reset_edit_tracking, WORKFLOW_BUGFIX, WORKFLOW_TDD,
        clear_workflow_session,
    )
except ImportError:
    from whitelist_config import STAGE_WHITELISTS, get_stage_allowed_commands, get_stage_max_edit_lines, get_stage_max_files, get_stage_blocked_env  # type: ignore
    from stage_machine import detect_stage, get_stage_tools  # type: ignore
    from workflow import (
        activate_workflow, get_current_state, get_state_def,
        get_allowed_commands as get_workflow_allowed_commands,
        get_allowed_tools as get_workflow_allowed_tools,
        get_state_instructions, transition as workflow_transition,
        reset_edit_tracking, WORKFLOW_BUGFIX, WORKFLOW_TDD,
        clear_workflow_session,
    )


# ---------------------------------------------------------------------------
# Session state (thread-safe, session-scoped)
# ---------------------------------------------------------------------------
_state_lock = threading.Lock()
_session_state: dict[str, dict] = {}


def _get_key(session_id: str, task_id: str) -> str:
    return session_id or task_id or "default"


def _get_or_create(session_id: str, task_id: str) -> dict:
    key = _get_key(session_id, task_id)
    with _state_lock:
        return _session_state.setdefault(key, {
            "stage": "CHAT",
            "stage_updated_at": 0.0,
            "pending_warning": None,
            "workflow_active": False,
        })


def _set_stage(session_id: str, task_id: str, stage: str) -> None:
    key = _get_key(session_id, task_id)
    with _state_lock:
        s = _session_state.setdefault(key, {})
        s["stage"] = stage
        s["stage_updated_at"] = time.monotonic()


def _set_warning(session_id: str, task_id: str, tool_name: str, allowed: list[str], extra: str = "") -> None:
    key = _get_key(session_id, task_id)
    msg = (
        f"[边界警告] 你刚才调用了 `{tool_name}`，但当前阶段不允许使用此工具。\n"
        f"允许的工具: {', '.join(allowed)}\n"
        f"请只使用上述列表中的工具，不要越界调用。{extra}"
    )
    with _state_lock:
        _session_state.setdefault(key, {})["pending_warning"] = msg


def _get_and_clear_warning(session_id: str, task_id: str) -> str | None:
    key = _get_key(session_id, task_id)
    with _state_lock:
        entry = _session_state.get(key, {})
        return entry.pop("pending_warning", None)


def _clear_session(session_id: str, task_id: str) -> None:
    key = _get_key(session_id, task_id)
    with _state_lock:
        _session_state.pop(key, None)
    clear_workflow_session(session_id, task_id)


# ---------------------------------------------------------------------------
# StateWright helpers
# ---------------------------------------------------------------------------

def _build_workflow_context(session_id: str, task_id: str, stage: str) -> str | None:
    """Build StateWright workflow context string for injection."""
    # Try workflow first (higher priority than stage config)
    wf_state = get_current_state(session_id, task_id)
    if wf_state:
        instructions = get_state_instructions(session_id, task_id)
        wf_tools = get_workflow_allowed_tools(session_id, task_id)
        wf_cmds = get_workflow_allowed_commands(session_id, task_id)
        state_def = get_state_def(session_id, task_id)
        max_lines = state_def.get("max_edit_lines") if state_def else None
        max_files = state_def.get("max_files_per_state") if state_def else None

        parts = [
            f"[Workflow State: {wf_state}]",
            f"State instructions: {instructions or '(none)'}",
        ]
        if wf_tools:
            parts.append(f"Allowed tools: {', '.join(wf_tools)}")
        if wf_cmds:
            parts.append(f"Allowed commands: {', '.join(wf_cmds)}")
        if max_lines is not None:
            parts.append(f"Max edit lines per edit: {max_lines}")
        if max_files is not None:
            parts.append(f"Max files in this state: {max_files}")
        return "\n".join(parts)

    # Fall back to stage config
    allowed_cmds = get_stage_allowed_commands(stage)
    max_lines = get_stage_max_edit_lines(stage)
    max_files = get_stage_max_files(stage)
    blocked_env = get_stage_blocked_env(stage)

    parts = [f"[Stage: {stage}]"]
    if allowed_cmds is not None:
        if allowed_cmds:
            parts.append(f"Allowed shell commands: {', '.join(allowed_cmds)}")
        else:
            parts.append("Shell commands: BLOCKED in this stage")
    if max_lines is not None and max_lines == 0:
        parts.append("File editing: BLOCKED in this stage")
    elif max_lines:
        parts.append(f"Max edit lines per operation: {max_lines}")
    if max_files is not None and max_files == 0:
        parts.append("New file creation: BLOCKED in this stage")
    elif max_files:
        parts.append(f"Max files in this stage: {max_files}")
    if blocked_env:
        parts.append(f"Blocked environment variables: {', '.join(blocked_env)}")

    return "\n".join(parts)


def _check_workflow_transition(user_message: str) -> tuple[str, dict] | None:
    """
    检测用户是否在请求 workflow transition。

    Returns:
        (event, event_data) if transition detected, else None
    """
    msg_lower = user_message.lower().strip()

    # Transition event mapping
    TRANSITION_MAP = {
        ("准备好了", "ready", "开始实现", "开始", "implement"): "READY",
        ("完成了", "done", "实现完成", "写完了"): "DONE",
        ("测试通过", "pass", "测试成功", "测试 ok"): "PASS",
        ("测试失败", "fail", "测试没通过", "测试挂了"): "FAIL",
        ("审查通过", "approve", "可以了", "approved"): "APPROVE",
    }

    for patterns, event in TRANSITION_MAP.items():
        for pattern in patterns:
            if pattern in msg_lower:
                return event, {}
    return None


# ---------------------------------------------------------------------------
# Hook implementations
# ---------------------------------------------------------------------------

def pre_llm_call(
    session_id: str = "",
    task_id: str = "",
    user_message: str = "",
    conversation_history: list | None = None,
    is_first_turn: bool = False,
    **kwargs,
) -> None | dict | str:
    """
    Detect stage, inject StateWright context, return tool whitelist.

    Returns:
        {"context": str, "tools": list[str]]} to restrict tools
        {"context": str} (no tools) for CHAT stage
        None — leave tools unrestricted
    """
    history = conversation_history or []
    state = _get_or_create(session_id, task_id)

    # Check for workflow transition requests first
    transition_info = _check_workflow_transition(user_message)
    if transition_info and state.get("workflow_active"):
        event, event_data = transition_info
        result = workflow_transition(session_id, task_id, event, event_data)
        if result["ok"]:
            reset_edit_tracking(session_id, task_id)

    # Detect stage (with sticky behavior)
    new_stage = detect_stage(
        user_message,
        history,
        current_stage=state["stage"] if not is_first_turn else None,
    )

    # Update stage if changed
    if new_stage != state["stage"]:
        _set_stage(session_id, task_id, new_stage)
        # Reset edit tracking on stage change
        reset_edit_tracking(session_id, task_id)

    # Check for pending warning
    warning = _get_and_clear_warning(session_id, task_id)

    if new_stage == "CHAT":
        if warning:
            return {"context": warning, "tools": []}
        return {"context": warning} if warning else None

    # Build allowed tools list
    allowed_tools = get_stage_tools(new_stage)
    stage_desc = STAGE_WHITELISTS[new_stage]["description"]

    # Build StateWright context
    workflow_context = _build_workflow_context(session_id, task_id, new_stage)

    context_parts = []
    if warning:
        context_parts.append(warning)
    context_parts.append(f"[Stage: {new_stage}] {stage_desc}")
    context_parts.append(f"可用工具: {', '.join(allowed_tools)}")
    context_parts.append("只使用上述列表中的工具，不要调用列表以外的工具。")
    if workflow_context:
        context_parts.append("")
        context_parts.append(workflow_context)

    return {
        "context": "\n\n".join(context_parts),
        "tools": allowed_tools,
    }


def on_session_reset(session_id: str = "", task_id: str = "", **kwargs) -> None:
    """Clear session state on reset."""
    _clear_session(session_id, task_id)


# ---------------------------------------------------------------------------
# Workflow activation command (called by user or skill system)
# ---------------------------------------------------------------------------

def activate_bugfix_workflow(session_id: str, task_id: str) -> dict:
    """Activate the built-in bugfix workflow."""
    result = activate_workflow(session_id, task_id, WORKFLOW_BUGFIX)
    if result["ok"]:
        key = _get_key(session_id, task_id)
        with _state_lock:
            _session_state[key]["workflow_active"] = True
    return result


def activate_tdd_workflow(session_id: str, task_id: str) -> dict:
    """Activate the built-in TDD workflow."""
    result = activate_workflow(session_id, task_id, WORKFLOW_TDD)
    if result["ok"]:
        key = _get_key(session_id, task_id)
        with _state_lock:
            _session_state[key]["workflow_active"] = True
    return result


def deactivate_workflow(session_id: str, task_id: str) -> None:
    """Deactivate workflow and return to normal stage-based mode."""
    clear_workflow_session(session_id, task_id)
    key = _get_key(session_id, task_id)
    with _state_lock:
        if key in _session_state:
            _session_state[key]["workflow_active"] = False
