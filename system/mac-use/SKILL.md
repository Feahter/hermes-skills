---
name: mac-use
description: >
  macOS GUI 自动化 — 通过"截图→OCR识别→点击/输入"的方式操作任意 Mac 桌面应用。
  也整合了 Apple 原生应用（Notes/Reminders/iMessage）、Shell 命令执行、
  第三方工具（macbot-cli/Peekaboo/MCP）的完整能力。
  触发：macOS GUI操作、Mac桌面自动化、需要操作应用界面、或需要调用 AppleScript/MCP。
metadata:
  openclaw:
    emoji: "🖥️"
    os: [darwin]
    requires:
      bins: [python3, osascript]
    install:
      - id: python-brew
        kind: brew
        formula: python
        bins: [python3]
        label: Install Python 3 (brew)
      - id: macbot-cli
        kind: pip
        package: macbot-cli
        bins: [macbot]
        label: Install macbot-cli (optional, for advanced controls)
      - id: peekaboo
        kind: brew
        formula: peekaboo
        bins: [peekaboo]
        label: Install Peekaboo (optional, for pixel-precise GUI)
  combinator:
    triggers: ['macOS GUI', 'mac桌面', 'Mac自动化', 'mac-use', '操作mac应用', 'gui自动化', 'apple应用']
---

# Mac Use

macOS 自动化操作员——整合 5 层能力，层层递进，按需取用。

## 能力层次总览

| 层次 | 方式 | 工具/命令 | 适用场景 |
|------|------|----------|---------|
| **L1** | GUI 截图自动化 | `mac_use.py` | 有文字界面的应用（截图→OCR→点击） |
| **L2** | AppleScript/JXA | `osascript` | 支持脚本的原生 Mac 应用 |
| **L3** | Shell 命令 | `terminal` 工具 | 文件操作、open 命令、系统命令 |
| **L4** | 第三方 CLI | `macbot-cli` / `Peekaboo` | 高级控制（通知/窗口/WiFi/像素级操作） |
| **L5** | Apple 原生应用 | 独立 skill | Notes/Reminders/iMessage/FindMy |

## L1: GUI 截图自动化（mac_use.py）

通过 **截图→OCR 识别文字→点击/输入** 的闭环操作任意 GUI 应用。

### Setup

**Python 包**（已安装 pyautogui，若缺失）：
```bash
pip3 install --break-system-packages pyautogui Pillow
```

**macOS 权限**（必须，否则窗口列表为空）：
- 系统设置 → 隐私与安全性 → **辅助功能** → 添加 terminal/hermes
- 系统设置 → 隐私与安全性 → **屏幕录制** → 添加

### Quick Reference

```bash
# 列出所有可见窗口
python3 {baseDir}/scripts/mac_use.py list

# 截图 + OCR 标注（返回图片 + 可点击元素列表）
python3 {baseDir}/scripts/mac_use.py screenshot <app> [--id N]

# 点击编号元素（主要方式）
python3 {baseDir}/scripts/mac_use.py clicknum <N>

# 点击坐标（仅用于无文字的图标）
python3 {baseDir}/scripts/mac_use.py click --app <app> [--id N] <x> <y>

# 滚动
python3 {baseDir}/scripts/mac_use.py scroll --app <app> [--id N] <up|down|left|right> <amount>

# 输入文字（剪贴板粘贴，支持中文）
python3 {baseDir}/scripts/mac_use.py type --app <app> "文字内容"

# 按键
python3 {baseDir}/scripts/mac_use.py key --app <app> <combo>
```

### 坐标系统

截图渲染到 **1000×1000 画布**：
- 原点 (0,0) 在**左上角**
- x 从左到右（0=左边缘，1000=右边缘）
- y 从上到下（0=顶部，1000=底部）
- 点击时脚本自动换算为实际屏幕坐标

### 完整工作流

```bash
# 1. 打开目标应用
open -a "AppName"
sleep 2

# 2. 截图并获取元素列表
python3 {baseDir}/scripts/mac_use.py screenshot appname
# → 返回 JSON 元素列表 + /tmp/mac_use.png 标注图

# 3. 读标注图确认
Read /tmp/mac_use.png

# 4. 点击编号元素
python3 {baseDir}/scripts/mac_use.py clicknum 5

# 5. 输入文字
python3 {baseDir}/scripts/mac_use.py type --app appname "内容"
```

## L2: AppleScript / JXA

直接调用 macOS 原生脚本引擎，操作支持 AppleScript 的应用。

### osascript 基础

```bash
# 执行 AppleScript
osascript -e 'tell application "Finder" to return name of home'

# 多行脚本
osascript -e '
tell application "System Events"
    keystroke "hello"
end tell
'
```

### 常用场景

```bash
# 打开应用
osascript -e 'tell application "Safari" to activate'

# 读写剪贴板
osascript -e 'set the clipboard to "内容"'
osascript -e 'the clipboard'

# 获取应用列表（支持脚本的应用）
osascript -e 'tell application "System Events" to get name of every process'

# 模拟按键
osascript -e '
tell application "System Events"
    keystroke "s" using command down
end tell
'

# 读写文件
osascript -e 'tell application "Finder" to make new folder at desktop with properties {name:"测试"}'
```

### JXA（JavaScript for Automation）

```bash
# 执行 JS 脚本
osascript -l JavaScript -e '
Application("Safari").windows[0].url();
'

# 读写文件
osascript -l JavaScript -e '
const app = Application.currentApplication();
app.includeStandardAdditions = true;
app.doShellScript("echo hello");
'
```

## L3: Shell 命令

通过 terminal 工具执行系统命令，结合 `open` 命令操作应用。

```bash
# 打开任意应用/文件/URL
open -a "WeChat"
open "https://example.com"
open ~/Documents/file.pdf

# 通过 URL Scheme 触发应用动作
open "slack://channel?team=xxx"
open "x-devonthink://search?query=关键词"

# 系统信息
sw_vers           # macOS 版本
system_profiler   # 硬件信息
launchctl list    # 运行中的服务
```

## L4: 第三方工具

### macbot-cli（通知/剪贴板/窗口/音量/WiFi/蓝牙）

```bash
pip3 install --break-system-packages macbot-cli

# 通知
macbot notify "任务完成"

# 剪贴板
macbot clipboard copy "内容"
macbot clipboard paste

# 窗口管理
macbot window list
macbot window move left

# 系统控制
macbot volume set 50
macbot brightness set 80
macbot wifi on
macbot bluetooth off
```

### Peekaboo（像素级精准操作）

> peekaboo 基于 Accessibility API 精确定位 UI 元素，无需 OCR。完整文档 → `peekaboo` skill。
> **必须先 `see --app X --json` 获取 snapshot，再用 `click --on elem_X --snapshot $SNAP`**。

```bash
# 1. 截图 + 获取元素列表
SNAP=$(peekaboo see --app "MyApp" --json | jq -r '.data.snapshot_id')

# 2. 查看输出中的 element ID（如 elem_19）
# 3. 点击指定元素
peekaboo click --on elem_19 --snapshot "$SNAP"

# 菜单栏/Dock 操作（位置参数，不用 --name）
peekaboo dock launch Safari
peekaboo menu list --app Safari
```

**权限：Screen Recording + Accessibility 均必须。macOS 15+ only。**

## L5: Apple 原生应用

| 应用 | Skill | 说明 |
|------|-------|------|
| Notes 备忘录 | `apple-notes` | 创建/读取笔记 |
| Reminders 提醒事项 | `apple-reminders` | 管理待办 |
| iMessage 信息 | `imessage` | 发送短信 |
| FindMy 查找 | `findmy` | 查找设备/AirTag |

## 权限说明

| 权限 | 路径 | 用途 |
|------|------|------|
| 辅助功能 | 隐私与安全性→辅助功能 | 窗口列表、按键模拟 |
| 屏幕录制 | 隐私与安全性→屏幕录制 | 截图（mac_use.py 必须） |
| 完全磁盘访问 | 隐私与安全性→完全磁盘访问 | 访问所有文件 |

## 能力边界

| ✅ 能做到 | ❌ 做不到 |
|---------|---------|
| 有文字界面的 GUI 应用 | 无文字的复杂界面（用 Peekaboo） |
| 启动/激活应用 | 强制终止无响应的应用 |
| 截图→OCR→点击 | 直接操作菜单栏 |
| AppleScript 支持的应用 | 不支持脚本且无界面的应用 |
| Shell 命令执行 | 需要 sudo 的系统操作 |

## How It Works

The `screenshot` command captures a window, uses **Apple Vision OCR** to detect all text elements, draws numbered annotations on the image, and returns both:
1. **Annotated image** at `/tmp/mac_use.png` — numbered green boxes around each detected text
2. **Element list** in JSON — `[{num: 1, text: "Submit", at: [500, 200]}, {num: 2, text: "Cancel", at: [600, 200]}, ...]` where `at` is the center point `[x, y]` on the 1000x1000 canvas (origin at top-left)

You receive both by calling Bash (gets JSON with element list) and then Read on `/tmp/mac_use.png` (gets the visual). **Always do both** so you can cross-reference the numbers with what you see.

## Quick Reference

```bash
# List all visible windows
python3 {baseDir}/scripts/mac_use.py list

# Screenshot + annotate (returns image + numbered element list)
python3 {baseDir}/scripts/mac_use.py screenshot <app> [--id N]

# Click element by number (primary click method)
python3 {baseDir}/scripts/mac_use.py clicknum <N>

# Click at canvas coordinates (fallback for unlabeled icons)
python3 {baseDir}/scripts/mac_use.py click --app <app> [--id N] <x> <y>

# Scroll inside a window
python3 {baseDir}/scripts/mac_use.py scroll --app <app> [--id N] <direction> <amount>

# Type text (uses clipboard paste — supports all languages)
python3 {baseDir}/scripts/mac_use.py type [--app <app>] "text here"

# Press key or combo
python3 {baseDir}/scripts/mac_use.py key [--app <app>] <combo>
```

## Workflow

1. **Open** the target app with `open -a "App Name"` (optionally with a URL or file path)
2. **Wait** for it to load: `sleep 2`
3. **Screenshot** the app:
   ```bash
   python3 {baseDir}/scripts/mac_use.py screenshot <app> [--id N]
   ```
   This returns JSON with `file` (image path) and `elements` (numbered text list).
4. **Read** the annotated image at `/tmp/mac_use.png` to see the numbered elements visually
5. **Decide** which element to interact with:
   - **Prefer `clicknum N`** — pick the number of a detected text element
   - **Fallback `click --app <app> x y`** — only for unlabeled icons (arrows, close buttons, cart icons) that have no text and therefore no number
6. **Act** using `clicknum`, `type`, `key`, or `scroll`
7. **Screenshot again** to verify the result
8. Repeat from step 3

## Commands

### list

Show all visible app windows.

```bash
python3 {baseDir}/scripts/mac_use.py list
```

Returns JSON array: `[{"app":"Google Chrome","title":"Wikipedia","id":4527,"x":120,"y":80,"w":1200,"h":800}, ...]`

### screenshot

Capture a window, detect text elements via OCR, annotate with numbered markers, and return the element list. The target window is automatically raised to the top before capture, so overlapping windows are handled.

```bash
python3 {baseDir}/scripts/mac_use.py screenshot chrome
python3 {baseDir}/scripts/mac_use.py screenshot chrome --id 4527
```

- `<app>`: fuzzy, case-insensitive match (e.g. "chrome" matches "Google Chrome")
- `--id N`: target a specific window ID (required when multiple windows of the same app exist)
- Returns JSON with:
  - `file`: path to annotated screenshot (`/tmp/mac_use.png`)
  - `id`, `app`, `title`, `scale`: window metadata
  - `elements`: array of `{num, text, at}` — the numbered clickable text elements, where `at` is `[x, y]` center coordinates on the 1000x1000 canvas (origin at top-left)
- If multiple windows match, returns a list of windows instead — pick one and retry with `--id`
- The image is 1000x1000 pixels with green bounding boxes and blue number badges
- Element map is saved to `/tmp/mac_use_elements.json` for `clicknum`

### clicknum

Click on a numbered element from the last screenshot. **This is the primary click method.**

```bash
python3 {baseDir}/scripts/mac_use.py clicknum 5
python3 {baseDir}/scripts/mac_use.py clicknum 12
```

- `N`: the element number from the last `screenshot` output
- Reads the saved element map, activates the window, and clicks at the element's center
- Returns JSON with `clicked_num`, `text`, canvas coords, and absolute screen coords

### click

Click at a position using canvas coordinates. **Fallback only — use for unlabeled icons.**

```bash
python3 {baseDir}/scripts/mac_use.py click --app chrome 500 300
python3 {baseDir}/scripts/mac_use.py click --app chrome --id 4527 500 300
```

- **Coordinates are canvas positions (0-1000)** from the screenshot image
- x=0 is left, x=1000 is right; y=0 is top, y=1000 is bottom
- Use this only when Vision OCR didn't detect the element (icon-only buttons, images, etc.)

### scroll

Scroll inside an app window.

```bash
python3 {baseDir}/scripts/mac_use.py scroll --app chrome down 5
python3 {baseDir}/scripts/mac_use.py scroll --app notes up 10
```

- Directions: `up`, `down`, `left`, `right`
- Amount: number of scroll clicks (3-5 for moderate, 10+ for fast scrolling)
- Mouse is moved to the center of the window before scrolling

### type

Type text into the currently focused input field.

```bash
python3 {baseDir}/scripts/mac_use.py type --app chrome "hello world"
python3 {baseDir}/scripts/mac_use.py type --app chrome "你好世界"
```

- `--app`: activates the app first to ensure keystrokes go to the right window
- Uses clipboard paste (Cmd+V) for reliable Unicode/CJK support
- **Always click on the target input field first** before typing

### key

Press a single key or key combination.

```bash
python3 {baseDir}/scripts/mac_use.py key --app chrome return
python3 {baseDir}/scripts/mac_use.py key --app chrome cmd+a
python3 {baseDir}/scripts/mac_use.py key --app chrome cmd+shift+s
```

- `--app`: activates the app first
- Common keys: `return`, `tab`, `escape`, `space`, `delete`, `backspace`, `up`, `down`, `left`, `right`
- Modifiers: `cmd`, `ctrl`, `alt`/`opt`, `shift`

## Important Rules

- **Always screenshot before your first interaction** with an app
- **Always screenshot after an action** to verify the result
- **Always Read the screenshot image** after running the screenshot command — you need both the element list AND the visual
- **Prefer `clicknum`** over `click` — only use direct coordinates for unlabeled icons
- **Click before typing** — ensure the correct input field has focus first
- **Multiple windows**: if you get `multiple_windows` error, use `list` to see all windows, then pass `--id`
- **Popup windows** (like WeChat mini-program panels) are separate windows with their own IDs — use `list` to find them and `--id` to target them
- **Wait after opening apps**: use `sleep 2-3` after `open -a` before taking a screenshot
- **Activate the app** before screenshot/click: prepend `osascript -e 'tell application "AppName" to activate' && sleep 1` when the target app may be behind other windows
- **Do not type passwords or secrets** via this tool

## Coordinate System (for fallback `click` only)

Screenshots are rendered onto a **1000x1000 canvas**:
- **Origin (0, 0)** is at the **top-left** corner
- **x** increases left to right (0 = left edge, 1000 = right edge)
- **y** increases top to bottom (0 = top edge, 1000 = bottom edge)
- The app window is scaled to fit (aspect ratio preserved), centered, with dark gray padding

## Example: Order food on Meituan in WeChat

```bash
# 1. Open WeChat
open -a "WeChat"
sleep 3

# 2. Screenshot WeChat — find the mini program window
python3 {baseDir}/scripts/mac_use.py list
# → find the mini program window ID

# 3. Screenshot the mini program (annotated + element list)
python3 {baseDir}/scripts/mac_use.py screenshot 微信 --id 41266
# → returns: {"file": "/tmp/mac_use.png", "elements": [{num: 1, text: "搜索", at: [500, 200]}, ...]}
# → Read /tmp/mac_use.png to see annotated image

# 4. Click "搜索" (element #1)
python3 {baseDir}/scripts/mac_use.py clicknum 1

# 5. Type search query
python3 {baseDir}/scripts/mac_use.py type --app 微信 "炸鸡"

# 6. Press Enter
python3 {baseDir}/scripts/mac_use.py key --app 微信 return
sleep 2

# 7. Screenshot to see results
python3 {baseDir}/scripts/mac_use.py screenshot 微信 --id 41266
# → Read /tmp/mac_use.png, pick a restaurant by number

# 8. Click on a restaurant (e.g. element #5)
python3 {baseDir}/scripts/mac_use.py clicknum 5
```
