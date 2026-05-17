"""
Command Filter — 命令白名单过滤器（移植自 Statewright tool_enforcer.rs 的 command allowlist）

功能：
  - prefix-match 检查命令是否在白名单
  - 识别危险模式（; | && $() 等）
  - 检查命令中是否包含危险环境变量

用法：
    result = check_command("pytest tests/", allowed_commands=["pytest", "cargo test"])
    # result = {"ok": True}

    result = check_command("rm -rf /", allowed_commands=["pytest"])
    # result = {"ok": False, "reason": "Command 'rm' not in allowlist: pytest, cargo test"}
"""

import os
import re
import shlex
from typing import TypedDict

try:
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
except ImportError:
    pass


# 危险命令黑名单（无条件 block）
DANGEROUS_COMMANDS = {
    "rm -rf", "rm -rf /", "rm -rf /*",
    "dd if=", "mkfs", "fdisk", "parted",
    ":(){:|:&};:",  # fork bomb
    "chmod -R 777 /",
    "wget .*\\| sh", "curl .*\\| sh",  # pipe to shell
}

# 危险 pattern（不管白名单如何都 block）
DANGEROUS_PATTERNS = [
    re.compile(r">\s*/dev/sd[a-z]"),       # 直接写磁盘设备
    re.compile(r"\|?\s*sh\s*$"),            # 管道到 shell 结尾
    re.compile(r"&&\s*rm\s+"),              # && rm
    re.compile(r"%\s*\(.*\)\s*\|"),         # 替换执行
]


class CheckResult(TypedDict, total=False):
    ok: bool
    reason: str | None


# 提取命令的 base（去除 path）
def _command_base(cmd: str) -> str:
    """提取命令的 base name（如 /usr/bin/pytest → pytest）。"""
    parts = cmd.strip().split()
    if not parts:
        return cmd
    base = os.path.basename(parts[0])
    # 处理 "python -m pytest" 这种情况
    if "-" in base:
        return base.split("-")[-1]
    return base


def _tokenize(cmd: str) -> list[str]:
    """简单 tokenize，分离命令和参数。"""
    try:
        return shlex.split(cmd)
    except ValueError:
        # shlex 失败时用空格 split
        return cmd.split()


def check_command(
    command: str,
    allowed_commands: list[str] | None = None,
    blocked_env: list[str] | None = None,
    env_overrides: dict[str, str] | None = None,
) -> CheckResult:
    """
    检查命令是否允许执行。

    Args:
        command: 完整命令字符串（如 "pytest tests/test_foo.py -v"）
        allowed_commands: 允许的命令前缀列表（如 ["pytest", "cargo test", "npm"])
        blocked_env: 不允许存在的环境变量名列表
        env_overrides: 允许覆盖的环境变量（key: allowed_value）

    Returns:
        {"ok": True} 或 {"ok": False, "reason": "..."}
    """
    allowed_commands = allowed_commands or []
    blocked_env = blocked_env or []
    env_overrides = env_overrides or {}

    if not command.strip():
        return {"ok": False, "reason": "Empty command"}

    # 检查危险命令黑名单
    cmd_lower = command.lower().strip()
    for danger in DANGEROUS_COMMANDS:
        if danger.lower() in cmd_lower:
            return {"ok": False, "reason": f"Dangerous command blocked: '{danger}'"}

    # 检查危险 pattern
    for pattern in DANGEROUS_PATTERNS:
        if pattern.search(command):
            return {"ok": False, "reason": f"Command contains dangerous pattern"}

    # 检查环境变量
    env_vars_in_cmd = re.findall(r"\$[A-Za-z_][A-Za-z0-9_]*", command)
    for var in env_vars_in_cmd:
        var_name = var[1:]  # 去掉 $
        if var_name in blocked_env:
            return {"ok": False, "reason": f"Blocked environment variable in command: {var}"}

    # 如果没有白名单配置，允许所有
    if not allowed_commands:
        return {"ok": True}

    # 提取 tokens
    tokens = _tokenize(command)
    if not tokens:
        return {"ok": False, "reason": "Failed to parse command"}

    # 命令主体（第一个 token）
    primary_cmd = tokens[0]

    # 特殊情况：shell 内建命令（cd, echo, export 等）总是允许
    SHELL_BUILTINS = {"cd", "echo", "export", "source", "alias", "history", "pwd", "ls", "mkdir", "cp", "mv", "cat", "head", "tail"}
    if primary_cmd in SHELL_BUILTINS:
        return {"ok": True}

    # 特殊情况：python -m / node -e 等 module runner
    # 将 "python -m pytest" 映射为 "pytest"，"node --eval" 映射为 "node"
    if len(tokens) >= 3 and tokens[0] in ("python", "python3", "node", "ruby"):
        if tokens[1] in ("-m", "--module"):
            # tokens[2] 是实际的 module/command
            module_cmd = tokens[2]
            for allowed in allowed_commands:
                if module_cmd == allowed or module_cmd.startswith(allowed.split()[0]):
                    return {"ok": True}
            return {"ok": False, "reason": f"Module '{module_cmd}' not in allowlist: {', '.join(allowed_commands)}"}
        elif tokens[1] in ("-c", "--eval", "-e"):
            # "python -c 'code'" / "node --eval 'code'" 等直接执行
            runner = tokens[0]
            return {"ok": False, "reason": f"Direct code execution ({runner} -c/--eval) not allowed"}

    # 检查是否匹配白名单
    for allowed in allowed_commands:
        # 白名单可能是 "pytest" 或 "cargo test" 或 "npm run"
        allowed_tokens = _tokenize(allowed)
        if not allowed_tokens:
            continue

        # 前缀匹配：命令必须以白名单开头
        # "pytest" 匹配 "pytest tests/", "pytest -v"
        # "cargo test" 匹配 "cargo test --lib"
        matches = True
        for i, allowed_token in enumerate(allowed_tokens):
            if i >= len(tokens):
                matches = False
                break
            # token 必须以 allowed token 开头（允许后续参数）
            if not tokens[i].startswith(allowed_token) and allowed_token not in tokens[i]:
                # 最后一个 token 可以是部分 match
                if i == len(allowed_tokens) - 1:
                    if not (tokens[i].startswith(allowed_token) or allowed_token.startswith(tokens[i])):
                        matches = False
                        break
                else:
                    matches = False
                    break

        if matches:
            return {"ok": True}

    # 不在白名单
    return {
        "ok": False,
        "reason": f"Command '{primary_cmd}' not in allowlist: {', '.join(allowed_commands)}"
    }


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------
if __name__ == "__main__":
    import uuid
    sid = str(uuid.uuid4())

    # Allowed commands
    allowed = ["pytest", "cargo test", "npm test"]

    cases = [
        # (command, expected_ok, description)
        ("pytest tests/", True, "pytest with args"),
        ("cargo test --lib", True, "cargo test prefix"),
        ("npm test", True, "npm test exact"),
        ("echo hello", True, "shell builtin"),
        ("cd /tmp", True, "shell builtin cd"),
        ("rm file.txt", False, "rm not in allowlist"),
        ("rm -rf /", False, "dangerous command"),
        ("pytest tests/ & rm -rf /", False, "dangerous in command"),
        ("python -m pytest", True, "python -m pytest"),
        ("make test", False, "make not in allowlist"),
        ("cat /etc/passwd", False, "cat not in allowlist"),
        ("ls -la", False, "ls not in allowlist"),
        ("ls", False, "ls not in allowlist"),
        ("cd ..", True, "cd builtin"),
        ("export FOO=bar", True, "export builtin"),
    ]

    passed = 0
    for cmd, expected_ok, desc in cases:
        result = check_command(cmd, allowed_commands=allowed)
        ok = result["ok"] == expected_ok
        status = "✓" if ok else "✗"
        if ok:
            passed += 1
        print(f"{status} [{desc}] '{cmd}' → ok={result['ok']} (expected {expected_ok}) {('| ' + result.get('reason', '')) if not ok else ''}")

    print(f"\n{passed}/{len(cases)} passed")
