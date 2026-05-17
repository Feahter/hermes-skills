---
name: peekaboo
description: |
  macOS 原生 GUI 自动化 — 基于 Accessibility API 精确定位 UI 元素，替代坐标点击。
  支持截图、点击/输入/滚动、菜单栏/Dock/窗口操作、AI 视觉分析。
  Use when the user mentions macOS GUI automation, screen interaction,
  menu-driven tasks, Accessibility API, or automating macOS desktop apps.
triggers:
  - GUI自动化
  - 屏幕截图
  - 菜单操作
  - 窗口管理
  - Accessibility
category: system
phases:
  - execution
version: "1.1.0"
---

# Peekaboo

macOS 原生 GUI 自动化，基于 Accessibility API（AXUIElement），支持截图、元素定位、输入模拟、菜单/窗口操作。

## 核心优势 vs mac-use

| 能力 | mac-use | peekaboo |
|------|---------|----------|
| UI 元素定位 | OCR 坐标 | ID/label 直接引用 |
| 菜单读取 | ❌ | `menu list` 结构化 JSON |
| 菜单栏/Dock | ❌ | `menubar/dock` 命令 |
| Dialog 驱动 | ❌ | `dialog input/click` |
| AI 视觉分析 | ❌ | `--analyze "..."` |
| 自然语言 Agent | ❌ | `peekaboo agent "..."` |

## 安装

```bash
# npm（推荐，Homebrew 有超时问题）
npm install -g @steipete/peekaboo
peekaboo --version  # 验证

# 权限（必须）
peekaboo permissions status
peekaboo permissions grant   # 仅对非 GUI 保护目录有效；macOS 弹窗需手动在 System Settings 中勾选
open "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenRecording"
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
# 将终端应用勾选加入两个列表
peekaboo permissions status
```

> **系统要求：macOS 15+ (Sequoia)**，不支持旧版本。

## 典型工作流

**自动填写表单：**
```bash
# 1. 截图 + 获取元素列表
SNAP=$(peekaboo see --app "MyApp" --json | jq -r '.data.snapshot_id')

# 2. 按 label 填写
peekaboo set-value --on "用户名" --value "test@email.com" --snapshot "$SNAP"
peekaboo set-value --on "密码" --value "pass123" --snapshot "$SNAP"

# 3. 点击提交
peekaboo click --on "登录" --snapshot "$SNAP"
```

**菜单驱动自动化：**
```bash
peekaboo menu list --app Safari
peekaboo menu click --app Safari --path "文件/另存为..."
```

**自然语言 Agent：**
```bash
peekaboo agent "打开 Safari，访问 github.com，点击 Sign in"
```

## 限制

- **macOS 15+ 必须**，不支持旧系统
- Screen Recording + Accessibility 权限必须（见下节）
- SIP 下某些系统应用受限
- Agent 模式 token 消耗较高

## Pitfalls（避坑）

| 坑 | 原因 | 解法 |
|----|------|------|
| `click --on elem_X` 报 Element not found | 缺少 `--snapshot` | 先 `see --app X` 获取 snapshot，再 `click --on elem_X --snapshot $SNAP` |
| `dock launch --name X` 报 Unknown option | `--name` 不存在 | 用位置参数：`peekaboo dock launch Safari` |
| `see --json` 返回无 elements | Accessibility 未授权 | 去 System Settings → Privacy & Security → Accessibility 授权终端 |
| `click --on "标签文本"` 失败 | `--on` 接受 element ID（如 `elem_19`），不接受 label | 先看 snapshot 输出里的 element ID |
| snapshot_id 提取失败 | JSON 结构是 `data.snapshot_id` | 用 `jq -r '.data.snapshot_id'`，不要直接 `.snapshot_id` |

## 命令速查

详细命令 → `references/command-reference.md`
安装配置 → `references/install-setup.md`
命令勘误 → `references/command-corrections.md`（dock/click 等常见错误）

## 与现有 Skills

- **替代** `mac-use`：peekaboo 用 AXUIElement 替代 OCR 坐标
- **互补** `browser`：browser 抓网页，peekaboo 控本地 GUI
- **增强** `automation-workflows`：作为 macOS GUI 层执行器
