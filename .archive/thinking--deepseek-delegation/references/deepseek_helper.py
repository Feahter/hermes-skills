"""
DeepSeek delegation helper — 通过 tmux + deepseek-tui 发送任务并捕获结果。

关键：deepseek-tui 使用 Composer（Draft）界面，需要先输入内容再按 Ctrl+O 发送。

用法：
    from deepseek_helper import send_task, switch_model

    # 顾问模式（v4-pro，处理复杂问题）
    send_task("帮我分析这个架构问题...")

    # 批量模式（flash，处理简单任务）
    switch_model("deepseek-chat")  # 切换到 flash
    send_task("翻译这段文字")

    # 切换回 pro
    switch_model("deepseek-v4-pro")
"""

import subprocess
import time
import re

SESSION = "deepseek"


def send(prompt: str, confirm: bool = True):
    """
    发送 prompt 到 deepseek-tui。
    confirm=True：Composer 模式，先输入内容，再按 Ctrl+O 发送。
    confirm=False：直接发送（用于切换模型等命令）。
    """
    # 先按 Ctrl+C 中断可能正在运行的任务
    subprocess.run(["tmux", "send-keys", "-t", SESSION, "C-c"], check=False)
    time.sleep(0.3)

    # 输入内容到 Composer（Draft）
    subprocess.run(["tmux", "send-keys", "-t", SESSION, prompt, "Enter"])

    if confirm:
        time.sleep(0.5)
        subprocess.run(["tmux", "send-keys", "-t", SESSION, "C-o"])  # 确认发送


def capture_raw() -> str:
    """抓取 tmux pane 原始内容"""
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", SESSION, "-p"],
        capture_output=True, text=True
    )
    return result.stdout


def parse_response(raw: str) -> str:
    """
    从 tmux capture 中提取 DeepSeek 回复块。

    匹配格式：
      ┌Composer──────────────────────────────────────────────────────────────────────┐
      │                                                                              │
      │内容                                                                         │
      └──────────────────────────────────────────────────────────────────────────────┘
      agent · deepseek-v4-pro · draft   ← 发送前的 draft
    """
    lines = raw.split('\n')
    # 找最新的 ┌ 或 ╭ 开始，到第一个 ❯ 或 >_ 结束的区域
    result_lines = []
    capture = False
    for line in lines:
        if ('❯' in line or '>_' in line) and 'deepseek' not in line.lower():
            capture = False
        if capture:
            result_lines.append(line)
        if '┌' in line and '──────────────────────────────────────' in line:
            capture = True
    return '\n'.join(result_lines).strip()


def switch_model(model: str):
    """切换 deepseek-tui 模型（如 'deepseek-chat' 切换到 flash）"""
    send(f"/model {model}", confirm=False)
    time.sleep(2)


def send_task(prompt: str, wait: float = 15.0, confirm: bool = True) -> str:
    """发送任务并等待结果"""
    send(prompt, confirm=confirm)
    time.sleep(wait)
    return capture_raw()


def send_and_confirm(prompt: str, wait: float = 20.0) -> str:
    """发送 Draft 并确认（Composer 模式），等待回复"""
    send(prompt, confirm=True)
    time.sleep(wait)
    raw = capture_raw()
    # 提取 agent 回复部分
    return extract_agent_response(raw)


def extract_agent_response(raw: str) -> str:
    """从 raw capture 中提取 agent 的完整回复"""
    lines = raw.split('\n')
    # 找 agent 回复的起点（通常是第一次出现 ● 或 >_ 或 Hermes 消息块）
    result = []
    for line in lines:
        if '╭─' in line or '│' in line:
            result.append(line)
    return '\n'.join(result).strip()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python deepseek_helper.py <prompt>")
        sys.exit(1)
    result = send_task(sys.argv[1])
    print(result)