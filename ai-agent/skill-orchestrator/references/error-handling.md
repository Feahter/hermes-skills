## 错误处理

### 技能安装失败

**常见错误及处理：**

| 错误类型 | 检测方式 | 处理策略 |
|---------|---------|---------|
| 网络超时 | 请求超时 > 30s | 重试 3 次，间隔递增（5s, 10s, 20s） |
| 技能不存在 | 404 响应 | 报告用户，推荐替代技能 |
| 依赖冲突 | 安装报错 | 记录冲突，尝试兼容版本 |
| 权限不足 | EACCES 错误 | 提示用户授权，降级到基础能力 |
| 磁盘空间不足 | ENOSPC 错误 | 清理缓存后重试，失败则报告用户 |

**重试机制：**
```python
def install_skill_with_retry(skill_name: str, max_retries: int = 3) -> bool:
    """带重试的技能安装"""
    for attempt in range(max_retries):
        try:
            result = skillhub_install(action="install_skill", skillName=skill_name)
            if result.success:
                return True
        except NetworkTimeout:
            wait_time = 5 * (2 ** attempt)  # 指数退避
            time.sleep(wait_time)
            continue
        except SkillNotFound:
            log_error(f"技能 {skill_name} 不存在")
            suggest_alternatives(skill_name)
            return False
        except Exception as e:
            log_error(f"安装失败: {e}")
            if attempt == max_retries - 1:
                return False
    return False
```

### 子任务执行失败

**失败处理流程：**

```
子任务失败
    ↓
[1] 记录错误上下文（任务、模型、错误信息）
    ↓
[2] 判断是否可重试
    ↓  是              否
[3] 重试执行    [4] 降级处理
    ↓              ↓
[5] 成功则继续   [6] 报告用户，提供选项
```

**降级策略：**

| 场景 | 降级方案 |
|------|---------|
| 技能调用失败 | 使用内置基础能力 |
| 模型限速 | 切换备用模型 |
| 外部服务不可用 | 使用本地缓存或跳过 |
| 数据格式错误 | 尝试自动修复格式 |

**错误恢复示例：**
```python
def execute_with_fallback(task: dict) -> Result:
    """带降级的任务执行"""
    try:
        return execute_task(task)
    except SkillCallError as e:
        log_warning(f"技能调用失败: {e}")
        # 尝试使用内置能力
        return execute_with_builtin(task)
    except ModelRateLimited:
        # 切换模型重试
        fallback_model = get_fallback_model()
        return execute_task(task, model=fallback_model)
    except Exception as e:
        # 记录完整错误上下文
        error_context = {
            "task": task,
            "error": str(e),
            "timestamp": datetime.now(),
            "stacktrace": traceback.format_exc()
        }
        save_error_context(error_context)
        raise
```

### 重试机制配置

```json
{
  "retry": {
    "max_attempts": 3,
    "backoff_strategy": "exponential",
    "initial_delay_ms": 1000,
    "max_delay_ms": 30000,
    "retryable_errors": [
      "NetworkTimeout",
      "RateLimited",
      "TemporaryUnavailable"
    ]
  }
}
```

