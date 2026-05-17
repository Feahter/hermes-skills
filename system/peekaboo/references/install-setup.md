# Peekaboo 安装与权限配置

## 系统要求

| 要求 | 最低版本 |
|------|---------|
| macOS | 15.0 (Sequoia) |
| Swift | 6.2 |
| Node.js | 22+（仅 MCP 模式需要） |

验证当前系统版本：
```bash
sw_vers -buildVersion
# 24A335 = macOS 15.0
# 24Gxxx = macOS 15.x
```

## 安装方式

### Homebrew（推荐）

```bash
# 添加 tap 并安装
brew tap steipete/tap
brew install peekaboo

# 验证安装
peekaboo --version
```

### npm

```bash
npm install -g @steipete/peekaboo
peekaboo --version
```

### 手动下载

```bash
# 下载最新 release
curl -L https://github.com/openclaw/Peekaboo/releases/latest/download/peekaboo-macos.zip -o peekaboo.zip
unzip peekaboo.zip
mv peekaboo /usr/local/bin/
chmod +x /usr/local/bin/peekaboo
```

## 权限配置

### 必须的权限

1. **Screen Recording** — 截图能力
2. **Accessibility** — UI 元素访问、输入模拟

### 检查权限状态

```bash
peekaboo permissions status
```

输出示例：
```
Screen Recording: ❌ Not granted
Accessibility:     ❌ Not granted
```

### 授予权限

```bash
# 方式 1：CLI 引导（会自动打开 System Settings）
peekaboo permissions grant

# 方式 2：手动打开
open "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture"
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
```

### 权限生效

授予后可能需要**重启终端**或**重新登录**，Accessibility 权限需要将终端加入辅助功能列表。

## 快速验证

```bash
# 1. 检查权限
peekaboo permissions status

# 2. 列出可见应用（验证截图权限）
peekaboo list apps

# 3. 截图并分析（验证 Screen Recording）
peekaboo image --mode screen --analyze "测试截图"

# 4. 尝试点击（验证 Accessibility）
peekaboo click --on "Apple" --snapshot "$(peekaboo see --mode screen --json | jq -r '.snapshot_id')"
```

## AI Provider 配置

Peekaboo 的 AI 分析功能（`--analyze`、`agent` 模式）需要配置 API key：

```bash
# 交互式配置
peekaboo config add

# 或设置环境变量
export PEEKABOO_AI_PROVIDERS="openai/gpt-4.1,anthropic/claude-sonnet-4"
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-..."
```

## 常见问题

### Q: 提示 "Screen Recording permission denied"
A: 前往 System Settings → Privacy & Security → Screen Recording，将终端应用加入列表。

### Q: `peekaboo see` 返回空元素列表
A: Accessibility 权限未授予，或应用在系统保护下运行。

### Q: macOS 14 或更低版本能用吗？
A: 不能。Peekaboo 强制要求 macOS 15.0+，依赖 Sequoia 的新 Accessibility API。

### Q: Homebrew 安装慢/超时
A: 尝试手动下载 release，或使用 npm：`npm install -g @steipete/peekaboo`
