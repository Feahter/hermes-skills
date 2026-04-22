## 失败处理（Best Practices）

### 常见失败原因及对策

#### 1. 权限被拒绝（Permission denied）

```
症状：bypassPermissions 仍然被拒绝
原因：目录不在信任列表中
解决：
  - 确认 PROJECT_DIR 在 ~/project/ 或 /tmp/
  - 或手动 chmod +x 需要的脚本
  - 或在终端先手动 claude 确认一次
```

#### 2. 进程卡住（不输出也不结束）

```
症状：session 一直处于 running 状态
原因：
  - AI 在等待某个输入
  - 网络问题导致 API 无响应
  - 进入了需要确认的死循环

处理流程：
  1. 查看实时日志：
     tail -f $SKILL_DIR/.state/logs/<session_id>.log
  2. 检查进程：
     ps aux | grep claude
  3. 手动发信号终止：
     kill -9 $(cat $SKILL_DIR/.state/pids/<session_id>.pid)
  4. 将状态标记为 failed：
     echo '{"status":"failed","reason":"timeout_killed"}' \
       > $SKILL_DIR/.state/progress/<session_id>.json
  5. 分析日志找原因，重试
```

#### 3. 依赖安装失败

```
症状：npm install / pip install 报错
常见原因：
  - 网络问题（国内访问 npm/pypi 慢）
  - 版本冲突
  - 权限问题

解决：
  1. 先检查是否有网络问题：
     npm install --registry https://registry.npmmirror.com
  2. 检查 package.json 语法
  3. 删除 node_modules 重新安装
  4. 手动在项目目录运行一次，确认可以成功
```

#### 4. 测试失败（AI 写的代码跑不通测试）

```
这是正常情况，需要多轮修正：

1. 查看测试输出：
   cd $PROJECT_DIR && npm test

2. 定位失败原因：
   - 语法错误 → AI 漏看了
   - 逻辑错误 → AI 的实现思路不对
   - 测试本身写错了 → 测试需要修正

3. 启动子 session 修正：
   sessions_spawn(
     task="测试失败了，以下是测试输出：
     [粘贴测试输出]
     
     请：
     1. 分析失败原因
     2. 修正代码
     3. 重新运行测试
     4. 直到全部通过",
     runtime="subagent",
     mode="session"
   )
```

#### 5. Git 冲突或脏状态

```
症状：AI 提交失败 / diff 异常
解决：
  1. 检查 git 状态：
     cd $PROJECT_DIR && git status
  2. 处理冲突或 stash
  3. 重试任务
```

### 自动重试机制

对于非致命错误，建议自动重试：

```bash
MAX_RETRIES=3
RETRY_DELAY=10

for i in $(seq 1 $MAX_RETRIES); do
  echo "Attempt $i of $MAX_RETRIES"
  bash $SKILL_DIR/pipeline/run-task.sh "$TASK" "$PROJECT_DIR"
  
  # 检查结果
  STATUS=$(cat $SKILL_DIR/.state/progress/<session_id>.json | jq -r '.status')
  if [ "$STATUS" = "completed" ]; then
    echo "Success!"
    break
  elif [ "$STATUS" = "failed" ]; then
    REASON=$(cat $SKILL_DIR/.state/progress/<session_id>.json | jq -r '.reason // "unknown"')
    if [ "$REASON" = "timeout" ] || [ "$REASON" = "network" ]; then
      echo "Retrying after $RETRY_DELAY seconds..."
      sleep $RETRY_DELAY
      RETRY_DELAY=$((RETRY_DELAY * 2))
    else
      echo "Non-retryable failure: $REASON"
      break
    fi
  fi
done
```

---

