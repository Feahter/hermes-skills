"""
Stage detection — determines the current operational stage from message content
and conversation history.

Detection strategy:
  1. Check user message for stage keywords (highest priority)
  2. Check last assistant message for stage signals
  3. Default to CHAT (no restriction) if ambiguous
"""

import re
try:
    from .whitelist_config import STAGE_WHITELISTS
except ImportError:
    from whitelist_config import STAGE_WHITELISTS  # standalone test


def detect_stage(
    user_message: str,
    conversation_history: list,
    current_stage: str | None = None,
) -> str:
    """
    Detect the current stage from user message and conversation context.

    Args:
        user_message: Current user input
        conversation_history: List of prior messages dicts with "role" and "content"
        current_stage: Previously detected stage (for sticky detection)

    Returns:
        Stage name string (STAGE_WHITELISTS key), default "CHAT"
    """
    msg_lower = (user_message or "").lower()

    # 1. Check for explicit stage keywords in user message
    for stage_name, config in STAGE_WHITELISTS.items():
        if stage_name == "CHAT":
            continue
        for kw in config["keywords"]:
            if kw.lower() in msg_lower:
                return stage_name

    # 2. Check conversation history for stage signals (last 3 messages)
    # This handles cases where the model is mid-task and the user says "ok continue"
    if current_stage and current_stage != "CHAT":
        # Stage is sticky — stay in current stage unless explicitly switched
        # Short continuation messages don't reset the stage
        continuation_patterns = [
            r"^ok(?:ay)?[.,]?$", r"^继续$", r"^go on$", r"^yes[,.]?$",
            r"^继续吧$", r"^是的$", r"^对$", r"^好的$",
        ]
        msg_stripped = msg_lower.strip()
        for pattern in continuation_patterns:
            if re.match(pattern, msg_stripped):
                return current_stage

    # 3. Check if any recent assistant message ended with a stage indicator
    # e.g., "[Stage: CODE]" in assistant message
    stage_indicator_pattern = re.compile(r"\[Stage:\s*(\w+)\]")
    history_to_check = conversation_history[-4:] if conversation_history else []
    for msg in reversed(history_to_check):
        content = msg.get("content", "") if isinstance(msg, dict) else str(msg)
        match = stage_indicator_pattern.search(content)
        if match:
            inferred = match.group(1).upper()
            if inferred in STAGE_WHITELISTS:
                return inferred

    return "CHAT"


def get_stage_tools(stage: str) -> list[str]:
    """Return the full tool list for a given stage (global + stage-specific)."""
    try:
        from .whitelist_config import GLOBAL_TOOLS
    except ImportError:
        from whitelist_config import GLOBAL_TOOLS  # type: ignore

    if stage == "CHAT":
        return []  # no restriction

    stage_config = STAGE_WHITELISTS.get(stage, STAGE_WHITELISTS["CHAT"])
    stage_tools = stage_config["tools"]

    # Global tools are always available
    return list(stage_tools) + GLOBAL_TOOLS
