
> 所有示例以 bash 为主。PowerShell 转换规则见 [§6 Shell 格式模板](#6-shell-格式模板)，不在每个接口处重复。
> `<SCRIPT_PATH>` 在初始化阶段替换为本文件所在目录的绝对路径。

---

### Issues 操作（#1-#25）

#### 1. 列出仓库 Issue

`GET repos/{owner}/{repo}/issues`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| owner | path | ✅ | 仓库所有者 |
| repo | path | ✅ | 仓库名 |
| state | query | — | `open`/`closed`/`all`（默认 open） |
| labels | query | — | 逗号分隔的标签名（如 `bug,help wanted`） |
| assignee | query | — | 用户名（`*` = 任何已分配，`none` = 未分配） |
| sort | query | — | `created`/`updated`/`comments`（默认 created） |
| direction | query | — | `asc`/`desc`（默认 desc） |
| per_page | query | — | 每页数量（**强制使用 100**） |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/issues?state=open&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> **注意**：此接口同时返回 Issue 和 PR。纯 Issue 过滤：排除含 `pull_request` 字段的项。

#### 2. 获取 Issue

`GET repos/{owner}/{repo}/issues/{issue_number}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| owner | path | ✅ | 仓库所有者 |
| repo | path | ✅ | 仓库名 |
| issue_number | path | ✅ | Issue 编号 |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/issues/ISSUE_NUMBER" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 3. 创建 Issue

`POST repos/{owner}/{repo}/issues`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| owner | path | ✅ | 仓库所有者 |
| repo | path | ✅ | 仓库名 |
| title | body | ✅ | Issue 标题 |
| body | body | — | Issue 内容（Markdown） |
| labels | body | — | 标签数组 `["bug","help wanted"]` |
| assignees | body | — | 分配人数组 `["user1"]` |
| milestone | body | — | 里程碑编号（整数） |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/issues" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Issue 标题",
    "body": "Issue 描述内容",
    "labels": ["bug"],
    "assignees": ["username"]
  }'
```

#### 4. 更新 Issue

`PATCH repos/{owner}/{repo}/issues/{issue_number}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| issue_number | path | ✅ | Issue 编号 |
| title | body | — | 新标题 |
| body | body | — | 新内容 |
| state | body | — | `open`/`closed` |
| state_reason | body | — | `completed`/`not_planned`/`reopened` |
| labels | body | — | 替换全部标签 |
| assignees | body | — | 替换全部分配人 |

```bash
curl -s -X PATCH "https://api.github.com/repos/OWNER/REPO/issues/ISSUE_NUMBER" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"state": "closed", "state_reason": "completed"}'
```

#### 5. 锁定 Issue

`PUT repos/{owner}/{repo}/issues/{issue_number}/lock`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| lock_reason | body | — | `off-topic`/`too heated`/`resolved`/`spam` |

```bash
curl -s -X PUT "https://api.github.com/repos/OWNER/REPO/issues/ISSUE_NUMBER/lock" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"lock_reason": "resolved"}'
```

#### 9. 创建 Issue 评论

`POST repos/{owner}/{repo}/issues/{issue_number}/comments`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| issue_number | path | ✅ | Issue 编号（也适用于 PR 编号） |
| body | body | ✅ | 评论内容（Markdown） |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/issues/ISSUE_NUMBER/comments" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"body": "评论内容"}'
```

#### 14. 创建标签

`POST repos/{owner}/{repo}/labels`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| name | body | ✅ | 标签名 |
| color | body | ✅ | 颜色（6 位 hex，不带 #，如 `ff0000`） |
| description | body | — | 标签描述 |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/labels" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"name": "priority-high", "color": "ff0000", "description": "高优先级"}'
```

#### 18. 添加 Issue 标签

`POST repos/{owner}/{repo}/issues/{issue_number}/labels`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| labels | body | ✅ | 标签名数组 `["bug","help wanted"]` |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/issues/ISSUE_NUMBER/labels" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"labels": ["bug", "help wanted"]}'
```

#### 21. 添加 Assignees

`POST repos/{owner}/{repo}/issues/{issue_number}/assignees`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| assignees | body | ✅ | 用户名数组 `["user1","user2"]` |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/issues/ISSUE_NUMBER/assignees" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"assignees": ["username"]}'
```

---

### Pull Requests 操作（#26-#45）

#### 26. 列出 PR

`GET repos/{owner}/{repo}/pulls`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| state | query | — | `open`/`closed`/`all`（默认 open） |
| head | query | — | 过滤源分支（格式 `user:branch`） |
| base | query | — | 过滤目标分支 |
| sort | query | — | `created`/`updated`/`popularity`/`long-running` |
| per_page | query | — | 每页数量（**强制使用 100**） |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/pulls?state=open&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 27. 获取 PR

`GET repos/{owner}/{repo}/pulls/{pull_number}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| pull_number | path | ✅ | PR 编号 |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/pulls/PULL_NUMBER" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> 返回 `mergeable`（bool/null）和 `mergeable_state`（"clean"/"dirty"/"blocked"/"behind"/"unknown"）。`mergeable` 为 null 表示 GitHub 正在计算，需等待重试。

#### 28. 创建 PR

`POST repos/{owner}/{repo}/pulls`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| title | body | ✅ | PR 标题 |
| head | body | ✅ | 源分支（或 `user:branch` 跨 fork） |
| base | body | ✅ | 目标分支 |
| body | body | — | PR 描述（Markdown） |
| draft | body | — | 是否为草稿 PR |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/pulls" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "PR 标题",
    "head": "feature-branch",
    "base": "main",
    "body": "PR 描述"
  }'
```

#### 30. 合并 PR ⚠️ DESTRUCTIVE

`PUT repos/{owner}/{repo}/pulls/{pull_number}/merge`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| commit_title | body | — | 合并 commit 标题 |
| commit_message | body | — | 合并 commit 描述 |
| merge_method | body | — | `merge`/`squash`/`rebase` |
| sha | body | — | PR HEAD SHA（确保合并时 PR 未变更） |

```bash
curl -s -X PUT "https://api.github.com/repos/OWNER/REPO/pulls/PULL_NUMBER/merge" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"merge_method": "squash", "commit_title": "feat: 新功能"}'
```

#### 31. 列出 PR 文件

`GET repos/{owner}/{repo}/pulls/{pull_number}/files`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| per_page | query | — | 每页数量（**强制使用 100**） |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/pulls/PULL_NUMBER/files?per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 38. 创建 PR Review

`POST repos/{owner}/{repo}/pulls/{pull_number}/reviews`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| event | body | ✅ | `APPROVE`/`REQUEST_CHANGES`/`COMMENT` |
| body | body | — | Review 总结评论 |
| comments | body | — | 行内评论数组 |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/pulls/PULL_NUMBER/reviews" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"event": "APPROVE", "body": "LGTM!"}'
```

#### 42. 请求 Review

`POST repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| reviewers | body | — | 用户名数组 |
| team_reviewers | body | — | 团队 slug 数组 |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/pulls/PULL_NUMBER/requested_reviewers" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"reviewers": ["reviewer-username"]}'
```

---

### Repos 操作（#46-#83）

#### 46. 获取仓库

`GET repos/{owner}/{repo}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| owner | path | ✅ | 仓库所有者 |
| repo | path | ✅ | 仓库名 |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 49. 创建仓库

`POST user/repos`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| name | body | ✅ | 仓库名 |
| description | body | — | 仓库描述 |
| private | body | — | 是否私有（默认 false） |
| auto_init | body | — | 是否自动初始化 README |
| gitignore_template | body | — | .gitignore 模板（如 `Go`/`Node`） |
| license_template | body | — | License 模板（如 `mit`/`apache-2.0`） |

```bash
curl -s -X POST "https://api.github.com/user/repos" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-repo",
    "description": "仓库描述",
    "private": false,
    "auto_init": true
  }'
```

#### 53. Fork 仓库

`POST repos/{owner}/{repo}/forks`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| organization | body | — | Fork 到指定组织（默认当前用户） |
| name | body | — | 自定义 Fork 名称 |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/forks" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### 55. 获取文件内容

`GET repos/{owner}/{repo}/contents/{path}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| path | path | ✅ | 文件路径（如 `src/main.go`） |
| ref | query | — | 分支/tag/commit SHA（默认默认分支） |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/contents/README.md" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> 返回 `content`（base64 编码）和 `sha`。解码内容：`echo "$content" | base64 -d`。目录返回文件对象数组。

#### 56. 创建/更新文件

`PUT repos/{owner}/{repo}/contents/{path}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| path | path | ✅ | 文件路径 |
| message | body | ✅ | Commit message |
| content | body | ✅ | base64 编码的文件内容 |
| sha | body | ⚠️ | 更新已有文件时**必填**（从 GET 获取） |
| branch | body | — | 目标分支（默认默认分支） |

```bash
# 更新已有文件（需要 sha）
curl -s -X PUT "https://api.github.com/repos/OWNER/REPO/contents/path/to/file.txt" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "更新文件",
    "content": "SGVsbG8gV29ybGQ=",
    "sha": "CURRENT_FILE_SHA"
  }'
```

#### 61. 列出 Release

`GET repos/{owner}/{repo}/releases`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| per_page | query | — | 每页数量（**强制使用 100**） |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/releases?per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 65. 创建 Release

`POST repos/{owner}/{repo}/releases`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| tag_name | body | ✅ | Tag 名（如 `v1.0.0`） |
| name | body | — | Release 标题 |
| body | body | — | Release 说明（Markdown） |
| draft | body | — | 是否为草稿 |
| prerelease | body | — | 是否为预发布 |
| target_commitish | body | — | 创建 Tag 的目标（branch/SHA） |
| generate_release_notes | body | — | 自动生成 Release Notes |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/releases" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "tag_name": "v1.0.0",
    "name": "Release v1.0.0",
    "body": "## 变更内容\n- 新功能",
    "generate_release_notes": true
  }'
```

#### 69. 上传 Release Asset

`POST uploads.github.com/repos/{owner}/{repo}/releases/{release_id}/assets`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| release_id | path | ✅ | Release ID |
| name | query | ✅ | 文件名 |
| label | query | — | 显示标签 |
| Content-Type | header | ✅ | 文件 MIME 类型 |

```bash
curl -s -X POST "https://uploads.github.com/repos/OWNER/REPO/releases/RELEASE_ID/assets?name=app.zip" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/zip" \
  --data-binary @app.zip
```

> **注意**：域名是 `uploads.github.com`（不是 `api.github.com`），Content-Type 按文件实际类型设置。

---

### Users 操作（#84-#95）

#### 84. 获取认证用户

`GET user`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| — | — | — | 无参数 |

```bash
curl -s "https://api.github.com/user" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 86. 获取用户

`GET users/{username}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| username | path | ✅ | 用户名 |

```bash
curl -s "https://api.github.com/users/USERNAME" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 90. 关注用户

`PUT user/following/{username}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| username | path | ✅ | 要关注的用户名 |

```bash
curl -s -X PUT "https://api.github.com/user/following/USERNAME" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> 成功返回 204（无 body）。

#### 93. 添加 SSH Key

`POST user/keys`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| title | body | ✅ | Key 标题 |
| key | body | ✅ | SSH 公钥内容 |

```bash
curl -s -X POST "https://api.github.com/user/keys" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"title": "My SSH Key", "key": "ssh-ed25519 AAAA..."}'
```

---

### Search 操作（#96-#101）

> **限流提醒**：Search API 独立限流 30 req/min（见 §8.5）。批量搜索时注意间隔。

#### 96. 搜索仓库

`GET search/repositories`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| q | query | ✅ | 搜索查询（支持限定词：`language:go stars:>100 topic:cli`） |
| sort | query | — | `stars`/`forks`/`help-wanted-issues`/`updated` |
| order | query | — | `asc`/`desc` |
| per_page | query | — | 每页数量（最大 100） |

```bash
curl -s "https://api.github.com/search/repositories?q=language:go+stars:>1000&sort=stars&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> 返回 `total_count` + `items` 数组。`items` 中每个对象含 `full_name`、`html_url`、`description` 等。

#### 97. 搜索 Issues/PRs

`GET search/issues`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| q | query | ✅ | 搜索查询（限定词：`is:issue is:open repo:owner/repo label:bug`） |
| sort | query | — | `comments`/`reactions`/`created`/`updated` |
| order | query | — | `asc`/`desc` |
| per_page | query | — | 每页数量（最大 100） |

```bash
curl -s "https://api.github.com/search/issues?q=is:issue+is:open+repo:cli/cli+label:bug&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> **常用限定词**：`is:issue`/`is:pr`、`is:open`/`is:closed`、`repo:owner/repo`、`author:user`、`label:name`、`assignee:user`。

#### 98. 搜索代码

`GET search/code`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| q | query | ✅ | 搜索查询（限定词：`filename:*.go repo:owner/repo path:src/`） |
| sort | query | — | `indexed`（按索引日期） |
| order | query | — | `asc`/`desc` |
| per_page | query | — | 每页数量（最大 100） |

```bash
curl -s "https://api.github.com/search/code?q=handleError+repo:cli/cli+filename:*.go&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> 代码搜索**必须**指定 `repo:`、`org:` 或 `user:` 限定词，否则返回 422。

#### 99. 搜索 Commits

`GET search/commits`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| q | query | ✅ | 搜索查询（限定词：`repo:owner/repo author:user`） |
| sort | query | — | `author-date`/`committer-date` |
| per_page | query | — | 每页数量 |

```bash
curl -s "https://api.github.com/search/commits?q=fix+repo:cli/cli&sort=author-date&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 100. 搜索用户

`GET search/users`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| q | query | ✅ | 搜索查询（限定词：`type:user location:china language:go`） |
| sort | query | — | `followers`/`repositories`/`joined` |
| per_page | query | — | 每页数量 |

```bash
curl -s "https://api.github.com/search/users?q=type:user+language:go+followers:>100&sort=followers&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 101. 搜索 Topics

`GET search/topics`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| q | query | ✅ | Topic 名称关键词 |
| per_page | query | — | 每页数量 |

```bash
curl -s "https://api.github.com/search/topics?q=machine-learning&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

---

### Actions 操作（#102-#136）

#### 102. 列出仓库 Workflows

`GET repos/{owner}/{repo}/actions/workflows`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| per_page | query | — | 每页数量（**强制使用 100**） |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/actions/workflows?per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 104. 触发 Workflow ⚠️ DESTRUCTIVE

`POST repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| workflow_id | path | ✅ | Workflow ID 或文件名（如 `ci.yml`） |
| ref | body | ✅ | 目标分支/tag |
| inputs | body | — | Workflow 输入参数（key-value 对象） |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/actions/workflows/ci.yml/dispatches" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"ref": "main", "inputs": {"environment": "staging"}}'
```

> 成功返回 204（无 body）。不返回 run_id，需通过 workflow:trigger-workflow 流程追踪。

#### 105. 列出 Workflow Runs

`GET repos/{owner}/{repo}/actions/runs`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| status | query | — | `completed`/`in_progress`/`queued`/`waiting` 等 |
| branch | query | — | 过滤分支 |
| event | query | — | 触发事件（`push`/`pull_request`/`workflow_dispatch` 等） |
| per_page | query | — | 每页数量（**强制使用 100**） |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/actions/runs?status=completed&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 107. 获取 Run

`GET repos/{owner}/{repo}/actions/runs/{run_id}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| run_id | path | ✅ | Run ID |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/actions/runs/RUN_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> 关键字段：`status`（queued/in_progress/completed）、`conclusion`（success/failure/cancelled/skipped）。

#### 108. 取消 Run

`POST repos/{owner}/{repo}/actions/runs/{run_id}/cancel`

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/actions/runs/RUN_ID/cancel" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 109. 重新运行 Run

`POST repos/{owner}/{repo}/actions/runs/{run_id}/rerun`

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/actions/runs/RUN_ID/rerun" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 114. 列出 Run 的 Jobs

`GET repos/{owner}/{repo}/actions/runs/{run_id}/jobs`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| filter | query | — | `latest`（仅最新尝试）/`all` |
| per_page | query | — | 每页数量 |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/actions/runs/RUN_ID/jobs?per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 120. 下载 Artifact

`GET repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip`

```bash
curl -sL "https://api.github.com/repos/OWNER/REPO/actions/artifacts/ARTIFACT_ID/zip" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -o artifact.zip
```

> 返回 302 重定向到下载 URL，使用 `-L` 跟随重定向。

#### 124. 创建/更新 Secret（需加密）

`PUT repos/{owner}/{repo}/actions/secrets/{secret_name}`

**加密流程**（必须先获取 public key）：

```bash
# 步骤 1：获取仓库 public key
curl -s "https://api.github.com/repos/OWNER/REPO/actions/secrets/public-key" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
# 返回：{"key_id": "...", "key": "base64_public_key"}

# 步骤 2：使用 openssl 加密 Secret（无需 libsodium）
# 注意：GitHub 使用 libsodium sealed box 加密，openssl 不能直接替代
# 推荐方式：使用 Python 或 Node.js 的 tweetnacl 库
python3 -c "
import base64, sys
from nacl.public import SealedBox, PublicKey
public_key = base64.b64decode('BASE64_PUBLIC_KEY')
sealed_box = SealedBox(PublicKey(public_key))
encrypted = sealed_box.encrypt(b'SECRET_VALUE')
print(base64.b64encode(encrypted).decode())
"

# 步骤 3：创建/更新 Secret
curl -s -X PUT "https://api.github.com/repos/OWNER/REPO/actions/secrets/MY_SECRET" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"encrypted_value": "ENCRYPTED_BASE64", "key_id": "KEY_ID"}'
```

> Secret 值必须使用 libsodium sealed box 加密。Python `pynacl` 或 Node.js `tweetnacl` 均可完成。

#### 129. 创建 Variable

`POST repos/{owner}/{repo}/actions/variables`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| name | body | ✅ | Variable 名称 |
| value | body | ✅ | Variable 值（明文） |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/actions/variables" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"name": "ENV_NAME", "value": "production"}'
```

---

### Orgs & Teams 操作（#137-#154）

#### 137. 获取组织

`GET orgs/{org}`

```bash
curl -s "https://api.github.com/orgs/ORG_NAME" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 140. 列出组织成员

`GET orgs/{org}/members`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| role | query | — | `all`/`admin`/`member`（默认 all） |
| per_page | query | — | 每页数量（**强制使用 100**） |

```bash
curl -s "https://api.github.com/orgs/ORG_NAME/members?per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 146. 创建团队

`POST orgs/{org}/teams`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| name | body | ✅ | 团队名称 |
| description | body | — | 团队描述 |
| privacy | body | — | `secret`（仅成员可见）/`closed`（组织内可见） |
| permission | body | — | `pull`/`push`/`admin` |

```bash
curl -s -X POST "https://api.github.com/orgs/ORG_NAME/teams" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"name": "frontend-team", "description": "前端团队", "privacy": "closed"}'
```

#### 150. 添加团队成员

`PUT orgs/{org}/teams/{team_slug}/memberships/{username}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| role | body | — | `member`/`maintainer`（默认 member） |

```bash
curl -s -X PUT "https://api.github.com/orgs/ORG_NAME/teams/TEAM_SLUG/memberships/USERNAME" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"role": "member"}'
```

---

### Commits & Checks 操作（#155-#168）

#### 155. 列出 Commits

`GET repos/{owner}/{repo}/commits`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| sha | query | — | 分支名或 commit SHA |
| path | query | — | 过滤修改了指定路径的 commit |
| author | query | — | 过滤作者（GitHub 用户名或邮箱） |
| since | query | — | 起始时间（ISO 8601） |
| until | query | — | 截止时间（ISO 8601） |
| per_page | query | — | 每页数量（**强制使用 100**） |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/commits?sha=main&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 156. 获取 Commit

`GET repos/{owner}/{repo}/commits/{ref}`

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/commits/COMMIT_SHA" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> 返回 `files` 数组含每个变更文件的 filename/status/additions/deletions/patch。

#### 157. 比较 Commits

`GET repos/{owner}/{repo}/compare/{basehead}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| basehead | path | ✅ | 格式 `base...head`（如 `main...feature`） |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/compare/main...feature-branch" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 160. 列出 Commit 的 Check Runs

`GET repos/{owner}/{repo}/commits/{ref}/check-runs`

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/commits/COMMIT_SHA/check-runs?per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 164. 获取 Combined Status

`GET repos/{owner}/{repo}/commits/{ref}/status`

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/commits/COMMIT_SHA/status" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> 返回 `state`（pending/success/error/failure）和 `statuses` 数组。

#### 166. 创建 Commit Status

`POST repos/{owner}/{repo}/statuses/{sha}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| sha | path | ✅ | Commit SHA |
| state | body | ✅ | `pending`/`success`/`error`/`failure` |
| target_url | body | — | 状态详情链接 |
| description | body | — | 状态描述 |
| context | body | — | 状态上下文标识（如 `ci/build`） |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/statuses/COMMIT_SHA" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "success",
    "target_url": "https://ci.example.com/build/123",
    "description": "Build passed",
    "context": "ci/build"
  }'
```

---

### Activity 操作（#169-#180）

#### 169. 列出通知

`GET notifications`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| all | query | — | `true` 包含已读通知 |
| participating | query | — | `true` 仅参与的 |
| since | query | — | 起始时间（ISO 8601） |
| per_page | query | — | 每页数量（**强制使用 100**） |

```bash
curl -s "https://api.github.com/notifications?all=false&per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 171. 标记通知已读

`PUT notifications`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| last_read_at | body | — | 标记此时间之前的通知为已读（ISO 8601，默认当前时间） |

```bash
curl -s -X PUT "https://api.github.com/notifications" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"last_read_at": "2024-01-01T00:00:00Z"}'
```

#### 175. Star 仓库

`PUT user/starred/{owner}/{repo}`

```bash
curl -s -X PUT "https://api.github.com/user/starred/OWNER/REPO" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> 成功返回 204（无 body）。

#### 177. 列出用户 Starred

`GET users/{username}/starred`

```bash
curl -s "https://api.github.com/users/USERNAME/starred?per_page=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

#### 178. Watch 仓库

`PUT repos/{owner}/{repo}/subscription`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| subscribed | body | — | 是否订阅通知 |
| ignored | body | — | 是否忽略通知 |

```bash
curl -s -X PUT "https://api.github.com/repos/OWNER/REPO/subscription" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"subscribed": true, "ignored": false}'
```

---

### Git Low-level 操作（#181-#190）

#### 181. 创建 Blob

`POST repos/{owner}/{repo}/git/blobs`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| content | body | ✅ | 文件内容 |
| encoding | body | — | `utf-8`（默认）或 `base64` |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/git/blobs" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"content": "文件内容", "encoding": "utf-8"}'
```

#### 183. 创建 Tree

`POST repos/{owner}/{repo}/git/trees`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| tree | body | ✅ | Tree 条目数组 |
| base_tree | body | — | 基础 tree SHA（增量更新时使用） |

每个 tree 条目：

| 字段 | 必填 | 说明 |
|------|------|------|
| path | ✅ | 文件路径 |
| mode | ✅ | `100644`（普通文件）/`100755`（可执行）/`040000`（目录）/`160000`（子模块） |
| type | ✅ | `blob`/`tree`/`commit` |
| sha | ⚠️ | Blob SHA（与 content 二选一） |
| content | ⚠️ | 直接内联内容（与 sha 二选一） |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/git/trees" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "base_tree": "BASE_TREE_SHA",
    "tree": [
      {"path": "src/main.go", "mode": "100644", "type": "blob", "sha": "BLOB_SHA"}
    ]
  }'
```

#### 185. 创建 Commit

`POST repos/{owner}/{repo}/git/commits`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| message | body | ✅ | Commit message |
| tree | body | ✅ | Tree SHA |
| parents | body | ✅ | 父 commit SHA 数组 |
| author | body | — | 作者信息 `{name, email, date}` |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/git/commits" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "feat: 通过 API 创建的 commit",
    "tree": "NEW_TREE_SHA",
    "parents": ["PARENT_COMMIT_SHA"]
  }'
```

#### 187. 获取 Ref

`GET repos/{owner}/{repo}/git/ref/{ref}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| ref | path | ✅ | Ref 路径（如 `heads/main`、`tags/v1.0`） |

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/git/ref/heads/main" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

> 返回 `object.sha` 即为当前分支指向的 commit SHA。

#### 188. 创建 Ref

`POST repos/{owner}/{repo}/git/refs`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| ref | body | ✅ | Ref 全路径（如 `refs/heads/new-branch`） |
| sha | body | ✅ | 指向的 commit SHA |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/git/refs" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"ref": "refs/heads/new-branch", "sha": "COMMIT_SHA"}'
```

#### 189. 更新 Ref

`PATCH repos/{owner}/{repo}/git/refs/{ref}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| ref | path | ✅ | Ref 路径（如 `heads/main`） |
| sha | body | ✅ | 新指向的 commit SHA |
| force | body | — | 是否强制更新（非 fast-forward） |

```bash
curl -s -X PATCH "https://api.github.com/repos/OWNER/REPO/git/refs/heads/main" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{"sha": "NEW_COMMIT_SHA"}'
```

---

### Gists 操作（#191-#198）

#### 193. 创建 Gist

`POST gists`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| files | body | ✅ | 文件对象 `{"filename": {"content": "..."}}` |
| description | body | — | Gist 描述 |
| public | body | — | 是否公开（默认 false） |

```bash
curl -s -X POST "https://api.github.com/gists" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "代码片段",
    "public": false,
    "files": {
      "hello.py": {"content": "print(\"Hello World\")"}
    }
  }'
```

#### 194. 更新 Gist

`PATCH gists/{gist_id}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| files | body | — | 文件变更（content=null 删除文件，新 key 添加文件） |
| description | body | — | 新描述 |

```bash
curl -s -X PATCH "https://api.github.com/gists/GIST_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "files": {
      "hello.py": {"content": "print(\"Updated\")"},
      "new_file.txt": {"content": "新文件内容"}
    }
  }'
```

---

### Deployments 操作（#199-#206）

#### 201. 创建 Deployment

`POST repos/{owner}/{repo}/deployments`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| ref | body | ✅ | 部署的分支/tag/SHA |
| environment | body | — | 环境名（如 `production`/`staging`） |
| description | body | — | 部署描述 |
| auto_merge | body | — | 是否自动合并（默认 true） |
| required_contexts | body | — | 必须通过的状态检查（空数组跳过检查） |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/deployments" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "ref": "main",
    "environment": "production",
    "description": "部署到生产环境",
    "required_contexts": []
  }'
```

#### 205. 创建 Deployment Status

`POST repos/{owner}/{repo}/deployments/{deployment_id}/statuses`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| state | body | ✅ | `error`/`failure`/`inactive`/`in_progress`/`queued`/`pending`/`success` |
| description | body | — | 状态描述 |
| environment_url | body | — | 环境 URL |
| log_url | body | — | 日志 URL |

```bash
curl -s -X POST "https://api.github.com/repos/OWNER/REPO/deployments/DEPLOYMENT_ID/statuses" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "success",
    "description": "部署成功",
    "environment_url": "https://app.example.com"
  }'
```

---