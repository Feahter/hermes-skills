---
name: code-extract
description: 从代码仓库提取泛用价值组件。当用户想深入研究一个项目并析出可复用代码时触发，如"分析这个项目"、"提取代码"、"克隆并研究"、"拆解这个项目"。工作流：克隆仓库 → 并行分析源码 → 识别泛用组件 → 结构化保存（README + Cargo.toml + src/）。
---

# Code Extract

从代码仓库提取泛用价值组件，保存为独立可引用的模块。

## 触发条件

用户说"分析这个项目"、"提取代码"、"克隆并研究"、"拆解这个项目"、"把项目克隆到 X 目录然后析出泛用代码"等类似表述。

## 工作流

### Phase 1: 克隆 + 初步侦察

```bash
mkdir -p ~/project/github ~/project/code
git clone https://github.com/{owner}/{repo}.git ~/project/github/{repo}
```

快速侦察源码结构：
```bash
find ~/project/github/{repo}/src -type f -name "*.rs" | head -50
ls -la ~/project/github/{repo}/src/
```

### Phase 2: 并行源码分析（关键步骤）

使用 `delegate_task` 并行分析多个模块，不要串行读文件：

**分配策略：** 每个 delegate_task 负责一个功能域（如 memory/、auth/、transport/），读取该域所有文件并输出结构摘要。

```
任务1: memory/ 目录 → memory_graph.rs, cache.rs, search.rs, model.rs
任务2: auth/ 目录 → oauth.rs, login_flows.rs  
任务3: transport/ 目录 → unix.rs, mod.rs
任务4: tui/ 目录 → 渲染架构
任务5: tool/ 目录 → 工具调用系统
```

每个 delegate_task 输出：
- 关键 struct 和 pub fn 签名
- 核心设计模式
- 可提取性评估（泛用 vs 专用）
- 建议的输出路径

### Phase 3: 组件识别

从分析结果中识别泛用组件。泛用组件的特征：
- **无项目特有依赖**（不依赖本项目的 internal crate）
- **接口自包含**（输入输出清晰）
- **可独立测试**（不依赖 main app 的全局状态）
- **概念通用**（其他项目也需要的模式）

通常值得提取的类型：
- 缓存策略（LRU、TTL、Write-through）
- 数据结构（Graph、Tree、Ring buffer）
- 网络协议（OAuth、WS、HTTP middleware）
- 压缩/编码（Context compaction、Tokenization）
- 安全模型（Permission tier、Action classification）

不值得提取的：
- 业务逻辑（project-specific domain）
- 直接依赖内部 crate 的代码
- UI/TUI 渲染代码（通常强耦合）

### Phase 4: 批量提取文件

读取每个目标文件的完整内容，使用 `execute_code` Python 批量写入（**重要：** `write_file` 在循环中会丢失 content 参数，必须用 Python）：

```python
# 不要这样做（write_file 会丢失参数）：
for path, content in files.items():
    write_file(path=path, content=content)  # BUG: content 参数丢失

# 正确做法：
for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
```

通过 `execute_code` 调用：
```python
for name, src_path in files.items():
    result = terminal(f"cat {src_path}")
    content = result['output']
    with open(f"{base_dst}/{name}/src/{name}.rs", 'w') as f:
        f.write(content)
```

### Phase 5: 结构化输出

每个组件输出到独立目录：

```
{component}/
├── README.md          # 核心价值 + 架构 + 关键模式 + 泛用评估
├── Cargo.toml         # workspace 成员配置
└── src/
    ├── {component}.rs  # 主要源码
    └── {submodule}.rs  # 可选的子模块
```

**README.md 模板：**
```markdown
# {Component Name} — `{component}/`

## 核心价值
**为什么值得提取：** 一句话说明

## 架构设计
关键数据结构 + 交互关系

## 关键模式
1. 模式名称：简短描述 + 核心代码片段

## 泛用性评估
| 维度 | 评分 | 说明 |
|------|------|------|
| 可移植性 | X/10 | ... |
| 概念通用性 | X/10 | ... |

## 提取来源
`src/{path}.rs` (N行)

## 依赖
```toml
[dependencies]
serde = "1"
```
```

### Phase 6: Workspace 配置

根目录写 `Cargo.toml`（workspace）和 `Cargo.packages.toml`（各包配置）：

```toml
[workspace]
members = ["memory_graph", "embedding", "oauth", ...]
resolver = "2"

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
anyhow = "1"
```

## 关键陷阱

### ⚠️ write_file 参数丢失
`write_file` 在循环/批量调用时会丢失 `content` 参数（tool loop 警告后 context pressure 导致截断）。**必须用 `execute_code` + Python file write** 写大文件（>5KB 或批量写入）。

### ⚠️ 过度提取
不要因为"这段代码写得好"就提取。只提取**其他项目也真正需要**的组件。项目特有业务逻辑不应提取。

### ⚠️ 依赖陷阱
检查提取的代码是否依赖项目内部的 `crate::*`。如果依赖了：
1. 要么把内部依赖也一起提取（但这会产生大量耦合代码）
2. 要么只提取接口和模式，依赖部分留空让使用者自己实现

## 验证步骤

提取完成后验证：
```bash
# 文件存在性
find ~/project/code/{repo}-extract -type f | sort

# 大小合理（通常 50KB-200KB/组件）
du -sh ~/project/code/{repo}-extract/*/

# Workspace 可解析
cd ~/project/code/{repo}-extract && cargo metadata --format-version 1 2>&1 | head -5
```
