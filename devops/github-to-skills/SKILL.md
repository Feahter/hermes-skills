---
name: github-to-skills
description: GitHub 操作中心：转换仓库为 Skills + gh CLI 操作。触发场景：(1) 打包 GitHub 仓库为 Skill (2) GitHub PR/CI/API 操作 (3) 检查更新、列出/删除 Skills。
---

# GitHub 操作中心

GitHub 相关操作的全能工具箱。

## Part A: GitHub 转 Skills 工厂

自动将 GitHub 仓库转换为 Hermes-native Skills。

### ⚠️ 关键陷阱：生态不兼容

**`npx skills add` 绝不用于 Hermes 安装。**

`npx skills add`（vercel-labs/skills CLI）安装到以下生态，**不是 Hermes**：
- Claude Code → `~/.claude/skills/`
- OpenClaw → `~/.openclaw/skills/`
- OpenCode → `.opencode/skills/` 或 `~/.config/opencode/skills/`

Hermes 使用自己的 `SKILL.md` 格式，位于 `~/.hermes/skills/<category>/`。必须手动从 GitHub 构建。

### 核心功能

1. **分析**：获取仓库元数据（描述、README、最新 commit hash）
2. **脚手架**：创建标准化 Skill 目录结构
3. **内容获取**：从 raw.githubusercontent.com 读取真实 SKILL.md 内容
4. **格式转换**：适配 Hermes YAML frontmatter 格式

### 使用方式

**触发**：`/github-to-skills <github_url>` 或 "把这个仓库打包成 Skill: <url>"

### 工作流程

1. **分析仓库结构**：读 README，确认是否有 `SKILL.md`（Agent Skills 标准格式）
2. **定位内容**：
   - 标准路径：`/tree/main/<skill-name>/SKILL.md`
   - Raw URL：`https://raw.githubusercontent.com/<owner>/<repo>/main/<skill-name>/SKILL.md`
   - MD branch：`https://raw.githubusercontent.com/<owner>/<repo>/md/<skill-name>/SKILL.md`
3. **提取内容**：用 `web_extract` 读 raw Markdown
4. **判断子集**：如果 repo 是多 Skill 合集，只提取需要的那几个
5. **创建目录**：`mkdir -p ~/.hermes/skills/<category>/<skill-name>`
6. **写入 SKILL.md**：确保有正确的 YAML frontmatter
7. **重建 registry**：`python3 ~/.hermes/scripts/skill_registry.py`
8. **验证**：`ls ~/.hermes/skills/` 确认出现

### Hermes Skill 元数据 Schema

```yaml
---
name: <kebab-case>
description: <简洁描述，触发词在前>
category: <ai-agent|creative|research|...>
---
```

**name** 用 kebab-case，**description** 包含触发词（用户可能说的话），**category** 对应 `~/.hermes/skills/` 下的子目录。

### 常用 category 映射

| 内容类型 | category |
|---------|----------|
| 思维/认知/推理框架 | `thinking` |
| 写作/内容创作 | `creative` |
| 深度调研/竞品分析 | `research` |
| 工程化/SOP/测试 | `software-development` |
| 知识管理/笔记 | `note-taking` |
| 前端/设计/可视化 | `media` |

---

## Part B: GitHub CLI 操作（gh）

使用 `gh` CLI 与 GitHub 交互。

### 使用原则

- 不在 git 目录时，**必须**用 `--repo owner/repo` 指定仓库
- 或直接使用 URL

### Pull Requests

| 操作 | 命令 |
|------|------|
| 检查 PR CI 状态 | `gh pr checks <PR号> --repo owner/repo` |
| 列出最近 workflow | `gh run list --repo owner/repo --limit 10` |
| 查看运行详情 | `gh run view <run-id> --repo owner/repo` |
| 查看失败日志 | `gh run view <run-id> --repo owner/repo --log-failed` |

### API 高级查询

使用 `gh api` 获取其他子命令不支持的数据：

```bash
# 获取 PR 特定字段
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'

# 列出 issues
gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'
```

### JSON 输出

大多数命令支持 `--json` 结构化输出，用 `--jq` 过滤：

```bash
gh issue list --repo owner/repo --json state,title --jq '.[] | select(.state == "open")'
```

---

## 脚本工具

| 脚本 | 用途 |
|------|------|
| `scripts/fetch_github_info.py` | 获取仓库信息（README、hash） |
| `scripts/scan_and_check.py` | 检查 Skills 更新（来自 skill-manager） |
| `scripts/list_skills.py` | 列出所有 Skills |

---

## 与其他 Skill 配合

| 场景 | 工作流 |
|------|--------|
| 创建 Skill | `github-to-skills` → 安装 |
| 检查更新 | `skill-manager check` |
| 持续改进 | `skill-evolution-manager` |

---

## 注意事项

- 确保 `gh` CLI 已安装且认证
- 确保 Git 可用（用于获取 commit hash）
- 操作前确认仓库路径正确
