## 使用示例

### 示例 1: 完整自动化

**用户输入:**
> "帮我分析这个 sales.csv，生成趋势图，并导出为 PDF 报告"

**系统自动执行:**
1. **解析需求:**
   - 读取 CSV → 需要 `xlsx` skill
   - 数据分析 → 内置能力
   - 生成图表 → 需要 `canvas-design` skill
   - 导出 PDF → 需要 `pdf` skill

2. **检查技能:**
   ```bash
   ls skills/ | grep -E "xlsx|canvas|pdf"
   # 发现 xlsx 已安装
   # 发现 canvas-design 缺失
   # 发现 pdf 缺失
   ```

3. **自动安装（使用 skillhub_install 工具）:**
   ```python
   # 工具自动处理环境检测、依赖安装、CLI 安装
   skillhub_install(action="install_skill", skillName="canvas-design")
   skillhub_install(action="install_skill", skillName="pdf")
   ```

4. **选择模型:**
   - 当前模型: kimi-coding/k2p5 ✓ 正常
   - 决策: 使用当前模型

5. **执行子任务:**
   - 使用 `xlsx` 读取 CSV
   - 使用 `canvas-design` 生成图表
   - 使用 `pdf` 导出报告

6. **输出结果:**
   - 返回 PDF 文件路径
   - 提供数据分析摘要

### 示例 2: 模型降级

**场景:** 当前模型限速

**系统自动处理:**
```python
# 检测到限速
if rate_limited(current_model):
    # 切换到备用模型
    fallback_model = get_available_model()
    spawn_task(task, model=fallback_model)
```

### 示例 3: 错误处理

**场景:** 技能安装失败

**系统自动处理:**
```python
try:
    skillhub_install(action="install_skill", skillName="pdf")
except NetworkTimeout:
    # 重试 3 次，指数退避
    retry_with_backoff(max_attempts=3)
except SkillNotFound:
    # 推荐替代方案
    suggest("可以使用内置 PDF 能力，或手动从 GitHub 安装")
```

