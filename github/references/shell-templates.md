
所有操作速查以 bash 为主要示例格式。PowerShell 转换遵循以下统一规则，不在每个接口处重复说明。

### 6.1 基础结构对比表

| 要素 | bash | PowerShell |
|------|------|------------|
| Token 获取 | `$(bash '<SCRIPT_PATH>/get-token.sh')` 内联在命令中 | `$token = & "<SCRIPT_PATH>\get-token.ps1"` 先获取再引用 `$token` |
| GET 请求 | `curl -s "URL" -H "Key: Value"` | `irm "URL" -Headers @{"Key"="Value"}` |
| POST/PATCH/PUT 请求 | `curl -s -X METHOD "URL" -H "..." -d '{...}'` | `$body = @{...} \| ConvertTo-Json -Depth 10; irm "URL" -Method Method -Headers @{...} -ContentType "application/json" -Body $body` |
| DELETE 请求 | `curl -s -X DELETE "URL" -H "..."` | `irm "URL" -Method Delete -Headers @{...}` |
| 文件上传（binary） | `curl -s -X POST "URL" -H "Content-Type: ..." --data-binary @path` | `curl.exe -s -X POST "URL" -H "..." --data-binary @path`（irm 不便处理 binary upload） |
| 续行符 | `\` | `` ` ``（反引号） |
| Header 格式 | `-H "Key: Value"` | `-Headers @{"Key"="Value"}` |

### 6.2 完整模板

**bash 模板**
```bash
# GET 请求模板
curl -s "https://api.github.com/{{PATH}}" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"

# POST/PATCH/PUT 请求模板
curl -s -X {{METHOD}} "https://api.github.com/{{PATH}}" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d '{{BODY}}'

# DELETE 请求模板
curl -s -X DELETE "https://api.github.com/{{PATH}}" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Accept: application/vnd.github+json"
```

**PowerShell 模板**
```powershell
# GET 请求模板
$token = & "<SCRIPT_PATH>\get-token.ps1"
irm "https://api.github.com/{{PATH}}" `
  -Headers @{"Authorization"="Bearer $token"; "X-GitHub-Api-Version"="2022-11-28"; "Accept"="application/vnd.github+json"}

# POST/PATCH/PUT 请求模板
$token = & "<SCRIPT_PATH>\get-token.ps1"
$body = @{ {{BODY}} } | ConvertTo-Json -Depth 10
irm "https://api.github.com/{{PATH}}" -Method {{METHOD}} `
  -Headers @{"Authorization"="Bearer $token"; "X-GitHub-Api-Version"="2022-11-28"; "Accept"="application/vnd.github+json"} `
  -ContentType "application/json" -Body $body

# DELETE 请求模板
$token = & "<SCRIPT_PATH>\get-token.ps1"
irm "https://api.github.com/{{PATH}}" -Method Delete `
  -Headers @{"Authorization"="Bearer $token"; "X-GitHub-Api-Version"="2022-11-28"; "Accept"="application/vnd.github+json"}
```

### 6.3 转换规则摘要

从 bash 示例转换为 PowerShell 的步骤：

1. **Token**：将 `$(bash '<SCRIPT_PATH>/get-token.sh')` 替换为先执行 `$token = & "<SCRIPT_PATH>\get-token.ps1"` 再在 Header 中使用 `$token`
2. **命令**：将 `curl -s` 替换为 `irm`，`-X METHOD` 替换为 `-Method Method`
3. **Header**：将 `-H "Key: Value"` 替换为 `-Headers @{"Key"="Value"}`
4. **Body**：将 `-d '{...}'` 替换为 `$body = @{...} | ConvertTo-Json -Depth 10` + `-Body $body`
5. **续行**：将 `\` 替换为 `` ` ``；文件上传场景改用 `curl.exe` 而非 `irm`
6. **Accept Header**：始终包含 `Accept: application/vnd.github+json`（GitHub API 推荐）

---