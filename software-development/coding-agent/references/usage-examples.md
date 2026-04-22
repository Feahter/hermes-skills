## 常见使用场景示例

### 场景 1：快速生成一个脚本

**用户说：** "帮我写一个 Python 脚本，监控文件夹变化，有新文件就打印文件名"

**处理：**
```bash
exec workdir:$HOME \
  command:"claude -p 'Write a Python script that monitors a directory for file changes and prints the filename when a new file is created. Use watchdog library. Save to monitor.py' --output-format stream-json --no-session-persistence --permission-mode bypassPermissions"
```

**不需要子 session，简单任务直接执行。**

---

### 场景 2：实现一个完整功能模块

**用户说：** "帮我做一个用户认证模块，用 JWT，包含注册、登录、token 刷新"

**处理：**
```bash
exec workdir:$HOME/project/myapp background:true \
  command:"claude -p '实现用户认证模块：注册、登录、JWT token 刷新。技术栈：Node.js + Express + MongoDB。包含完整验证、中间件、最小测试。' --output-format stream-json --no-session-persistence --permission-mode bypassPermissions"
```

**中等复杂度，可用 exec 背景执行，等待完成。**

---

### 场景 3：大型重构（需要子 session）

**用户说：** "把我们前端的 Redux 状态管理迁移到 Zustand，涉及 50+ 文件"

**处理：**
```bash
sessions_spawn(
  task="## 任务
把 ~/project/frontend/src 下的 Redux 状态管理迁移到 Zustand。

## 技术栈
- React 18
- 当前使用 @reduxjs/toolkit
- 迁移目标：zustand

## 具体要求
1. 分析现有 Redux store 结构
2. 逐步迁移每个模块（保持功能不变）
3. 更新所有 connect() / useSelector() / useDispatch() 调用
4. 移除旧的 Redux 相关代码
5. 运行测试确保功能正常

## 验收标准
- [ ] 所有组件使用 Zustand
- [ ] 测试全部通过
- [ ] 移除 @reduxjs/toolkit 依赖",
  runtime="subagent",
  mode="session"
)
```

---

### 场景 4：调试疑难问题

**用户说：** "这个 API 偶尔会返回 500，但日志里看不出原因"

**处理：**
```bash
sessions_spawn(
  task="## 任务
调试 ~/project/backend/api.py 中的一个偶发性 500 错误。

## 问题描述
- 错误不是每次都发生，大概 10% 概率
- 日志里只有 'Internal Server Error'，没有 stack trace
- 涉及用户并发时更容易出现

## 已尝试
- 检查了数据库连接池（应该够用）
- 查了最近代码改动（没有问题）
- 在本地无法复现

## 要求
1. 添加更详细的错误追踪
2. 找出根本原因
3. 修复并验证",
  runtime="subagent",
  mode="session"
)
```

---

### 场景 5：快速修复 Bug

**用户说：** "帮我修一下这个 bug：登录按钮点了没反应"

**处理：**
```bash
exec workdir:$HOME/project/frontend \
  command:"claude -p '修复登录按钮点击无反应的问题。项目在当前目录，使用 React。检查按钮 onClick 绑定、事件处理函数、是否有条件渲染导致按钮实际被禁用。' --output-format stream-json --no-session-persistence --permission-mode bypassPermissions"
```

**简单 bug 直接修复，不需要子 session。**

---

### 场景 6：初始化新项目

**用户说：** "帮我初始化一个 FastAPI 项目，包含用户认证、数据库连接、RESTful API 结构"

**处理：**
```bash
exec workdir:$HOME/project/myapi background:true \
  command:"claude -p 'Initialize a FastAPI project with:
1. SQLAlchemy + PostgreSQL connection
2. User authentication (JWT)
3. RESTful API structure with routers
4. Docker setup
5. Basic test structure with pytest

Use modern Python best practices. Save to current directory.' --output-format stream-json --no-session-persistence --permission-mode bypassPermissions"
```

---

### 场景 7：自动化脚本

**用户说：** "写个脚本帮我每天自动备份数据库到阿里云 OSS"

**处理：**
```bash
exec workdir:/tmp \
  command:"claude -p 'Write a bash script that:
1. Dumps a PostgreSQL database
2. Uploads the dump to Aliyun OSS using ossutil
3. Keeps only the last 7 days of backups
4. Sends a notification to Slack on failure
5. Has proper error handling and logging

Save as backup.sh and make it executable.' --output-format stream-json --no-session-persistence --permission-mode bypassPermissions"
```

---

