# GitHub REST API Index (206 Endpoints)

Base URL: `https://api.github.com` | API Version: `2022-11-28` | Accept: `application/vnd.github+json`

### Issues（25 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 1 | 列出仓库 Issue | `GET` | `repos/{owner}/{repo}/issues` | 列出仓库 Issue（含 PR），支持 state/labels/assignee 过滤 |
| 2 | 获取 Issue | `GET` | `repos/{owner}/{repo}/issues/{issue_number}` | 获取单个 Issue 详情 |
| 3 | 创建 Issue | `POST` | `repos/{owner}/{repo}/issues` | 创建新 Issue |
| 4 | 更新 Issue | `PATCH` | `repos/{owner}/{repo}/issues/{issue_number}` | 更新 Issue（标题/内容/状态/标签/分配人） |
| 5 | 锁定 Issue | `PUT` | `repos/{owner}/{repo}/issues/{issue_number}/lock` | 锁定 Issue 讨论 |
| 6 | 解锁 Issue | `DELETE` | `repos/{owner}/{repo}/issues/{issue_number}/lock` | 解锁 Issue 讨论 |
| 7 | 列出 Issue 评论 | `GET` | `repos/{owner}/{repo}/issues/{issue_number}/comments` | 列出 Issue 的所有评论 |
| 8 | 获取 Issue 评论 | `GET` | `repos/{owner}/{repo}/issues/comments/{comment_id}` | 获取单条评论 |
| 9 | 创建 Issue 评论 | `POST` | `repos/{owner}/{repo}/issues/{issue_number}/comments` | 创建评论 |
| 10 | 更新 Issue 评论 | `PATCH` | `repos/{owner}/{repo}/issues/comments/{comment_id}` | 更新评论内容 |
| 11 | 删除 Issue 评论 | `DELETE` | `repos/{owner}/{repo}/issues/comments/{comment_id}` | 删除评论 |
| 12 | 列出仓库标签 | `GET` | `repos/{owner}/{repo}/labels` | 列出仓库所有标签 |
| 13 | 获取标签 | `GET` | `repos/{owner}/{repo}/labels/{name}` | 获取单个标签 |
| 14 | 创建标签 | `POST` | `repos/{owner}/{repo}/labels` | 创建新标签 |
| 15 | 更新标签 | `PATCH` | `repos/{owner}/{repo}/labels/{name}` | 更新标签 |
| 16 | 删除标签 | `DELETE` | `repos/{owner}/{repo}/labels/{name}` | 删除标签 |
| 17 | 列出 Issue 标签 | `GET` | `repos/{owner}/{repo}/issues/{issue_number}/labels` | 列出 Issue 上的标签 |
| 18 | 添加 Issue 标签 | `POST` | `repos/{owner}/{repo}/issues/{issue_number}/labels` | 添加标签到 Issue |
| 19 | 移除 Issue 标签 | `DELETE` | `repos/{owner}/{repo}/issues/{issue_number}/labels/{name}` | 从 Issue 移除标签 |
| 20 | 列出 Assignees | `GET` | `repos/{owner}/{repo}/assignees` | 列出仓库可分配人员 |
| 21 | 添加 Assignees | `POST` | `repos/{owner}/{repo}/issues/{issue_number}/assignees` | 添加分配人到 Issue |
| 22 | 移除 Assignees | `DELETE` | `repos/{owner}/{repo}/issues/{issue_number}/assignees` | 从 Issue 移除分配人 |
| 23 | 列出仓库里程碑 | `GET` | `repos/{owner}/{repo}/milestones` | 列出所有里程碑 |
| 24 | 创建里程碑 | `POST` | `repos/{owner}/{repo}/milestones` | 创建新里程碑 |
| 25 | 更新里程碑 | `PATCH` | `repos/{owner}/{repo}/milestones/{milestone_number}` | 更新里程碑 |

### Pull Requests（20 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 26 | 列出 PR | `GET` | `repos/{owner}/{repo}/pulls` | 列出仓库 PR，支持 state/head/base 过滤 |
| 27 | 获取 PR | `GET` | `repos/{owner}/{repo}/pulls/{pull_number}` | 获取 PR 详情（含 mergeable 状态） |
| 28 | 创建 PR | `POST` | `repos/{owner}/{repo}/pulls` | 创建新 PR |
| 29 | 更新 PR | `PATCH` | `repos/{owner}/{repo}/pulls/{pull_number}` | 更新 PR（标题/内容/状态/base） |
| 30 | 合并 PR ⚠️ | `PUT` | `repos/{owner}/{repo}/pulls/{pull_number}/merge` | 合并 PR（需先检查 mergeable） |
| 31 | 列出 PR 文件 | `GET` | `repos/{owner}/{repo}/pulls/{pull_number}/files` | 列出 PR 变更的文件 |
| 32 | 列出 PR 提交 | `GET` | `repos/{owner}/{repo}/pulls/{pull_number}/commits` | 列出 PR 的所有提交 |
| 33 | 检查 PR 是否已合并 | `GET` | `repos/{owner}/{repo}/pulls/{pull_number}/merge` | 204=已合并, 404=未合并 |
| 34 | 列出 PR 评论 | `GET` | `repos/{owner}/{repo}/pulls/{pull_number}/comments` | 列出 PR review 评论 |
| 35 | 创建 PR 评论 | `POST` | `repos/{owner}/{repo}/pulls/{pull_number}/comments` | 在 PR diff 上创建 review 评论 |
| 36 | 列出 PR Review | `GET` | `repos/{owner}/{repo}/pulls/{pull_number}/reviews` | 列出 PR 的所有 Review |
| 37 | 获取 PR Review | `GET` | `repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}` | 获取 Review 详情 |
| 38 | 创建 PR Review | `POST` | `repos/{owner}/{repo}/pulls/{pull_number}/reviews` | 创建 Review（APPROVE/REQUEST_CHANGES/COMMENT） |
| 39 | 提交 PR Review | `POST` | `repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/events` | 提交待处理的 Review |
| 40 | 删除 PR Review | `DELETE` | `repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}` | 删除待处理的 Review |
| 41 | 列出 Requested Reviewers | `GET` | `repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers` | 列出被请求的审查人 |
| 42 | 请求 Review | `POST` | `repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers` | 请求用户/团队审查 PR |
| 43 | 移除 Review 请求 | `DELETE` | `repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers` | 取消审查请求 |
| 44 | 更新 PR 分支 | `PUT` | `repos/{owner}/{repo}/pulls/{pull_number}/update-branch` | 将 base 分支合并到 PR 分支 |
| 45 | 列出 Issue 评论（PR 用） | `GET` | `repos/{owner}/{repo}/issues/{pull_number}/comments` | PR 的 Issue 级评论（非 diff 评论） |

### Repos（38 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 46 | 获取仓库 | `GET` | `repos/{owner}/{repo}` | 获取仓库详情 |
| 47 | 列出用户仓库 | `GET` | `users/{username}/repos` | 列出指定用户的仓库 |
| 48 | 列出认证用户仓库 | `GET` | `user/repos` | 列出当前认证用户的仓库 |
| 49 | 创建仓库 | `POST` | `user/repos` | 为认证用户创建仓库 |
| 50 | 创建组织仓库 | `POST` | `orgs/{org}/repos` | 为组织创建仓库 |
| 51 | 更新仓库 | `PATCH` | `repos/{owner}/{repo}` | 更新仓库设置 |
| 52 | 删除仓库 ⚠️ | `DELETE` | `repos/{owner}/{repo}` | 删除仓库（不可逆） |
| 53 | Fork 仓库 | `POST` | `repos/{owner}/{repo}/forks` | Fork 仓库到当前用户/组织 |
| 54 | 列出 Fork | `GET` | `repos/{owner}/{repo}/forks` | 列出仓库的 Fork |
| 55 | 获取文件内容 | `GET` | `repos/{owner}/{repo}/contents/{path}` | 获取文件/目录内容（base64 编码） |
| 56 | 创建/更新文件 | `PUT` | `repos/{owner}/{repo}/contents/{path}` | 创建或更新文件（需提供 SHA） |
| 57 | 删除文件 | `DELETE` | `repos/{owner}/{repo}/contents/{path}` | 删除文件（需提供 SHA） |
| 58 | 获取 README | `GET` | `repos/{owner}/{repo}/readme` | 获取仓库 README |
| 59 | 列出分支 | `GET` | `repos/{owner}/{repo}/branches` | 列出仓库分支 |
| 60 | 获取分支 | `GET` | `repos/{owner}/{repo}/branches/{branch}` | 获取分支详情（含保护状态） |
| 61 | 列出 Release | `GET` | `repos/{owner}/{repo}/releases` | 列出仓库 Release |
| 62 | 获取 Release | `GET` | `repos/{owner}/{repo}/releases/{release_id}` | 获取 Release 详情 |
| 63 | 获取最新 Release | `GET` | `repos/{owner}/{repo}/releases/latest` | 获取最新 Release |
| 64 | 按 Tag 获取 Release | `GET` | `repos/{owner}/{repo}/releases/tags/{tag}` | 按 Tag 名获取 Release |
| 65 | 创建 Release | `POST` | `repos/{owner}/{repo}/releases` | 创建新 Release |
| 66 | 更新 Release | `PATCH` | `repos/{owner}/{repo}/releases/{release_id}` | 更新 Release |
| 67 | 删除 Release ⚠️ | `DELETE` | `repos/{owner}/{repo}/releases/{release_id}` | 删除 Release（不可逆） |
| 68 | 列出 Release Assets | `GET` | `repos/{owner}/{repo}/releases/{release_id}/assets` | 列出 Release 附件 |
| 69 | 上传 Release Asset | `POST` | `uploads.github.com/repos/{owner}/{repo}/releases/{release_id}/assets` | 上传附件（Content-Type 按文件类型） |
| 70 | 获取 Release Asset | `GET` | `repos/{owner}/{repo}/releases/assets/{asset_id}` | 获取附件详情 |
| 71 | 删除 Release Asset | `DELETE` | `repos/{owner}/{repo}/releases/assets/{asset_id}` | 删除附件 |
| 72 | 列出协作者 | `GET` | `repos/{owner}/{repo}/collaborators` | 列出仓库协作者 |
| 73 | 添加协作者 | `PUT` | `repos/{owner}/{repo}/collaborators/{username}` | 添加协作者（发送邀请） |
| 74 | 移除协作者 | `DELETE` | `repos/{owner}/{repo}/collaborators/{username}` | 移除协作者 |
| 75 | 列出 Topics | `GET` | `repos/{owner}/{repo}/topics` | 获取仓库 Topic |
| 76 | 替换 Topics | `PUT` | `repos/{owner}/{repo}/topics` | 替换仓库全部 Topic |
| 77 | 列出语言 | `GET` | `repos/{owner}/{repo}/languages` | 获取仓库语言统计 |
| 78 | 列出 Tags | `GET` | `repos/{owner}/{repo}/tags` | 列出仓库 Tag |
| 79 | 获取 License | `GET` | `repos/{owner}/{repo}/license` | 获取仓库 License |
| 80 | 列出 Webhooks | `GET` | `repos/{owner}/{repo}/hooks` | 列出仓库 Webhook |
| 81 | 创建 Webhook | `POST` | `repos/{owner}/{repo}/hooks` | 创建 Webhook |
| 82 | 列出 Deploy Keys | `GET` | `repos/{owner}/{repo}/keys` | 列出仓库部署密钥 |
| 83 | 添加 Deploy Key | `POST` | `repos/{owner}/{repo}/keys` | 添加部署密钥 |

### Users（12 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 84 | 获取认证用户 | `GET` | `user` | 获取当前认证用户信息 |
| 85 | 更新认证用户 | `PATCH` | `user` | 更新认证用户资料 |
| 86 | 获取用户 | `GET` | `users/{username}` | 获取指定用户公开信息 |
| 87 | 列出用户 | `GET` | `users` | 列出所有用户（分页） |
| 88 | 列出关注者 | `GET` | `users/{username}/followers` | 列出用户的关注者 |
| 89 | 列出关注中 | `GET` | `users/{username}/following` | 列出用户关注的人 |
| 90 | 关注用户 | `PUT` | `user/following/{username}` | 关注用户 |
| 91 | 取消关注 | `DELETE` | `user/following/{username}` | 取消关注 |
| 92 | 列出 SSH Key | `GET` | `user/keys` | 列出认证用户 SSH Key |
| 93 | 添加 SSH Key | `POST` | `user/keys` | 添加 SSH Key |
| 94 | 列出邮箱 | `GET` | `user/emails` | 列出认证用户邮箱 |
| 95 | 添加邮箱 | `POST` | `user/emails` | 添加邮箱地址 |

### Search（6 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 96 | 搜索仓库 | `GET` | `search/repositories` | 按条件搜索仓库（q 参数） |
| 97 | 搜索 Issues/PRs | `GET` | `search/issues` | 搜索 Issue 和 PR |
| 98 | 搜索代码 | `GET` | `search/code` | 搜索代码内容 |
| 99 | 搜索 Commits | `GET` | `search/commits` | 搜索 Commit |
| 100 | 搜索用户 | `GET` | `search/users` | 搜索用户 |
| 101 | 搜索 Topics | `GET` | `search/topics` | 搜索 Topic |

### Actions（35 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 102 | 列出仓库 Workflows | `GET` | `repos/{owner}/{repo}/actions/workflows` | 列出仓库所有 Workflow |
| 103 | 获取 Workflow | `GET` | `repos/{owner}/{repo}/actions/workflows/{workflow_id}` | 获取 Workflow 详情（也接受文件名） |
| 104 | 触发 Workflow ⚠️ | `POST` | `repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches` | 手动触发 Workflow |
| 105 | 列出 Workflow Runs | `GET` | `repos/{owner}/{repo}/actions/runs` | 列出仓库所有 Run |
| 106 | 列出 Workflow 的 Runs | `GET` | `repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs` | 列出指定 Workflow 的 Run |
| 107 | 获取 Run | `GET` | `repos/{owner}/{repo}/actions/runs/{run_id}` | 获取 Run 详情 |
| 108 | 取消 Run | `POST` | `repos/{owner}/{repo}/actions/runs/{run_id}/cancel` | 取消正在运行的 Run |
| 109 | 重新运行 Run | `POST` | `repos/{owner}/{repo}/actions/runs/{run_id}/rerun` | 重新运行 Run |
| 110 | 重新运行失败 Jobs | `POST` | `repos/{owner}/{repo}/actions/runs/{run_id}/rerun-failed-jobs` | 仅重新运行失败的 Job |
| 111 | 删除 Run | `DELETE` | `repos/{owner}/{repo}/actions/runs/{run_id}` | 删除 Run 记录 |
| 112 | 下载 Run 日志 | `GET` | `repos/{owner}/{repo}/actions/runs/{run_id}/logs` | 下载 Run 日志（ZIP，302 重定向） |
| 113 | 删除 Run 日志 | `DELETE` | `repos/{owner}/{repo}/actions/runs/{run_id}/logs` | 删除 Run 日志 |
| 114 | 列出 Run 的 Jobs | `GET` | `repos/{owner}/{repo}/actions/runs/{run_id}/jobs` | 列出 Run 中的所有 Job |
| 115 | 获取 Job | `GET` | `repos/{owner}/{repo}/actions/jobs/{job_id}` | 获取 Job 详情（含 steps） |
| 116 | 下载 Job 日志 | `GET` | `repos/{owner}/{repo}/actions/jobs/{job_id}/logs` | 下载 Job 日志（302 重定向） |
| 117 | 列出 Run 的 Artifacts | `GET` | `repos/{owner}/{repo}/actions/runs/{run_id}/artifacts` | 列出 Run 产出的 Artifacts |
| 118 | 列出仓库 Artifacts | `GET` | `repos/{owner}/{repo}/actions/artifacts` | 列出仓库所有 Artifacts |
| 119 | 获取 Artifact | `GET` | `repos/{owner}/{repo}/actions/artifacts/{artifact_id}` | 获取 Artifact 详情 |
| 120 | 下载 Artifact | `GET` | `repos/{owner}/{repo}/actions/artifacts/{artifact_id}/{archive_format}` | 下载 Artifact（ZIP，302 重定向） |
| 121 | 删除 Artifact | `DELETE` | `repos/{owner}/{repo}/actions/artifacts/{artifact_id}` | 删除 Artifact |
| 122 | 列出仓库 Secrets | `GET` | `repos/{owner}/{repo}/actions/secrets` | 列出仓库 Actions Secrets |
| 123 | 获取 Secret | `GET` | `repos/{owner}/{repo}/actions/secrets/{secret_name}` | 获取 Secret 元数据（不含值） |
| 124 | 创建/更新 Secret ⚠️ | `PUT` | `repos/{owner}/{repo}/actions/secrets/{secret_name}` | 创建或更新 Secret（需加密） |
| 125 | 删除 Secret ⚠️ | `DELETE` | `repos/{owner}/{repo}/actions/secrets/{secret_name}` | 删除 Secret |
| 126 | 获取仓库 Public Key | `GET` | `repos/{owner}/{repo}/actions/secrets/public-key` | 获取用于加密 Secret 的公钥 |
| 127 | 列出仓库 Variables | `GET` | `repos/{owner}/{repo}/actions/variables` | 列出仓库 Actions Variables |
| 128 | 获取 Variable | `GET` | `repos/{owner}/{repo}/actions/variables/{name}` | 获取 Variable 值 |
| 129 | 创建 Variable | `POST` | `repos/{owner}/{repo}/actions/variables` | 创建 Variable |
| 130 | 更新 Variable | `PATCH` | `repos/{owner}/{repo}/actions/variables/{name}` | 更新 Variable |
| 131 | 删除 Variable | `DELETE` | `repos/{owner}/{repo}/actions/variables/{name}` | 删除 Variable |
| 132 | 列出 Environment Secrets | `GET` | `repos/{owner}/{repo}/environments/{env}/secrets` | 列出环境 Secrets |
| 133 | 列出 Environment Variables | `GET` | `repos/{owner}/{repo}/environments/{env}/variables` | 列出环境 Variables |
| 134 | 列出仓库 Environments | `GET` | `repos/{owner}/{repo}/environments` | 列出仓库 Environments |
| 135 | 获取 Environment | `GET` | `repos/{owner}/{repo}/environments/{env}` | 获取 Environment 详情 |
| 136 | 创建/更新 Environment | `PUT` | `repos/{owner}/{repo}/environments/{env}` | 创建或更新 Environment |

### Orgs & Teams（18 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 137 | 获取组织 | `GET` | `orgs/{org}` | 获取组织详情 |
| 138 | 更新组织 | `PATCH` | `orgs/{org}` | 更新组织设置 |
| 139 | 列出用户组织 | `GET` | `user/orgs` | 列出认证用户的组织 |
| 140 | 列出组织成员 | `GET` | `orgs/{org}/members` | 列出组织所有成员 |
| 141 | 检查成员 | `GET` | `orgs/{org}/members/{username}` | 检查用户是否为组织成员（204=是，404=否） |
| 142 | 移除成员 | `DELETE` | `orgs/{org}/members/{username}` | 从组织移除成员 |
| 143 | 列出组织仓库 | `GET` | `orgs/{org}/repos` | 列出组织仓库 |
| 144 | 列出团队 | `GET` | `orgs/{org}/teams` | 列出组织所有团队 |
| 145 | 获取团队 | `GET` | `orgs/{org}/teams/{team_slug}` | 获取团队详情 |
| 146 | 创建团队 | `POST` | `orgs/{org}/teams` | 创建新团队 |
| 147 | 更新团队 | `PATCH` | `orgs/{org}/teams/{team_slug}` | 更新团队设置 |
| 148 | 删除团队 | `DELETE` | `orgs/{org}/teams/{team_slug}` | 删除团队 |
| 149 | 列出团队成员 | `GET` | `orgs/{org}/teams/{team_slug}/members` | 列出团队成员 |
| 150 | 添加团队成员 | `PUT` | `orgs/{org}/teams/{team_slug}/memberships/{username}` | 添加团队成员 |
| 151 | 移除团队成员 | `DELETE` | `orgs/{org}/teams/{team_slug}/memberships/{username}` | 移除团队成员 |
| 152 | 列出团队仓库 | `GET` | `orgs/{org}/teams/{team_slug}/repos` | 列出团队管理的仓库 |
| 153 | 添加团队仓库 | `PUT` | `orgs/{org}/teams/{team_slug}/repos/{owner}/{repo}` | 将仓库添加到团队 |
| 154 | 列出组织 Secrets | `GET` | `orgs/{org}/actions/secrets` | 列出组织级 Secrets |

### Commits & Checks（14 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 155 | 列出 Commits | `GET` | `repos/{owner}/{repo}/commits` | 列出仓库 Commit |
| 156 | 获取 Commit | `GET` | `repos/{owner}/{repo}/commits/{ref}` | 获取 Commit 详情（含文件变更） |
| 157 | 比较 Commits | `GET` | `repos/{owner}/{repo}/compare/{basehead}` | 比较两个 Commit（格式 `base...head`） |
| 158 | 列出 Commit 评论 | `GET` | `repos/{owner}/{repo}/commits/{commit_sha}/comments` | 列出 Commit 上的评论 |
| 159 | 创建 Commit 评论 | `POST` | `repos/{owner}/{repo}/commits/{commit_sha}/comments` | 创建 Commit 评论 |
| 160 | 列出 Commit 的 Check Runs | `GET` | `repos/{owner}/{repo}/commits/{ref}/check-runs` | 列出 Commit 的 Check Run |
| 161 | 列出 Commit 的 Check Suites | `GET` | `repos/{owner}/{repo}/commits/{ref}/check-suites` | 列出 Commit 的 Check Suite |
| 162 | 获取 Check Run | `GET` | `repos/{owner}/{repo}/check-runs/{check_run_id}` | 获取 Check Run 详情 |
| 163 | 列出 Check Suite 的 Check Runs | `GET` | `repos/{owner}/{repo}/check-suites/{check_suite_id}/check-runs` | 列出 Check Suite 下的 Run |
| 164 | 获取 Combined Status | `GET` | `repos/{owner}/{repo}/commits/{ref}/status` | 获取 Commit 的综合状态 |
| 165 | 列出 Commit Statuses | `GET` | `repos/{owner}/{repo}/commits/{ref}/statuses` | 列出 Commit 状态（按创建时间） |
| 166 | 创建 Commit Status | `POST` | `repos/{owner}/{repo}/statuses/{sha}` | 创建 Commit 状态 |
| 167 | 列出 PR 的 Commit Statuses | `GET` | `repos/{owner}/{repo}/commits/{ref}/statuses` | 获取 PR HEAD 的状态 |
| 168 | 获取 Check Suite | `GET` | `repos/{owner}/{repo}/check-suites/{check_suite_id}` | 获取 Check Suite 详情 |

### Activity（12 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 169 | 列出通知 | `GET` | `notifications` | 列出认证用户的所有通知 |
| 170 | 列出仓库通知 | `GET` | `repos/{owner}/{repo}/notifications` | 列出指定仓库的通知 |
| 171 | 标记通知已读 | `PUT` | `notifications` | 标记所有通知已读 |
| 172 | 标记仓库通知已读 | `PUT` | `repos/{owner}/{repo}/notifications` | 标记仓库通知已读 |
| 173 | 获取通知线程 | `GET` | `notifications/threads/{thread_id}` | 获取通知线程详情 |
| 174 | 标记线程已读 | `PATCH` | `notifications/threads/{thread_id}` | 标记单个线程已读 |
| 175 | Star 仓库 | `PUT` | `user/starred/{owner}/{repo}` | Star 仓库 |
| 176 | Unstar 仓库 | `DELETE` | `user/starred/{owner}/{repo}` | 取消 Star |
| 177 | 列出用户 Starred | `GET` | `users/{username}/starred` | 列出用户 Star 的仓库 |
| 178 | Watch 仓库 | `PUT` | `repos/{owner}/{repo}/subscription` | Watch 仓库（设置订阅） |
| 179 | 取消 Watch | `DELETE` | `repos/{owner}/{repo}/subscription` | 取消 Watch |
| 180 | 列出仓库 Events | `GET` | `repos/{owner}/{repo}/events` | 列出仓库事件 |

### Git Low-level（10 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 181 | 创建 Blob | `POST` | `repos/{owner}/{repo}/git/blobs` | 创建 Git Blob（文件内容） |
| 182 | 获取 Blob | `GET` | `repos/{owner}/{repo}/git/blobs/{file_sha}` | 获取 Blob 内容 |
| 183 | 创建 Tree | `POST` | `repos/{owner}/{repo}/git/trees` | 创建 Git Tree |
| 184 | 获取 Tree | `GET` | `repos/{owner}/{repo}/git/trees/{tree_sha}` | 获取 Tree |
| 185 | 创建 Commit | `POST` | `repos/{owner}/{repo}/git/commits` | 创建 Git Commit 对象 |
| 186 | 获取 Commit | `GET` | `repos/{owner}/{repo}/git/commits/{commit_sha}` | 获取 Commit 对象 |
| 187 | 获取 Ref | `GET` | `repos/{owner}/{repo}/git/ref/{ref}` | 获取 Git Ref（如 heads/main） |
| 188 | 创建 Ref | `POST` | `repos/{owner}/{repo}/git/refs` | 创建 Ref（branch/tag） |
| 189 | 更新 Ref | `PATCH` | `repos/{owner}/{repo}/git/refs/{ref}` | 更新 Ref（移动指针） |
| 190 | 删除 Ref ⚠️ | `DELETE` | `repos/{owner}/{repo}/git/refs/{ref}` | 删除 Ref（删除分支/tag） |

### Gists（8 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 191 | 列出用户 Gists | `GET` | `gists` | 列出认证用户的 Gist |
| 192 | 获取 Gist | `GET` | `gists/{gist_id}` | 获取 Gist 详情 |
| 193 | 创建 Gist | `POST` | `gists` | 创建新 Gist |
| 194 | 更新 Gist | `PATCH` | `gists/{gist_id}` | 更新 Gist 内容 |
| 195 | 删除 Gist | `DELETE` | `gists/{gist_id}` | 删除 Gist |
| 196 | Star Gist | `PUT` | `gists/{gist_id}/star` | Star Gist |
| 197 | 列出 Gist 评论 | `GET` | `gists/{gist_id}/comments` | 列出 Gist 评论 |
| 198 | 创建 Gist 评论 | `POST` | `gists/{gist_id}/comments` | 创建 Gist 评论 |

### Deployments（8 个端点）

| # | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|
| 199 | 列出 Deployments | `GET` | `repos/{owner}/{repo}/deployments` | 列出仓库 Deployment |
| 200 | 获取 Deployment | `GET` | `repos/{owner}/{repo}/deployments/{deployment_id}` | 获取 Deployment 详情 |
| 201 | 创建 Deployment | `POST` | `repos/{owner}/{repo}/deployments` | 创建 Deployment |
| 202 | 删除 Deployment | `DELETE` | `repos/{owner}/{repo}/deployments/{deployment_id}` | 删除 Deployment |
| 203 | 列出 Deployment Statuses | `GET` | `repos/{owner}/{repo}/deployments/{deployment_id}/statuses` | 列出 Deployment 状态 |
| 204 | 获取 Deployment Status | `GET` | `repos/{owner}/{repo}/deployments/{deployment_id}/statuses/{status_id}` | 获取状态详情 |
| 205 | 创建 Deployment Status | `POST` | `repos/{owner}/{repo}/deployments/{deployment_id}/statuses` | 更新 Deployment 状态 |
| 206 | 列出 Environments | `GET` | `repos/{owner}/{repo}/environments` | 列出仓库 Environments |
