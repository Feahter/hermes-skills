"""
post_tool_call hook for context-pollution-defender.

Tracks tool-call volume per session and injects context-health reminders
via pre_llm_call when thresholds are crossed.

Thresholds (per session, reset on /new):
  警告  — 16 tool_calls  (≈ iteration 8 at 2 tool-calls/turn)
  警戒  — 32 tool_calls  (≈ iteration 15)
  应急  — 56 tool_calls  (≈ iteration 25)
"""

import threading
import time

# Thread-safe session counter: {(session_id,): {"count": N, "last_reset": timestamp}}
_counter_lock = threading.Lock()
_session_counters: dict[str, dict] = {}


def _get_session_key(session_id: str, task_id: str) -> str:
    """Bucket by session_id primarily; task_id for CLI context."""
    return session_id or task_id or "default"


def _get_counter(session_id: str, task_id: str) -> int:
    key = _get_session_key(session_id, task_id)
    with _counter_lock:
        return _session_counters.get(key, {}).get("count", 0)


def _increment(session_id: str, task_id: str) -> int:
    key = _get_session_key(session_id, task_id)
    with _counter_lock:
        entry = _session_counters.setdefault(key, {"count": 0, "last_reset": time.monotonic()})
        entry["count"] += 1
        return entry["count"]


def _reset_session(session_id: str, task_id: str) -> None:
    key = _get_session_key(session_id, task_id)
    with _counter_lock:
        _session_counters.pop(key, None)


def post_tool_call(tool_name: str, args: dict, result: str, task_id: str = "",
                   session_id: str = "", tool_call_id: str = "",
                   duration_ms: int = 0, **kwargs) -> None:
    """
    Track tool-call volume.  When thresholds are crossed, inject a reminder
    via pre_llm_call so the next LLM turn sees it.

    Thresholds:
        16 → inject 精简模式 reminder
        32 → inject 极简模式 reminder
        56 → inject 应急模式 reminder
    """
    count = _increment(session_id, task_id)

    if count == 16:
        _inject_reminder(session_id, task_id, "精简模式：减少解释，结论先行，每步验证")
    elif count == 32:
        _inject_reminder(session_id, task_id, "极简模式：只做当前最小动作，不扩展，不预想")
    elif count == 56:
        _inject_reminder(session_id, task_id, "应急模式：立即停止，发起上下文重置")


def _inject_reminder(session_id: str, task_id: str, message: str) -> None:
    """Queue a reminder to be injected at the next pre_llm_call."""
    key = _get_session_key(session_id, task_id)
    with _counter_lock:
        entry = _session_counters.setdefault(key, {})
        entry["pending_reminder"] = message


def pre_llm_call(messages: list, session_id: str = "", task_id: str = "",
                 **kwargs) -> None | dict | str:
    """
    Check for a pending reminder and inject it into the user message.

    Returns context dict (injected into user message) or None/empty.
    """
    key = _get_session_key(session_id, task_id)
    with _counter_lock:
        entry = _session_counters.get(key, {})
        reminder = entry.pop("pending_reminder", None)

    if reminder:
        return {
            "context": (
                f"[上下文污染预警] {reminder}\n"
                f"请立即调整工作模式，严格遵循上述指令。"
            )
        }
    return None


def on_session_reset(session_id: str = "", task_id: str = "", **kwargs) -> None:
    """Clear counter state for the resetting session."""
    _reset_session(session_id, task_id)
