"""
post_tool_call hook for stage-tool-whitelist (增强版 with StateWright).

功能：
  1. 检查工具是否在当前 stage/workflow 白名单
  2. terminal 命令检查 allowed_commands
  3. patch/edit 操作检查 max_edit_lines / max_files_per_state
  4. 队列警告到下一次 pre_llm_call

注意：这是"检测层"，不能真正 block（post-hook 无否决权）。
真正的 block 需要 core 改动（RFC Phase 3）。
"""

try:
    from .pre_llm_call import _set_warning, _get_or_create
    from .stage_machine import get_stage_tools
    from .whitelist_config import (
        get_stage_allowed_commands, get_stage_max_edit_lines,
        get_stage_max_files, get_stage_blocked_env,
    )
    from .workflow import (
        get_current_state, get_state_def,
        get_allowed_commands as get_wf_allowed_commands,
        get_allowed_tools as get_wf_allowed_tools,
        get_max_edit_lines as get_wf_max_edit_lines,
        get_max_files_per_state as get_wf_max_files,
        record_file_edit,
    )
    from .command_filter import check_command
    from .edit_enforcer import check_edit
except ImportError:
    from pre_llm_call import _set_warning, _get_or_create  # type: ignore
    from stage_machine import get_stage_tools  # type: ignore
    from whitelist_config import (  # type: ignore
        get_stage_allowed_commands, get_stage_max_edit_lines,
        get_stage_max_files, get_stage_blocked_env,
    )
    from workflow import (  # type: ignore
        get_current_state, get_state_def,
        get_allowed_commands as get_wf_allowed_commands,
        get_allowed_tools as get_wf_allowed_tools,
        get_max_edit_lines as get_wf_max_edit_lines,
        get_max_files_per_state as get_wf_max_files,
        record_file_edit,
    )
    from command_filter import check_command  # type: ignore
    from edit_enforcer import check_edit  # type: ignore


def _get_enforcement_context(session_id: str, task_id: str) -> dict:
    """
    获取当前执行上下文（workflow 或 stage 配置）。

    Returns:
        dict with keys: allowed_tools, allowed_commands, max_edit_lines, max_files, blocked_env, is_workflow
    """
    # 优先用 workflow 配置
    wf_state = get_current_state(session_id, task_id)
    if wf_state:
        state_def = get_state_def(session_id, task_id)
        return {
            "is_workflow": True,
            "allowed_tools": get_wf_allowed_tools(session_id, task_id),
            "allowed_commands": get_wf_allowed_commands(session_id, task_id),
            "max_edit_lines": get_wf_max_edit_lines(session_id, task_id),
            "max_files": get_wf_max_files(session_id, task_id),
            "blocked_env": state_def.get("blocked_env") if state_def else None,
        }

    # 回退到 stage 配置
    state = _get_or_create(session_id, task_id)
    stage = state.get("stage", "CHAT")
    return {
        "is_workflow": False,
        "allowed_tools": get_stage_tools(stage),
        "allowed_commands": get_stage_allowed_commands(stage),
        "max_edit_lines": get_stage_max_edit_lines(stage),
        "max_files": get_stage_max_files(stage),
        "blocked_env": get_stage_blocked_env(stage),
    }


def _queue_violation_warning(
    session_id: str,
    task_id: str,
    tool_name: str,
    allowed: list,
    extra: str = "",
) -> None:
    """Queue a violation warning for next pre_llm_call."""
    _set_warning(session_id, task_id, tool_name, allowed, extra)


def post_tool_call(
    tool_name: str,
    args: dict,
    result: str,
    task_id: str = "",
    session_id: str = "",
    tool_call_id: str = "",
    duration_ms: int = 0,
    **kwargs,
) -> None:
    """
    Check tool call against current stage/workflow restrictions.

    检测内容：
      - 工具名是否在白名单
      - terminal 命令是否在 allowed_commands
      - patch/edit 是否超过 max_edit_lines
      - 是否创建新文件超过 max_files_per_state
    """
    ctx = _get_enforcement_context(session_id, task_id)
    current_stage = ctx.get("is_workflow") and "workflow" or "stage"

    # 1. Tool name whitelist check
    if tool_name not in ["terminal", "patch", "write_file"]:
        # 对于非关键工具，只做 tool_name 白名检查
        if tool_name not in ctx.get("allowed_tools", []) and ctx.get("allowed_tools"):
            allowed = ctx["allowed_tools"]
            _queue_violation_warning(
                session_id, task_id, tool_name, allowed,
                f"(via {current_stage} whitelist)"
            )
        return

    # 2. Terminal command check
    if tool_name == "terminal":
        command = args.get("command", "")
        allowed_cmds = ctx.get("allowed_commands")

        if allowed_cmds is not None:
            # 0 或空列表 = 禁止所有命令
            if not allowed_cmds:
                _queue_violation_warning(
                    session_id, task_id, "terminal",
                    ["<none>"],
                    f"Shell commands are BLOCKED in this {current_stage}."
                )
                return

            check = check_command(
                command,
                allowed_commands=allowed_cmds,
                blocked_env=ctx.get("blocked_env"),
            )
            if not check["ok"]:
                _queue_violation_warning(
                    session_id, task_id, f"terminal: {command[:50]}",
                    allowed_cmds,
                    check.get("reason", ""),
                )
                return

    # 3. patch / write_file edit check
    if tool_name in ("patch", "write_file"):
        # 从 args 提取文件路径和内容
        file_path = args.get("path", "") or args.get("file_path", "")
        new_content = args.get("new_string", "") or args.get("content", "")
        old_content = args.get("old_string", "")

        # 如果是 write_file（创建文件），old_string 为空
        is_new_file = tool_name == "write_file"

        max_lines = ctx.get("max_edit_lines")
        max_files = ctx.get("max_files")

        # 0 = 禁止编辑
        if max_lines is not None and max_lines == 0:
            _queue_violation_warning(
                session_id, task_id, tool_name,
                ["<none>"],
                f"File editing is BLOCKED in this {current_stage}."
            )
            return

        # 检查 edit 行数
        if max_lines is not None and new_content:
            lines_changed = new_content.count("\n")
            if is_new_file:
                # 新文件的"行数"就是内容的行数
                lines_changed = lines_changed + (1 if new_content else 0)
            if lines_changed > max_lines:
                _queue_violation_warning(
                    session_id, task_id, f"{tool_name} on {file_path}",
                    [f"max {max_lines} lines"],
                    f"Edit changes {lines_changed} lines (limit: {max_lines})"
                )
                return

        # 记录文件编辑（用于 max_files_per_state）
        if is_new_file or tool_name == "patch":
            # 获取当前状态已编辑的文件列表
            from .workflow import _get_or_create_workflow
            wf_key = session_id or task_id or "default"
            try:
                wf = _get_or_create_workflow(wf_key, "")
                already_edited = list(wf.get("files_edited", [])) if wf else []
            except Exception:
                already_edited = []

            if max_files is not None and max_files > 0:
                # 新文件才检查
                if is_new_file and file_path not in already_edited:
                    if len(set(already_edited)) >= max_files:
                        _queue_violation_warning(
                            session_id, task_id, f"write_file: {file_path}",
                            [f"max {max_files} files"],
                            f"max_files_per_state reached ({max_files} files max in this {current_stage})"
                        )
                        return

            # 记录编辑
            if file_path and new_content:
                try:
                    record_file_edit(
                        session_id or task_id or "default",
                        "",
                        file_path,
                        lines_changed if 'lines_changed' in dir() else new_content.count("\n")
                    )
                except Exception:
                    pass  # 非关键错误，不 block
