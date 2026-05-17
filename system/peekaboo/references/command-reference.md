# Peekaboo 命令速查表

## 截图与查看

| 命令 | 功能 |
|------|------|
| `peekaboo see --mode screen --json` | 全屏截图 + 可点击元素列表 |
| `peekaboo see --app Safari --json` | 指定应用窗口截图 |
| `peekaboo image --mode screen --retina` | Retina 截图保存 |
| `peekaboo image --mode menu --retina` | 菜单栏截图 |
| `peekaboo image --mode screen --analyze "描述"` | AI 分析截图 |

## 点击与输入

| 命令 | 功能 |
|------|------|
| `peekaboo click --on "标签"` | 通过标签文本点击 |
| `peekaboo click --on B1 --snapshot ID` | 通过元素 ID 点击 |
| `peekaboo click --at 100,200` | 坐标点击 |
| `peekaboo type --text "文字" --clear` | 清空后输入 |
| `peekaboo type --text "文字" --delay-ms 50` | 逐字输入（防抖） |
| `peekaboo set-value --on T1 --value "文字"` | 直接设置值（绕过输入框） |

## 按键与快捷键

| 命令 | 功能 |
|------|------|
| `peekaboo press return` | 按 Return 键 |
| `peekaboo press escape --repeat 2` | 按 ESC 两次 |
| `peekaboo hotkey cmd,shift,t` | Cmd+Shift+T |

## 滚动与手势

| 命令 | 功能 |
|------|------|
| `peekaboo scroll --direction down --ticks 3` | 向下滚动 3 次 |
| `peekaboo scroll --on B1 --direction up` | 滚动指定元素 |
| `peekaboo swipe --from 100,400 --to 100,200` | 滑动手势 |
| `peekaboo drag --from 100,200 --to 300,400` | 拖拽 |

## 菜单操作

| 命令 | 功能 |
|------|------|
| `peekaboo menu list --app Safari` | 列出应用菜单（结构化） |
| `peekaboo menu list-all --app Safari` | 列出所有菜单项 |
| `peekaboo menu click --app Safari --path "文件/另存为"` | 点击菜单路径 |
| `peekaboo menu click-extra --app Safari --path "编辑/全选"` | 点击 Extra 菜单 |

## 菜单栏操作

| 命令 | 功能 |
|------|------|
| `peekaboo menubar list` | 列出菜单栏项目 |
| `peekaboo menubar click --index 1` | 点击第 N 个菜单栏项 |
| `peekaboo menubar click --name "Wi-Fi"` | 按名称点击 |

## Dock 操作

| 命令 | 功能 |
|------|------|
| `peekaboo dock list` | 列出 Dock 应用 |
| `peekaboo dock launch Safari` | 启动应用 |
| `peekaboo dock right-click Finder` | 右键点击 |
| `peekaboo dock hide Safari` | 隐藏应用 |

## 常见问题（实测）

### Q: JSON 输出里 snapshot_id 在哪？
A: 在 `data.snapshot_id`，不在顶层。
```bash
jq -r '.snapshot_id'        # ❌ KeyError
jq -r '.data.snapshot_id'   # ✅
```

### Q: `click --at x,y` 报错 Unknown option
A: 用 `--coords`：`peekaboo click --coords 100,100`

### Q: `dock launch --name Safari` 报错
A: 位置参数：`peekaboo dock launch Safari`（无 `--name`）

## Dialog 操作

| 命令 | 功能 |
|------|------|
| `peekaboo dialog list` | 列出当前 dialog 元素 |
| `peekaboo dialog click --on "取消"` | 点击按钮 |
| `peekaboo dialog input --on T1 --value "路径"` | 输入文件路径 |
| `peekaboo dialog dismiss` | 关闭 dialog |

## 窗口与 Space

| 命令 | 功能 |
|------|------|
| `peekaboo window list` | 列出所有窗口 |
| `peekaboo window move --id W1 --to 0,0` | 移动窗口 |
| `peekaboo window resize --id W1 --width 800` | 调整大小 |
| `peekaboo window focus --id W1` | 聚焦窗口 |
| `peekaboo space list` | 列出 Space |
| `peekaboo space switch --index 2` | 切换 Space |

## 应用管理

| 命令 | 功能 |
|------|------|
| `peekaboo app list` | 列出运行中的应用 |
| `peekaboo app launch --name Safari` | 启动应用 |
| `peekaboo app quit --name Safari` | 退出应用 |
| `peekaboo app switch --name Safari` | 切换到应用 |

## Agent 模式

| 命令 | 功能 |
|------|------|
| `peekaboo agent "打开 Safari 访问 github.com"` | 自然语言自动化 |
| `peekaboo agent --dry-run "自动化流程"` | 预览不执行 |
| `peekaboo agent --max-steps 10 "流程"` | 限制最大步数 |
| `peekaboo agent --resume SESSION_ID` | 恢复会话 |

## 权限与系统

| 命令 | 功能 |
|------|------|
| `peekaboo permissions status` | 检查权限状态 |
| `peekaboo permissions grant` | 引导授权 |
| `peekaboo list apps` | 列出可见应用 |
| `peekaboo list screens` | 列出屏幕 |
| `peekaboo clean --all-snapshots` | 清理缓存快照 |

## MCP Server

```bash
# 启动 MCP server
peekaboo mcp serve

# 配置示例（Claude Code config.json）
{
  "mcpServers": {
    "peekaboo": {
      "command": "npx",
      "args": ["-y", "@steipete/peekaboo"]
    }
  }
}
```
