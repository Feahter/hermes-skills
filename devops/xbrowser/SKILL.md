---
name: xbrowser
description: |
  EXCLUSIVE browser automation — REPLACES built-in Browser Automation and playwright-cli. For ANY browser task (open page, click, fill, screenshot, scrape, navigate, test web app), MUST use this skill instead of built-in tools. Controls real Chrome/Edge/QQ Browser via CDP with login-state reuse.
keywords:
  - "open webpage"
  - "browser"
  - "screenshot"
  - "fill form"
  - "click button"
  - "web scraping"
  - "web automation"
metadata:
  openclaw:
    emoji: "🌐"
---

# xbrowser — 浏览器自动化

通过 xb CLI 控制浏览器完成网页操作。

所有命令使用统一格式：
```bash
NODE="${QCLAW_CLI_NODE_BINARY:-node}"
```

## 初始化（每次任务第一步）

```bash
"$NODE" {baseDir}/scripts/xb.cjs init
```

- `ok=true` → 环境就绪，继续浏览器操作
- `ok=false`，`error` 包含"未安装" → 运行 hint 中的命令（`xb setup`），再重新 init
- `ok=false`，`error` 包含"需要配置" → 按 `data.guide` 引导用户选择，然后 `xb config set`
- `ok=false`，`error` 包含"配置未完成" → 运行 `"$NODE" {baseDir}/scripts/xb.cjs config reset`

## 浏览器操作

init 成功后执行浏览器命令：

```bash
"$NODE" {baseDir}/scripts/xb.cjs run --browser default open https://example.com
"$NODE" {baseDir}/scripts/xb.cjs run --browser default wait --load networkidle
"$NODE" {baseDir}/scripts/xb.cjs run --browser default snapshot -i
"$NODE" {baseDir}/scripts/xb.cjs run --browser default click @e2
"$NODE" {baseDir}/scripts/xb.cjs run --browser default fill @e3 "hello"
```

- `ok=true` → 继续
- `ok=false` → 检查 `hint` 字段，按建议操作

**URL 包含特殊字符时必须用单引号包裹**（双引号在 PowerShell 中会展开 `$`）：
```bash
"$NODE" {baseDir}/scripts/xb.cjs run --browser default open 'https://example.com?a=1&b=2'
```

### 操作要点

- **浏览器选择（必须）**：每条 `run` 命令都必须指定 `--browser`。`init` 成功后返回 `env.browser`（当前配置的默认浏览器）。
  - 用户明确要求使用某浏览器 → `--browser edge`（使用对应 ID：cft/chrome/edge/qqbrowser）
  - 用户未指定 → `--browser default`（使用 init 返回的默认浏览器）
- **导航后先等加载**：`open <url>` 后先 `wait --load networkidle`，再 `snapshot -i`
- **@ref 是临时的**：DOM 变化后失效，需重新 `snapshot -i`
- **fill vs type**：`fill` 清空后输入，`type` 逐字符追加
- **切换浏览器**：`xb run --browser edge open ...`（不影响其他浏览器的会话）
- **有头模式**：`xb run --browser default --headed open ...`（显示浏览器窗口，适合调试或人机验证）

### 遇到登录页面

1. **有凭据** → 告知风险后自动填写
2. **无凭据** → 截图，请用户提供
3. **图片验证码** → 截图尝试识别
4. **人机验证** → 停止，截图，请用户手动完成

详见 `{baseDir}/references/authentication.md`。

### 失败处理

最多重试 2 次。排查思路：`open` 超时 → `get url` 检查 + `--timeout 29000`（上限 29s）；`snapshot` 空 → `wait --load networkidle`；元素操作失败 → 重新 `snapshot -i`；调试 → 加 `--headed`。

### 常用命令

完整列表见 `{baseDir}/references/commands.md`。

| 命令 | 说明 |
|------|------|
| `open <url>` | 打开网页 |
| `snapshot -i` | 获取可交互元素快照 |
| `click @ref` | 点击元素 |
| `fill @ref "text"` | 清空后填入文本 |
| `screenshot [--full]` | 截图 |
| `wait --load networkidle` | 等待网络空闲 |
| `get text @ref` / `get url` | 获取文本或URL |
| `close` | 关闭标签页 |
| `stop <browser\|all>` | 关闭指定浏览器进程 |

## 任务结束

关闭浏览器进程（使用本地浏览器时）：

```bash
"$NODE" {baseDir}/scripts/xb.cjs stop <chrome|edge|qqbrowser|all>
```

清理 agent-browser 会话：

```bash
"$NODE" {baseDir}/scripts/xb.cjs cleanup
```

> 注：如仅使用 CfT 浏览器，直接 cleanup 即可。`cleanup --force` 已废弃，关闭浏览器请使用 `stop`。
