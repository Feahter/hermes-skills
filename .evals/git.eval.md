# git.evals

> Skill: git
> Description: Git workflow best practices and safety rules. Use when working with git operations, committing code, resolving merge conflicts, pushing branches, or need guidance on proper git hygiene.
> Last updated: 2026-05-13

---

## POSITIVE — 应该触发

| # | 触发词 | 预期行为 | 边界条件 |
|---|--------|----------|----------|
| P1 | "帮我提交这个改动" | 触发 git | commit 是核心场景 |
| P2 | "怎么解决合并冲突" | 触发 git | merge conflict 是关键场景 |
| P3 | "创建一个新分支" | 触发 git | 分支操作 |
| P4 | "查看最近的提交记录" | 触发 git | log 也是 git 核心 |
| P5 | "怎么撤销上一次提交" | 触发 git | revert/reset 是危险操作需要指导 |
| P6 | "帮我推送代码到远程" | 触发 git | push 操作 |

---

## NEGATIVE — 不应触发

| # | 触发词 | 不触发原因 | 正确路由 |
|---|--------|------------|----------|
| N1 | "git 是什么" | 查概念不需要操作 | 无需 skill |
| N2 | "帮我写代码" | 代码任务不是 git | coding-agent |
| N3 | "告诉我这个项目的架构" | 架构分析不是 git 操作 | 直接回答或 deep-research |
| N4 | "帮我审查这段代码" | Code review 不是 git 操作 | code-review-expert |

---

## BOUNDARY — 边界情况

| # | 触发词 | 边界描述 | 预期行为 |
|---|--------|----------|----------|
| B1 | "帮我 git commit" | 大小写混用 | 触发但忽略大小写 |
| B2 | "git rebase 和 git merge 有什么区别" | 概念问题 | 不触发，需要解释而非操作 |
| B3 | "强制推送会丢失代码吗" | 危险操作询问 | 不触发，但需要 git 知识回答 |
| B4 | "帮我 git stash 然后切换分支再恢复" | 复杂组合操作 | 触发，解析为多个操作序列 |