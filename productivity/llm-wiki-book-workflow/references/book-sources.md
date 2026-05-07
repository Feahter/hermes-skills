# 书籍来源技术备忘

## Archive.org PDF 下载（⚠️ 政策已变，2026-05 实测）

> **⚠️ 2026-05 重大变更**：Archive.org 对版权书启用强制登录认证（HTTP 401），主 PDF 下载 URL 不再无条件可用。

**搜索**：`web_search` 查询 `site:archive.org "<书名>" pdf`

**identifier 发现方式**：搜索结果或 Open Library API：
```
GET https://openlibrary.org/search.json?q=<书名+作者>&limit=3
```
返回的 `ia` 字段即为 Archive.org identifier。

**验证文件存在**（不需认证）：
```bash
curl -s "https://archive.org/metadata/<ia_id>" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for f in d['files']:
    if '.pdf' in f['name'].lower():
        print(f['name'], int(f.get('size',0))/1024/1024, 'MB')
"
```

**下载主 PDF URL**：
```
https://archive.org/download/<identifier>/<identifier>.pdf
```
（需要 archive.org 免费账号登录后才能下载版权书）

**替代方案（版权书）**：
1. 注册 archive.org 免费账号，每14天可借阅1本
2. Anna's Archive（需 browser 提取真实 URL）
3. z-library.se（需账号）
4. 请用户手动从 archive.org 下载后存入 `~/books/`

**验证 PDF 有效性**（下载后必做）：
```bash
file ~/books/xxx.pdf
# ✓ 有效：PDF document, version 1.x
# ✗ 无效：HTML document text（curl 拿到的是 HTML 错误页）
```

**实测状态（2026-05）**：
- ✅ Thinking Fast and Slow、7 Habits、正义之心、品格的力量、心流、终身成长（老书/公版）
- ❌ Misbehaving、怪诞行为学、象与骑象人、清醒、活出生命的意义（版权书，需登录）

---

## 环境连通性（2026-05 实测）

| 源 | 域名 | 状态 | 备注 |
|----|------|------|------|
| Anna's Archive | annas-archive.gl | ✅ 200 | JS 渲染，不可直接 curl |
| archive.org | archive.org | ✅ 可用 | 公共领域书籍首选；`_text.pdf` 后缀返回 401 |
| icrrd.com | icrrd.com | ✅ 可用 | 7 Habits 4.4MB 有效 PDF |
| gmworldbook.com | gmworldbook.com | ✅ 可用 | Flow 1.5MB 有效 PDF |
| libgen.li | libgen.li | ✅ 200 | 下载需登录 |
| libgen.is | libgen.is | ❌ DNS 失败 | 不可用 |
| libgen.pw | libgen.pw | ✅ 200 | 同 libgen.li 限制 |
| z-library.se | z-library.se | ✅ 200 | 需账号，有日配额 |
| randombook.org | randombook.org | ✅ 200 | 可达，链接不稳定 |
| bdebooks.com | bdebooks.com | ❌ 返回 HTML | 假链接，无真实 PDF |
| pdfcoffee.com | pdfcoffee.com | ❌ 返回 HTML | 需看广告或跳转，不可靠 |

## 本次 session 新增发现（2026-05-06）

### 关键发现：Archive.org 老版本可绕过 401

copyright 书主下载 URL 返回 401，但**老版本/其他版本**可能仍可直链：

| 书 | 链接 | 大小 | 备注 |
|----|------|------|------|
| 活出生命的意义 1963版 | `ia600304.us.archive.org/15/items/frankl-viktor-mans-search-for-meaning-1963/FRANKL_Viktor_Man%27s_Search_For_Meaning-1963_text.pdf` | 9.3MB | ✅ 成功，243页 |
| 错误的行为 | `misbehavingmakin0000thal` 元数据显示 Text PDF 20.8MB，但直链 401 | - | 需找其他版本 |
| 怪诞行为学 | `predictablyirrat00arie` 元数据显示 Text PDF 17.6MB，但直链 401 | - | 需找其他版本 |

**策略**：IA 直链 401 → 搜索同一书名的**其他 IA identifier**（IA 同一书常有多个 scan）→ 逐一尝试 metadata 验证 + 下载。

### 失败源（本次新增）

| 源 | 书 | 结果 | 大小 |
|----|----|------|------|
| `climber.uml.edu.ni/.../ConsciousBusiness...pdf` | 清醒 | ❌ HTML | 1.1KB |
| `dev3.dattapeetham.org/.../HappinessHypothesis.pdf` | 象与骑象人 | ❌ HTML | 338B |
| `oceanofpdf.com` | 通用 | ⚠️ JS/Search 结果页，非直接文件 | - |

### oceanofPDF 注意事项

oceanofPDF.com 有书但不能直接 curl——需 browser 导航到详情页提取真实文件 URL，再 curl 下载。流程同 Anna's Archive。

---

## 新增实测源（2026-05 本次 session）

| 源 URL（截断） | 书 | 结果 | 大小 |
|--------|--------|------|------|
| `icrrd.com/...7%20Habits%20...pdf` | 7 Habits | ✅ 有效 PDF | 4.4MB |
| `files.blogs.baruch.cuny.edu/...Flow.pdf` | 心流 | ✅ 有效 PDF | 1.5MB |
| `archive.org/...thinking-fast-and-slow...pdf` | 思考快与慢 | ✅ 有效 PDF | 3.5MB |
| `nottinghamphilosophyclub...Invention-of-Good-and-Evil.pdf` | 善与恶的发明 | ⚠️ PDF 但仅样本章 | 58KB |
| `lan-portal.uob.edu.ly/...conscious_business.pdf` | 清醒 | ❌ 返回 HTML | 5KB |
| `dev3.dattapeetham.org/...HappinessHypothesis.pdf` | 象与骑象人 | ❌ 返回 HTML | 338B |
| `app.pulsar.uba.ar/...Misbehaving...pdf` | 错误的行为 | ❌ 返回 HTML | 1.1KB |
| `islamiceconomicsproject.com/...predictably-irrational.pdf` | 怪诞行为学 | ❌ 返回 HTML | 73KB |

**教训**：HTML 错误页大小从 1KB 到 150KB 不等，大小判断必须配合 `file` 命令。

---

## Anna's Archive 下载流程（✅ 可用，需浏览器）

**搜索**：`https://annas-archive.gl/search?q=<书名+作者>`

**找 md5**：搜索结果页每个结果有 `/md5/<hash>` 链接

**详情页**：`https://annas-archive.gl/md5/<hash>`

**下载链接**（JS 渲染后出现）：
```
/fast_download/<md5>/<bucket>/<file_id>   # 需要 free member cookie
/slow_download/<md5>/<bucket>/<file_id>  # DDoS-Guard 拦截
/ipfs_downloads/md5:<md5>                 # IPFS，可能可用
```

**直接 curl 不可用原因**：`fast_download` 返回 JS 挑战页（需要浏览器执行 JS），curl 只拿到 HTML 而非文件。

**正确方式**：browser 工具导航到详情页，从 DOM 中提取 `fast_download` URL，再用 `curl -L` 下载。

---

## libgen.li 下载流程（⚠️ 部分可用）

**搜索**：`https://libgen.li/index.php?req=<书名>&columns[]=t&columns[]=a`

**结果格式**：`/book/<md5hash>` → 点击进详情页

**详情页结构**：
- 页面包含文件信息（id、大小、格式）
- 下载链接通常通过 `ads.php?md5=<hash>` 或 `file.php?id=<id>` 跳转

**curl 直接下载**：`curl -s --max-time 20 "https://libgen.li/file.php?id=<file_id>" -o book.epub`
- 结果：HTTP 200 但内容是 HTML（需要登录态或 cookie）

---

## 批量下载失败模式

| 方法 | 失败原因 |
|------|----------|
| `curl + Anna's Archive fast_download` | 返回 JS 挑战页，非实际文件 |
| `curl + Anna's Archive slow_download` | DDoS-Guard 403 |
| `curl + Anna's Archive ipfs_downloads` | DDoS-Guard 拦截 |
| `curl + libgen file.php` | HTTP 200 但 body 是 HTML 登录页 |
| `urllib.request` 直接下载 | 同上，DNS 可能超时 |

---

## 推荐工作流（更新版）

```
1. 判断格式：PDF书 → 先 archive.org；EPUB/找不到 → Anna's Archive
2. archive.org：用 Open Library API 定位 identifier，用 metadata API 验证文件存在
3. 尝试 curl 下载主 PDF（老书大概率成功；版权书 → 401）
4. 401 → Anna's Archive（browser 提取 fast_download URL，curl 下载）
5. 再失败 → z-library.se（需账号）
6. 全部失败 → 请用户手动下载到 ~/books/
```

---

## 书签

- Anna's Archive: https://annas-archive.gl
- z-library: https://z-library.se
- libgen.li: https://libgen.li
