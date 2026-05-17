"""
Edit Enforcer — 编辑范围强制执行器（移植自 Statewright 的 edit guards）

功能：
  - 检查 edit 行数是否超过 max_edit_lines
  - 检查单次 edit 是否涉及过多文件
  - 返回错误信息（不实际 block，block 由调用方决定）

用法：
    result = check_edit(
        file_path="src/main.py",
        old_string="def foo():",
        new_string="def bar():",
        max_edit_lines=20,
    )
    # result = {"ok": True, "lines_changed": 3}

    result = check_edit(
        file_path="src/main.py",
        old_string="",
        new_string="x" * 1000,
        max_edit_lines=20,
    )
    # result = {"ok": False, "reason": "Edit changes 1000 lines (limit: 20)"}
"""

import re
from typing import TypedDict

try:
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
except ImportError:
    pass


# 危险 Pattern（在 old 或 new 里检测到会无条件 block）
DANGEROUS_PATTERNS = [
    (re.compile(r"chmod\s+-R\s+777"), "Recursive chmod 777 detected"),
    (re.compile(r"chmod\s+777"), "Dangerous chmod 777 detected"),
    (re.compile(r"sudo\s+rm"), "sudo rm detected"),
    (re.compile(r">\s*/etc/passwd"), "Writing to /etc/passwd detected"),
    (re.compile(r"eval\s*\("), "eval() detected"),
    (re.compile(r"exec\s*\("), "exec() detected"),
    (re.compile(r"__import__\s*\("), "__import__() detected"),
]


class EditCheckResult(TypedDict, total=False):
    ok: bool
    lines_changed: int | None
    reason: str | None


def count_newlines(s: str) -> int:
    """计算字符串里的换行符数量（近似行数）。"""
    if not s:
        return 0
    return s.count("\n") + (1 if not s.endswith("\n") else 0)


def check_edit(
    file_path: str,
    old_string: str,
    new_string: str,
    max_edit_lines: int | None = None,
    max_files_per_state: int | None = None,
    already_edited_files: list[str] | None = None,
) -> EditCheckResult:
    """
    检查一次编辑是否符合约束。

    Args:
        file_path: 目标文件路径
        old_string: 旧内容（被替换的部分）
        new_string: 新内容（替换后的内容）
        max_edit_lines: 单次 edit 最大行数
        max_files_per_state: 单个状态最大文件数
        already_edited_files: 该状态已编辑过的文件列表

    Returns:
        EditCheckResult
    """
    already_edited_files = already_edited_files or []

    # 危险 pattern 检查（无论约束如何都 block）
    combined = old_string + new_string
    for pattern, message in DANGEROUS_PATTERNS:
        if pattern.search(combined):
            return {"ok": False, "reason": f"Dangerous pattern detected: {message}"}

    # 行数计算
    lines_changed = count_newlines(new_string) - count_newlines(old_string)
    # 绝对值，因为删减也是变化
    abs_lines = abs(lines_changed)

    # max_edit_lines 检查
    if max_edit_lines is not None and abs_lines > max_edit_lines:
        return {
            "ok": False,
            "reason": f"Edit changes {abs_lines} lines (limit: {max_edit_lines})",
        }

    # max_files_per_state 检查（新文件）
    if max_files_per_state is not None and file_path not in already_edited_files:
        if len(set(already_edited_files)) >= max_files_per_state:
            return {
                "ok": False,
                "reason": f"max_files_per_state reached ({max_files_per_state} files max in this state)",
            }

    return {"ok": True, "lines_changed": abs_lines}


def parse_patch_diff(patch: str) -> list[tuple[str, str, str]]:
    """
    解析 unified diff 格式，返回 [(file_path, old_lines, new_lines)]。

    这用于从 model 生成的 diff 里提取文件信息。
    """
    files = []
    current_file = None
    current_old = []
    current_new = []

    for line in patch.splitlines():
        if line.startswith("--- ") or line.startswith("+++ "):
            # 新文件开始，保存之前的
            if current_file is not None:
                files.append((current_file, "\n".join(current_old), "\n".join(current_new)))
            # 解析文件名
            parts = line.split("\t", 1)
            filename = parts[0][4:].strip()
            if filename == "/dev/null":
                filename = parts[1].strip() if len(parts) > 1 else "unknown"
            current_file = filename
            current_old = []
            current_new = []
        elif line.startswith("@@"):
            # diff hunk 开始，忽略细节
            pass
        elif line.startswith("-") and not line.startswith("---"):
            current_old.append(line[1:])
        elif line.startswith("+") and not line.startswith("+++"):
            current_new.append(line[1:])
        elif current_file is not None:
            # 上下文行
            current_old.append(line)
            current_new.append(line)

    if current_file is not None:
        files.append((current_file, "\n".join(current_old), "\n".join(current_new)))

    return files


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------
if __name__ == "__main__":
    cases = [
        # Normal edits
        {
            "file_path": "main.py",
            "old_string": "def foo():\n    pass",
            "new_string": "def bar():\n    return 1",
            "max_edit_lines": 20,
            "expected_ok": True,
        },
        # Within limit
        {
            "file_path": "main.py",
            "old_string": "x = 1",
            "new_string": "x = 2",
            "max_edit_lines": 5,
            "expected_ok": True,
        },
        # Over limit
        {
            "file_path": "main.py",
            "old_string": "",
            "new_string": "\n".join([f"line {i}" for i in range(50)]),
            "max_edit_lines": 20,
            "expected_ok": False,
        },
        # New file in state
        {
            "file_path": "new.py",
            "old_string": "",
            "new_string": "print('hello')",
            "max_files_per_state": 3,
            "already_edited_files": ["a.py", "b.py", "c.py"],
            "expected_ok": False,
        },
        # Existing file in state (doesn't count against max_files)
        {
            "file_path": "a.py",
            "old_string": "x = 1",
            "new_string": "x = 2",
            "max_files_per_state": 3,
            "already_edited_files": ["a.py", "b.py"],
            "expected_ok": True,
        },
        # Dangerous pattern: eval
        {
            "file_path": "main.py",
            "old_string": "",
            "new_string": "eval(input())",
            "max_edit_lines": 100,
            "expected_ok": False,
        },
        # Dangerous pattern: chmod 777
        {
            "file_path": "setup.sh",
            "old_string": "",
            "new_string": "chmod 777 /tmp",
            "max_edit_lines": 100,
            "expected_ok": False,
        },
    ]

    passed = 0
    for case in cases:
        result = check_edit(
            file_path=case["file_path"],
            old_string=case.get("old_string", ""),
            new_string=case.get("new_string", ""),
            max_edit_lines=case.get("max_edit_lines"),
            max_files_per_state=case.get("max_files_per_state"),
            already_edited_files=case.get("already_edited_files"),
        )
        ok = result["ok"] == case["expected_ok"]
        status = "✓" if ok else "✗"
        if ok:
            passed += 1
        reason = f" | {result.get('reason', '')}" if not result["ok"] else ""
        print(f"{status} {case['file_path']}: ok={result['ok']} (expected {case['expected_ok']}){reason}")

    print(f"\n{passed}/{len(cases)} passed")
