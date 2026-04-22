# 认证与会话管理

浏览器认证方式与会话管理完整参考。

---

## 认证方式总览

| 方式 | 说明 | 复杂度 |
|------|------|--------|
| Session 持久化 | 首次手动登录后自动保存 Cookie/Session | 低 |
| State 文件导入/导出 | 导出的 JSON 文件，支持跨环境 | 低 |
| 表单自动填写 | 用户提供凭据，自动填入表单 | 低 |
| Auth Vault | 加密存储的凭据 | 低 |
| HTTP Basic Auth | 预设凭据 | 低 |
| Cookie 手动注入 | 已知 Cookie 值 | 低 |

---

## 1. Session 持久化

xb 自动为每个浏览器维护独立会话（`xbrowser-cft`、`xbrowser-chrome` 等），Cookie 和 localStorage 在会话间自动保存和恢复。

首次登录后，后续操作无需重新登录：

```bash
# 首次：打开页面并手动登录
xb run open https://app.example.com
# ... 完成登录操作 ...

# 后续：自动恢复登录态
xb run open https://app.example.com
```

---

## 2. State 文件导入/导出

适用于跨环境共享认证状态。

```bash
# 保存当前认证状态（cookies、localStorage 等）
xb run state save ./auth-state.json

# 恢复认证状态
xb run state load ./auth-state.json
```

### 从已登录的浏览器导出 State

适用于需要硬件密钥、短信验证码等复杂登录流程后导出状态：

```bash
# 1. 使用本地浏览器（保留登录态）
xb run --browser chrome open https://app.example.com

# 2. 导出认证状态（此时 Cookie 已在运行时解密）
xb run state save ./auth.json

# 3. 后续在默认浏览器中使用
xb run state load ./auth.json
xb run open https://app.example.com
```

---

## 3. 基本登录流程

标准用户名/密码表单的自动化登录：

```bash
xb run open https://app.example.com/login
xb run wait --load networkidle
xb run snapshot -i
xb run fill @e1 "user@example.com"
xb run fill @e2 "password123"
xb run click @e3
xb run wait --load networkidle
xb run get url  # 验证是否跳转到了目标页面
```

> 元素引用（`@e1`、`@e2`）来自 `snapshot -i` 输出，每次快照后编号可能不同。

---

## 4. OAuth / SSO 流程

处理多次重定向的 OAuth/SSO 登录：

```bash
# 触发 OAuth 登录（浏览器自动跟随重定向链）
xb run open https://app.example.com/auth/google

# 等待回调 URL（支持通配符）
xb run wait --url "https://app.example.com/callback*"

# 保存 OAuth 状态，下次跳过整个 OAuth 流程
xb run state save ./oauth-state.json
```

---

## 5. HTTP Basic Auth

```bash
# 预设凭据，后续请求自动携带 Authorization header
xb run set credentials myuser mypassword
xb run open https://protected.example.com
```

---

## 6. Cookie 手动设置

直接注入 session token 或 cookie：

```bash
xb run cookies set session_id "abc123def456"
xb run cookies set auth_token "eyJhbG..." --domain app.example.com
```

---

## 7. Auth Vault（加密凭据存储）

本地加密存储凭据，避免脚本中明文密码。

```bash
# 保存凭据（交互式输入密码）
xb run auth save my-app --url https://app.example.com --username user@example.com

# 使用凭据自动登录
xb run auth login my-app

# 管理凭据
xb run auth list
xb run auth delete my-app
```

---

## 8. Session 加密

通过 `AGENT_BROWSER_ENCRYPTION_KEY` 环境变量对 session 和 state 文件加密。

```bash
# 生成 64 字符 hex key
openssl rand -hex 32

# 设置加密密钥
export AGENT_BROWSER_ENCRYPTION_KEY="a1b2c3d4e5f6...（64字符hex）"
```

设置后，`state save/load` 和会话持久化数据自动加密/解密。

- 密钥丢失后已加密文件无法恢复
- 建议通过密钥管理工具（1Password CLI、macOS Keychain）管理
- 不同环境使用不同密钥

---

## 9. 安全最佳实践

### State 文件保护

State 文件包含 session token，等同于账号凭证，**绝对不要提交到 git**：

```gitignore
# .gitignore
*.auth.json
auth-state.json
```

### 凭据传递

```bash
# 正确：通过环境变量
xb run fill @e1 "$LOGIN_USER"
xb run fill @e2 "$LOGIN_PASS"

# 错误：硬编码（不要这样做）
xb run fill @e1 "admin@company.com"
xb run fill @e2 "P@ssw0rd!"
```

### 会话清理

```bash
xb run cookies clear
xb cleanup
```

### CI/CD 环境建议

- 每次构建使用独立短期 session，不跨构建持久化
- 通过 CI 密钥管理注入 `AGENT_BROWSER_ENCRYPTION_KEY`
- 构建结束后自动清理 state 文件和 session 数据
- 使用最小权限的专用服务账号
