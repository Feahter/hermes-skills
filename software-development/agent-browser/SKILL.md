---
name: local-agent-browser
description: Fast headless browser automation CLI for AI agents (v0.26.0). Use when automating web interactions, scraping, filling forms, testing UIs, parallel sessions, network mocking, HAR recording, AI chat control, or auth vault. Keywords: browser, automation, headless, screenshot, scrape, form-fill, web-testing, batch, har, chat, auth-vault.
read_when:
  - Automating web interactions or scraping
  - Filling forms programmatically
  - Testing web UIs
  - Needing parallel browser sessions
  - Network interception/mocking
  - HAR traffic recording
  - AI natural-language browser control
metadata: {"clawdbot":{"emoji":"🌐","requires":{"bins":["node","npm"]}}}
allowed-tools: Bash(agent-browser:*)
---

# Browser Automation — agent-browser v0.26.0

## Version & Path

**当前版本**：v0.26.0（hermes-agent 捆绑）
**CLI 路径**：`~/.hermes/hermes-agent/node_modules/.bin/agent-browser`
**版本确认**：`agent-browser --version`

> hermes-agent 内部调用捆绑版。升级 hermes-agent 的 `node_modules` 后才可用新命令。
> 全局 npm 安装路径（可能落后）：`/usr/local/.../agent-browser`

---

## 快速开始

```bash
agent-browser open <url>              # 1. 导航
agent-browser snapshot -i             # 2. 快照（仅交互元素）→ 得到 @e1 @e2 ...
agent-browser click @e1               # 3. 操作
agent-browser close                   # 4. 关闭
```

命令链（减少进程启动开销）：
```bash
agent-browser open example.com && agent-browser snapshot -i && agent-browser click @e1
```

---

## 核心工作流

1. **打开**：`agent-browser open <url>`
2. **快照**：`agent-browser snapshot -i` → 返回 refs（`@e1`, `@e2`）
3. **操作**：用 refs 交互
4. **重快照**：导航或 DOM 变化后重新 snapshot

---

## 导航

```bash
agent-browser open <url>      # 导航
agent-browser back             # 后退
agent-browser forward          # 前进
agent-browser reload           # 刷新
agent-browser close            # 关闭浏览器
agent-browser close --all      # 关闭所有 session
```

---

## 快照（页面分析）

```bash
agent-browser snapshot              # 完整 accessibility 树
agent-browser snapshot -i           # 仅交互元素（推荐）
agent-browser snapshot -c           # 紧凑 — 移除空结构元素
agent-browser snapshot -d <n>       # 限制深度
agent-browser snapshot -s "<sel>"   # 限定 CSS 选择器范围
agent-browser snapshot --json        # 机器可读输出
```

---

## 交互操作

**用 refs（snapshot 返回的引用）：**
```bash
agent-browser click @e1              # 单击
agent-browser dblclick @e1           # 双击
agent-browser focus @e1               # 聚焦
agent-browser fill @e2 "text"        # 清空后填充
agent-browser type @e2 "text"        # 追加输入
agent-browser press Enter            # 按键（Enter/Tab/Control+a 等）
agent-browser hover @e1              # 悬停
agent-browser check @e1              # 勾选
agent-browser uncheck @e1            # 取消勾选
agent-browser select @e1 "value"     # 下拉选择
agent-browser scroll down 500        # 滚动
agent-browser scrollintoview @e1     # 滚动到元素
agent-browser drag @e1 @e2           # 拖放
agent-browser upload @e1 file.pdf    # 上传文件
agent-browser download @e1 [path]    # 下载文件
```

**用 CSS 选择器（传统方式）：**
```bash
agent-browser click "#submit-button"
agent-browser fill "input[name='email']" "test@example.com"
agent-browser click "text=Submit"
```

---

## 语义定位器（AI 友好，无需 ref）

```bash
agent-browser find role button click --name "Submit"
agent-browser find text "Sign In" click
agent-browser find label "Email" fill "user@test.com"
agent-browser find first ".item" click
agent-browser find nth 2 "a" text
# 选项：--exact 精确匹配，--name <name> 按 accessible name 过滤
```

---

## 获取信息

```bash
agent-browser get text @e1           # 元素文本
agent-browser get html @e1           # innerHTML
agent-browser get value @e1          # 输入值
agent-browser get attr @e1 href      # 属性值
agent-browser get title              # 页面标题
agent-browser get url                # 当前 URL
agent-browser get count ".item"      # 匹配元素数量
agent-browser get box @e1           # 边界框 {x,y,width,height}
agent-browser get styles @e1        # 计算样式
agent-browser get cdp-url            # CDP WebSocket URL
```

---

## 检查状态

```bash
agent-browser is visible @e1
agent-browser is enabled @e1
agent-browser is checked @e1
```

---

## 截图 & PDF

```bash
agent-browser screenshot [path.png]    # 截图（默认 stdout）
agent-browser screenshot --full        # 全页截图
agent-browser screenshot --annotate      # 带编号标签的标注截图
agent-browser pdf output.pdf            # 保存为 PDF
```

---

## 视频录制

```bash
agent-browser record start ./demo.webm    # 开始录制
agent-browser click @e1                    # 执行操作
agent-browser record stop                  # 停止并保存
```
录制会创建新 context，但保留 cookies/storage。

---

## 等待

```bash
agent-browser wait @e1                 # 等待元素出现
agent-browser wait 2000                 # 等待毫秒数
agent-browser wait --load networkidle   # 等待网络空闲
agent-browser wait --url "/dashboard"   # 等待 URL 匹配
```

---

## Batch 执行（批量命令，减少进程开销）

```bash
agent-browser batch "open https://example.com" "snapshot -i" "click @e1"
# --bail：遇首个错误即停止（默认继续全部）
```

---

## Mouse & Keyboard

```bash
agent-browser mouse move <x> <y>        # 移动鼠标
agent-browser mouse down [btn]          # 按下按钮
agent-browser mouse up [btn]            # 释放按钮
agent-browser mouse wheel <dy> [dx]     # 滚轮滚动
agent-browser keyboard type <text>     # 真实按键事件输入
agent-browser keyboard inserttext <text> # 无按键事件插入文本
```

---

## 浏览器设置

```bash
agent-browser set viewport 1920 1080
agent-browser set device "iPhone 14"
agent-browser set geo 37.7749 -122.4194
agent-browser set offline on
agent-browser set headers '{"X-Key":"v"}'
agent-browser set credentials user pass
agent-browser set media dark
```

---

## 网络拦截 & Mocking

```bash
agent-browser network route <url>              # 拦截请求
agent-browser network route <url> --abort       # 阻止请求
agent-browser network route <url> --body '{}'  # Mock 响应体
agent-browser network unroute [url]             # 取消拦截
agent-browser network requests                  # 查看追踪的请求
agent-browser network requests --filter api    # 过滤
```

---

## HAR 录制（v0.26.0 新增）

```bash
agent-browser har start /tmp/capture.har   # 开始录制
# ... 执行操作 ...
agent-browser har stop                      # 停止并保存
```

---

## 剪贴板（v0.26.0 新增）

```bash
agent-browser clipboard read    # 读取剪贴板
agent-browser clipboard write "text"  # 写入剪贴板
agent-browser clipboard copy "text"   # 复制
agent-browser clipboard paste         # 粘贴
```

---

## AI Chat 控制（v0.26.0 新增）

```bash
# 单次自然语言指令
agent-browser chat "open google.com and search for cats"
agent-browser -q chat "summarize this page"    # 静默模式（仅文本）

# 交互 REPL 模式
agent-browser chat
```

> 需要设置 `AI_GATEWAY_API_KEY` 环境变量

---

## 诊断 & 升级（v0.26.0 新增）

```bash
agent-browser doctor        # 诊断安装问题
agent-browser doctor --fix  # 自动修复
agent-browser upgrade       # 升级到最新版本
```

---

## 内置 Skills 子系统（v0.26.0 新增）

```bash
agent-browser skills list              # 列出可用 skills
agent-browser skills get core          # 核心用法指南
agent-browser skills get core --full   # 完整命令参考
agent-browser skills get electron      # Electron 专用
agent-browser skills get slack         # Slack 专用
agent-browser skills get dogfood       # 探索性测试
agent-browser skills path [name]       # skill 目录路径
```

---

## 观测面板（v0.26.0 新增）

```bash
agent-browser dashboard start      # 启动面板（默认端口 4848）
agent-browser dashboard start --port 9191
agent-browser dashboard stop       # 停止面板
```

---

## WebSocket 流（v0.26.0 新增）

```bash
agent-browser stream enable [--port <n>]   # 启用运行时流
agent-browser stream status                 # 查看状态和端口
agent-browser stream disable                # 停止流
```

---

## Auth Vault（v0.26.0 新增 — 加密凭证存储）

```bash
agent-browser auth save <name> [--url <url> --username <u> --password <p>]
agent-browser auth login <name>    # 使用保存凭证自动填表登录
agent-browser auth list            # 列出保存的凭证
agent-browser auth show <name>     # 查看凭证元数据
agent-browser auth delete <name>   # 删除凭证
```

---

## 动作确认（v0.26.0 新增）

```bash
agent-browser confirm <id>         # 批准待确认动作
agent-browser deny <id>           # 拒绝待确认动作
```
可用 `--confirm-actions` 或 `--confirm-interactive` 控制确认策略。

---

## Cookies & Storage

```bash
agent-browser cookies                    # 获取所有 cookies
agent-browser cookies set name value     # 设置 cookie（含 --url/--domain/--expires 等选项）
agent-browser cookies clear              # 清除 cookies
agent-browser storage local             # 获取 localStorage
agent-browser storage local key         # 获取特定 key
agent-browser storage local set k v     # 设置值
agent-browser storage local clear        # 清除
```

---

## Tabs

```bash
agent-browser tab              # 列出 tabs
agent-browser tab new [url]    # 新建 tab
agent-browser tab new --label docs  # 带标签新建
agent-browser tab close        # 关闭当前 tab
agent-browser tab 2            # 切换到 tab 2
```
> Tab ID 用 `t` 前缀（`t1`, `t2`），非位置整数

---

## Sessions（并行隔离浏览器）

```bash
agent-browser --session test1 open site-a.com
agent-browser --session test2 open site-b.com
agent-browser session list
agent-browser session           # 显示当前 session 名
```

**自动状态持久化（session-name）：**
```bash
agent-browser --session-name myapp open example.com  # 自动保存 cookies + localStorage
```
下次用相同名称自动恢复状态。

**状态加密（AES-256-GCM）：**
```bash
export AGENT_BROWSER_ENCRYPTION_KEY="<64-char hex key>"
export AGENT_BROWSER_STATE_EXPIRE_DAYS=30   # 超过 N 天自动删除状态
```

**复用 Chrome profile：**
```bash
agent-browser --profile Default open gmail.com        # 复用 Chrome 已登录状态
agent-browser --profile ~/.myapp open example.com     # 自定义 profile 路径
agent-browser profiles                               # 列出可用 profiles
agent-browser --auto-connect open github.com         # 连接运行中 Chrome
```

---

## JavaScript

```bash
agent-browser eval "document.title"    # 执行任意 JS
```

**expression 参数核心规则：**

| 陷阱 | 后果 | 正确做法 |
|------|------|---------|
| 返回未序列化 DOM 节点 | 表达式成功但数据丢失 | 始终 `JSON.stringify()`，处理循环引用 |
| 依赖页面异步加载 | 元素不存在 | 先注入等待：`await new Promise(r => setTimeout(r, 500))` |
| 修改页面状态（click/submit） | 污染后续操作基准 | 只读探针与操作脚本严格分离 |
| 忽略跨域 iframe | 权限边界外 | 先检查 `window.frames` 权限 |

```javascript
// 检测 React/Vue 组件树状态
JSON.stringify([...document.querySelectorAll('*')]
  .filter(e => e._reactInternalFiber || e.__vue__)
  .map(e => ({tag: e.tagName, key: Object.keys(e).find(k => k.startsWith('_react') || k.startsWith('__vue__'))})))

// 检测慢加载资源
JSON.stringify(performance.getEntriesByType('resource')
  .filter(r => r.duration > 100)
  .map(r => ({name: r.name.split('?')[0], duration: r.duration})))
```

---

## Diff 对比

```bash
agent-browser diff snapshot       # 当前 vs 上次 snapshot
agent-browser diff screenshot --baseline   # 当前 vs baseline 图片
agent-browser diff url <u1> <u2>  # 两 URL 页面对比
```

---

## 调试

```bash
agent-browser open example.com --headed       # 显示浏览器窗口
agent-browser console                         # 查看控制台日志
agent-browser console --clear                # 清除控制台
agent-browser errors                          # 查看页面错误
agent-browser errors --clear                 # 清除错误
agent-browser highlight @e1                  # 高亮元素
agent-browser inspect                        # 打开 Chrome DevTools（v0.26.0 新增）
agent-browser trace start                     # 开始 trace 录制
agent-browser trace stop trace.zip           # 停止 + 保存
agent-browser profiler start [path]          # 开始 JS profiler
agent-browser profiler stop [path]           # 停止 profiler
agent-browser --cdp 9222 snapshot           # 通过 CDP 端口连接
```

---

## Options 参考

| Flag | 说明 |
|------|------|
| `--session <name>` | 隔离 session |
| `--session-name <name>` | 自动保存/恢复状态（cookies + localStorage） |
| `--profile <name\|path>` | 复用 Chrome profile |
| `--state <path>` | 加载已保存的认证状态 JSON |
| `--auto-connect` | 自动发现并连接运行中的 Chrome |
| `--json` | JSON 输出 |
| `--full` | 全页截图 |
| `--annotate` | 带编号标签的标注截图 |
| `--headed` | 显示浏览器窗口 |
| `--timeout <ms>` | 命令超时 |
| `--cdp <port>` | CDP 连接端口 |
| `--no-auto-dialog` | 禁用自动关闭对话框 |
| `--executable-path <path>` | 自定义浏览器路径 |
| `--args <args>` | 浏览器启动参数 |
| `--user-agent <ua>` | 自定义 User-Agent |
| `--proxy <url>` | 代理服务器（含认证格式 `http://user:pass@host:port`） |
| `--proxy-bypass <hosts>` | 代理绕过主机 |
| `--ignore-https-errors` | 忽略 HTTPS 证书错误 |
| `--headers <json>` | HTTP 请求头（作用于 URL 源） |
| `--color-scheme dark\|light` | 颜色方案（v0.26.0 新增） |
| `--engine chrome\|lightpanda` | 浏览器引擎（v0.26.0 新增） |
| `--download-path <path>` | 默认下载目录（v0.26.0 新增） |
| `--confirm-actions <list>` | 需要确认的动作类别（v0.26.0 新增） |
| `--confirm-interactive` | 交互式确认提示（v0.26.0 新增） |
| `--action-policy <path>` | 动作策略 JSON 文件 |
| `--max-output <chars>` | 截断页面输出上限 |
| `--allowed-domains <list>` | 限制导航域名 |
| `--model <name>` | AI chat 模型 |
| `-v, --verbose` | 显示工具命令和原始输出 |
| `-q, --quiet` | 静默模式（仅显示 AI 文本） |
| `--config <path>` | 自定义配置文件 |
| `--debug` | 调试输出 |

---

## Configuration（配置文件）

查找顺序（从低到高）：
1. `~/.agent-browser/config.json`
2. `./agent-browser.json`
3. 环境变量
4. CLI flags

```json
// ~/.agent-browser/config.json 示例
{
  "headed": true,
  "proxy": "http://localhost:8080",
  "profile": "./browser-data",
  "color-scheme": "dark"
}
```

---

## 环境变量速查

```bash
AGENT_BROWSER_SESSION_NAME=myapp           # 自动状态持久化
AGENT_BROWSER_ENCRYPTION_KEY=<64hex>       # 状态加密
AGENT_BROWSER_STATE_EXPIRE_DAYS=30         # 状态过期天数
AGENT_BROWSER_HEADED=1                     # 显示浏览器
AGENT_BROWSER_PROXY=http://host:port        # 代理
AGENT_BROWSER_USER_AGENT=<ua>              # User-Agent
AGENT_BROWSER_AUTO_CONNECT=1               # 自动连接 Chrome
AGENT_BROWSER_EXECUTABLE_PATH=<path>       # 自定义浏览器
AGENT_BROWSER_DOWNLOAD_PATH=<path>         # 下载目录
AGENT_BROWSER_COLOR_SCHEME=dark            # 颜色方案
AGENT_BROWSER_ENGINE=lightpanda            # 浏览器引擎
AI_GATEWAY_API_KEY=<key>                   # AI Gateway（启用 chat 命令）
AI_GATEWAY_MODEL=<model>                  # AI chat 默认模型
```

---

## 认知负荷预算

执行 browser 任务前评估：
- 页面复杂度 > 20 个动态元素 → 先 `snapshot -i` 再决定下一步
- 多步骤流程 → 优先用 `batch` 合并命令减少进程开销
- 需要 AI 判断时 → `chat` 单次指令更高效

---

## 已知陷阱

1. **hermes-agent 捆绑旧版**：升级 hermes-agent 的 `node_modules` 后才可用新命令
2. **Tab ID 格式**：用 `t1`, `t2`（带 `t` 前缀），不能用裸数字
3. **batch 中断**：默认遇错继续，加 `--bail` 停止
4. **chat 需要 AI Gateway**：需设置 `AI_GATEWAY_API_KEY`
5. **har 录制**：需指定路径 `har start /tmp/capture.har`
6. **session-name vs session**：`session-name` 自动持久化，`session` 仅当前进程
7. **fill vs type**：`fill` 会先清空字段，`type` 追加输入

---

## Source

- **CLI**: [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) (Apache-2.0)
- **Skill issues**: [TheSethRose/Agent-Browser-CLI](https://github.com/TheSethRose/Agent-Browser-CLI)
