## 结果验证（Standard Procedure）

### 验证清单（必须逐项检查）

```bash
# 基础检查：文件是否被创建/修改
cd $PROJECT_DIR
git status

# 检查改动范围
git diff --stat

# 检查具体改动内容
git diff

# 语言/框架特定检查
```

### 按项目类型的验证重点

#### Node.js / npm 项目

```bash
# 1. 检查 package.json 是否更新
cat package.json | jq '.dependencies, .devDependencies'

# 2. 检查依赖是否安装
ls node_modules/.package-lock.json 2>/dev/null && echo "deps installed"

# 3. 运行测试
npm test

# 4. 检查语法（可选）
node --check src/index.js 2>&1 | head -20
```

#### Python 项目

```bash
# 1. 检查 requirements.txt / pyproject.toml
cat requirements.txt 2>/dev/null || cat pyproject.toml 2>/dev/null | head -30

# 2. 检查语法
python -m py_compile src/*.py

# 3. 运行测试
pytest tests/ -v 2>&1 | tail -30

# 4. 检查虚拟环境（如果有）
[ -f venv/bin/activate ] && echo "venv found"
```

#### Rust 项目

```bash
# 1. 检查 Cargo.toml
cat Cargo.toml

# 2. 运行 cargo check
cargo check 2>&1 | tail -20

# 3. 运行测试
cargo test 2>&1 | tail -30

# 4. 编译（release 模式）
cargo build --release 2>&1 | tail -10
```

#### Go 项目

```bash
# 1. 检查 go.mod
cat go.mod

# 2. 运行 go vet
go vet ./...

# 3. 运行测试
go test -v ./... 2>&1 | tail -30

# 4. 尝试构建
go build -o output ./...
```

### 自动验证脚本

```bash
# 使用 verify.sh（已在 pipeline 中）
bash $SKILL_DIR/pipeline/verify.sh <session_id>

# 验证后会输出类似：
# {
#   "session_id": "1745112345-12345",
#   "git_diff": { "files_changed": 5, "additions": 120, "deletions": 10 },
#   "tests_passed": true,
#   "syntax_ok": true,
#   "warnings": []
# }
```

### 验证通过标准

以下全部满足才算验证通过：

- [ ] `git diff` 显示有实际代码改动（不只是格式调整）
- [ ] 新增/修改的文件语法正确
- [ ] 依赖正确添加到 package.json / requirements.txt 等
- [ ] 运行 `npm test` / `pytest` 等测试（如果项目有测试）
- [ ] 测试通过（如果项目有测试）
- [ ] 没有引入明显的安全问题（如 hardcode 密码等）

### 验证失败的处理

```bash
# 1. 收集失败信息
cat $SKILL_DIR/.state/results/<session_id>.json | jq '.errors'

# 2. 分类问题
# - 语法错误 → 需要重新调用 AI 修复
# - 测试失败 → 需要修正逻辑
# - 依赖问题 → 手动安装或修正 package.json

# 3. 启动修正 session
sessions_spawn(
  task="验证失败了，以下是失败信息：
  [粘贴失败信息]
  
  请修复问题并重新验证。",
  runtime="subagent",
  mode="session"
)
```

---

