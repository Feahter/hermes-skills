---
name: skill-porting-guide
description: 从 GitHub/Claude Code/Kimi 等平台导入 Skills 到 Hermes 的完整指南。触发：安装这个 skill、帮我装、导入 skill、npx skills add 装不上、从 GitHub 装 skill。
metadata:
  combinator:
    phases: [execution]
    triggers:
      - 安装这个skill
      - 帮我装
      - 导入skill
      - 装不上
      - 从GitHub装skill
      - porting
---

# Skill 跨生态导入指南

当用户分享一个 GitHub 链接或 npm skill 包想让 Hermes 安装时使用。

## 核心原则

**`npx skills add` 在 Hermes 里不工作。** Hermes 有自己原生的 SKILL.md 格式和 skill_manage 系统，独立于 Claude Code/OpenClaw 的 npm-based skills CLI。

## 两种来源的处理方式

### 来源 A：Hermes Skill 链接（Hermes 生态内）

如果 skill 已经托管在 `~/.hermes/skills/` 对应目录，或用户给的是 Hermes-native skill 链接，直接用 `skill_manage` 或 `write_file` 写入对应路径。

### 来源 B：其他生态的 Skill（Claude Code / OpenClaw / Kimi 分享 / npm）

步骤：

1. **识别 skill 目录结构**
   - Claude Code / OpenClaw skills 通常在 `~/.claude/skills/` 或 `~/.openclaw/skills/`
   - Kimi 分享的链接通常指向 GitHub 上的 `SKILL.md` 文件
   - 优先找 `md` branch（Markdown 版本），而非 `org` branch（org-mode 版本）

2. **读取 raw content**
   ```
   https://raw.githubusercontent.com/{owner}/{repo}/main/{skill-name}/SKILL.md
   ```
   GitHub repo 首页通常列出了目录结构，可据此构造 raw URL。

3. **写入 Hermes 目录**
   - 先用 `web_extract` 获取 SKILL.md 全文
   - 用 `write_file` 写入 `~/.hermes/skills/{category}/{skill-name}/SKILL.md`
   - category 根据 skill 用途选择：`creative`/`research`/`thinking`/`productivity` 等

4. **补 `metadata.combinator`（关键！）**
   新 skill 的 SKILL.md frontmatter 必须显式声明 combinator 元数据，否则 skill-combinator 无法精准触发：
   ```yaml
   metadata:
     combinator:
       phases: [analysis]        # generation / execution / validation / integration
       triggers:               # 中文+英文 触发词，精准不冗余
         - 深度研究
         - 竞品分析
         - deep research
   ```

5. **重建 registry**
   ```bash
   python3 ~/.hermes/scripts/skill_registry.py
   ```

6. **验证**
   - 确认 skill 在 registry 中：`python3 -c "import json; r=json.load(open('.skill_registry.json')); print('skill-name' in r.get('skills',{}))"`
   - 可选：用 skill-combinator pipeline 测试召回

## 常见坑

### `npx skills add` 装到了错误位置
- 症状：skill 文件出现在 `~/.claude/skills/` 或其他目录，但 Hermes 加载不到
- 解决：不使用 npx，直接读 raw content，手动写入 `~/.hermes/skills/`

### 新 skill 触发词不精准
- 症状：combinator discover 找不到这个 skill
- 解决：在 SKILL.md frontmatter 补 `metadata.combinator.triggers` 显式声明

### registry 扫描遗漏新 skill
- 检查：`~/.hermes/scripts/skill_registry.py` 有 double-parse bug（每个文件解析两次），不影响结果但有冗余
- 症状：skill 文件存在但 registry 里没有
- 解决：确认 glob 路径覆盖新 skill 所在目录

## registry 路径覆盖范围

当前 `skill_registry.py` glob `~/.hermes/skills/**/*.md`，包含所有子目录。排除以 `.` 开头的目录。

## phases 参考

| phase | 含义 | 典型 skill |
|-------|------|-----------|
| analysis | 分析、诊断、评估 | metacognition-auditor, tacit-mining |
| generation | 生成、写作、创作 | khazix-writer, songwriting |
| execution | 执行、操作 | coding-agent |
| validation | 验证、测试、质检 | test-driven-development |
| planning | 计划、规划、拆解 | plan |
| integration | 组合、编排、协作 | skill-orchestrator |
