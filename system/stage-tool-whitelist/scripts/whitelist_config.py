"""
Per-stage tool whitelist configuration.
Defines which tools are available in each operational stage.

Stages:
  PLAN   — understanding, decomposition, strategy
  SEARCH — information gathering, research
  CODE   — writing, editing, building
  REVIEW — verification, testing, critique
  WRITE  — documentation, content creation
  CHAT   — general conversation (no restriction)
"""

from typing import TypedDict

class StageConfig(TypedDict):
    keywords: list[str]
    tools: list[str]
    description: str


STAGE_WHITELISTS: dict[str, StageConfig] = {
    "PLAN": {
        "keywords": ["计划", "方案", "分析", "拆解", "怎么做", "如何开始", "plan", "analyze", "decompose", "strategy", "架构"],
        "tools": [
            "search_files", "read_file", "plan", "clarify", "todo",
            "web_search", "web_extract", "delegate_task",
        ],
        "description": "Planning and decomposition — only thinking/understanding tools",
        # StateWright extensions
        "allowed_commands": None,          # PLAN 阶段不允许执行命令
        "max_edit_lines": 0,              # PLAN 阶段不允许编辑
        "max_files_per_state": 0,         # PLAN 阶段不允许写文件
        "blocked_env": None,             # 无环境变量限制
    },
    "SEARCH": {
        "keywords": ["搜索", "查找", "查询", "研究", "调研", "search", "research", "find", "look up", "look for"],
        "tools": [
            "web_search", "web_extract", "search_files", "read_file",
            "browser_navigate", "jina_reader",
        ],
        "description": "Information gathering — only search and read tools",
        # StateWright extensions
        "allowed_commands": None,
        "max_edit_lines": 0,
        "max_files_per_state": 0,
        "blocked_env": None,
    },
    "CODE": {
        "keywords": ["写", "代码", "实现", "开发", "build", "code", "implement", "write code", "create function", "写一个", "帮我写", "开发", "debug", "fix bug"],
        "tools": [
            "read_file", "write_file", "patch", "terminal",
            "search_files", "execute_code", "python_debugpy",
            "delegate_task", "browser_navigate",
        ],
        "description": "Code writing — file operations and execution",
        # StateWright extensions
        "allowed_commands": ["patch", "sed -i", "git diff", "git status"],  # 允许的命令
        "max_edit_lines": 50,              # 单次 edit 最多 50 行
        "max_files_per_state": 5,          # 单个状态最多改 5 个文件
        "blocked_env": ["CI=true"],        # 禁止 CI 环境变量
    },
    "REVIEW": {
        "keywords": ["测试", "验证", "检查", "review", "test", "verify", "audit", "review", "check"],
        "tools": [
            "read_file", "terminal", "search_files", "execute_code",
            "browser_navigate",
        ],
        "description": "Verification and testing — execution and inspection tools",
        # StateWright extensions
        "allowed_commands": ["pytest", "cargo test", "npm test", "make test", "python -m pytest"],
        "max_edit_lines": 20,
        "max_files_per_state": 2,
        "blocked_env": None,
    },
    "WRITE": {
        "keywords": ["写文档", "写文章", "文档", "报告", "总结", "write doc", "documentation", "write report", "summarize"],
        "tools": [
            "read_file", "write_file", "patch", "browser_navigate",
            "search_files",
        ],
        "description": "Documentation and content — read/write tools",
        # StateWright extensions
        "allowed_commands": None,
        "max_edit_lines": 100,             # 文档可以多写点
        "max_files_per_state": 3,
        "blocked_env": None,
    },
    "CHAT": {
        "keywords": [],
        "tools": [],  # empty = no restriction
        "description": "General conversation — no tool restrictions",
        # StateWright extensions — CHAT 阶段完全无限制
        "allowed_commands": None,
        "max_edit_lines": None,
        "max_files_per_state": None,
        "blocked_env": None,
    },
}

# Default tools available in ALL stages (always allowed)
GLOBAL_TOOLS: list[str] = [
    "clarify",  # asking questions is always permitted
    "todo",     # task management always permitted
]


def get_stage_allowed_commands(stage: str) -> list[str] | None:
    """Get allowed_commands for a stage."""
    return STAGE_WHITELISTS.get(stage, {}).get("allowed_commands")


def get_stage_max_edit_lines(stage: str) -> int | None:
    """Get max_edit_lines for a stage. 0 = no edits allowed."""
    return STAGE_WHITELISTS.get(stage, {}).get("max_edit_lines")


def get_stage_max_files(stage: str) -> int | None:
    """Get max_files_per_state for a stage. 0 = no new files allowed."""
    return STAGE_WHITELISTS.get(stage, {}).get("max_files_per_state")


def get_stage_blocked_env(stage: str) -> list[str] | None:
    """Get blocked_env for a stage."""
    return STAGE_WHITELISTS.get(stage, {}).get("blocked_env")
