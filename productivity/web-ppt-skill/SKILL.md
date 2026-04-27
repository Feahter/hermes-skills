---
name: web-ppt-skill
description: 生成单文件 HTML 演示文稿，融合电子杂志的叙事美学与工程化密度管理。支持横向翻页、主题切换、PPT 转换、内联编辑、Vercel 部署和 PDF 导出。当用户需要制作分享/演讲/发布会的网页 PPT，或提到"杂志风 PPT"、"horizontal swipe deck"、"web slides"、"HTML presentation"时使用。
---

# Web PPT Skill

融合 magazine-web-ppt（叙事美学）× frontend-slides（工程密度管理）的下一代 HTML 演示文稿 skill。

## 核心设计原则

> 融合 magazine-web-ppt（叙事美学）× frontend-slides（工程密度管理）的设计哲学。

### 设计原则

1. **叙事为主轴，密度为锚点** — 横向翻页（magazine 遗产）+ 严格量化溢出管理（frontend 遗产）
2. **风格是变量，不是约束** — 17 套预设主题按需切换
3. **内容永远服务于故事** — 不管技术多强大，第一问永远是"你的故事是什么"

### 反 AI Slop（Anti-AI-Slop）

**这是设计红线。** 下面这些是 generic AI 输出的标配——必须避免：

- **字体**：Arial、Inter、Roboto、系统字体 → 用 Fontshare 或 Google Fonts 的特色字体
- **颜色**：`#6366f1`（通用靛蓝）、紫色渐变白底 → 用 themes.md 预设
- **布局**：全居中、通用 hero、均匀卡片网格 → 用 layouts.md 的非对称骨架
- **装饰**：真实插画、无目的玻璃拟态、无意义的阴影

你倾向于在多次生成中收敛到同一个选择（Space Grotesk 尤其典型）。每次都要主动打破这种收敛。

---

## 工作流程总览

```
Phase 0 · Detect    → 判断模式（新建/PPT转换/增强）
Phase 1 · Clarify   → 6+4 问需求澄清（叙事型 or 展示型）
Phase 2 · Style     → 选叙事轴 → 风格预览 → 用户选
Phase 3 · Generate  → 生成完整 HTML
Phase 4 · Deliver   → 本地预览 + 可选部署/导出
```

---

## Phase 0: Detect Mode

| 模式 | 判断条件 | 跳转 |
|---|---|---|
| **Mode A: 新建** | 用户要全新制作，无现有 PPT | → Phase 1 |
| **Mode B: PPT 转换** | 用户提供了 .pptx/.ppt 文件 | → Phase 1B |
| **Mode C: 增强** | 用户有现有 HTML 演示要改进 | → Phase 1C |

---

## Phase 1: 需求澄清（Mode A 新建）

### 1.1 叙事弧模板（先搭骨架）

**如果用户没有大纲**，用叙事弧模板搭骨架，再填内容。**三张表对齐后再进 Phase 2**：

```
钩子(Hook)       → 1 页   : 抛一个反差 / 问题 / 硬数据让人停下来
定调(Context)    → 1-2 页 : 说明背景 / 你是谁 / 为什么讲这个
主体(Core)       → 3-5 页 : 核心内容，用 Layout 4/5/6/9/10 穿插
转折(Shift)      → 1 页   : 打破预期 / 提出新观点
收束(Takeaway)   → 1-2 页 : 金句 / 悬念问题 / 行动建议
```

**节奏规划**（生成前必做）：

| 页 | 主题 | 布局 |
|---|---|---|
| 1 | `hero dark` | 封面 |
| 2 | `light` | 数据大字报（抛数据）|
| 3 | `dark` | 左文右图（故事）|
| 4 | `light` | Pipeline（流程）|
| 5 | `hero light` | 章节幕封（呼吸）|
| 6 | `dark` | 左文右图 or 大引用 |
| 7 | `hero dark` | 问题页（悬念）|
| 8 | `light` | 大引用/结尾（收束）|

**硬规则**：
- 每页必须带 `light` / `dark` / `hero light` / `hero dark` 之一，**不能只写 `hero`**
- 连续 3 页以上同主题 = 不允许
- 8 页以上必须有 ≥1 个 `hero dark` + ≥1 个 `hero light`
- **不能全是 `light` 正文页**，必须有 `dark` 正文页制造呼吸

**生成后自检**：`grep 'class="slide' index.html` 列出所有主题，人工确认节奏合理再交付。

### 1.2 六问澄清

**一次问完，不逐条追问：**

| # | 问题 | 选项 |
|---|------|------|
| 1 | 受众是谁？场景？ | 行业分享 / 商业发布 / Demo Day / 私享会 / 技术演讲 / 内部培训 |
| 2 | 预计时长？ | 5 分钟 ≈ 8 页 / 15 分钟 ≈ 15 页 / 30 分钟 ≈ 25 页 / 45 分钟 ≈ 35 页 |
| 3 | 有没有原始素材？ | 完整大纲+图片 / 只有大纲 / 只有主题/方向 |
| 4 | 有没有图片素材？ | 有（在XXX文件夹）/ 没有 / 需要配图建议 |
| 5 | 编辑器内联编辑？ | Yes（推荐）/ No |
| 6 | 有没有硬约束？ | 必须包含 XX / 不能出现 YY / 无 |

**额外 4 问（决定叙事轴）：**

| # | 问题 | 选项 |
|---|------|------|
| 7 | 这是什么类型的演示？ | **叙事型**（讲故事、有节奏感）/ **展示型**（信息密集、有逻辑链） |
| 8 | 视觉风格偏好？ | 沉稳克制（衬线+留白）/ 活力冲击（大体字+强对比）/ 技术极客（代码+图表） |
| 9 | 需要部署成可分享 URL？ | Yes（Vercel 部署）/ No |
| 10 | 需要导出 PDF？ | Yes / No |

> 6 问决定内容方向，4 问决定叙事轴和技术路径。

**内容密度规则（工程纪律，不可绕过）：**

| 类型 | 每页上限 |
|------|---------|
| 标题页 | 1 标题 + 1 副标题 + 可选 tagline |
| 内容页 | 1 标题 + 最多 6 条 bullet **或** 1 标题 + 最多 2 段文字 |
| 特性网格 | 1 标题 + 最多 6 张卡片（2×3 或 3×2）|
| 代码页 | 1 标题 + 最多 10 行代码 |
| 引用页 | 1 引用（最多 3 行）+ 出处 |
| 图片页 | 1 标题 + 1 图片（max-height: 56vh）|

**内容超出上限？自动拆页，不要问用户。**

---

## Phase 1B: PPT 转换（Mode B）

1. **提取内容**：`python scripts/extract-pptx.py <input.pptx> <output_dir>`
2. **确认大纲**：向用户展示提取的页面标题、内容摘要、图片数量
3. **判断叙事轴**：根据内容判断叙事型/展示型，或让用户确认
4. **进入 Phase 2**：风格选择

---

## Phase 1C: 增强现有 HTML（Mode C）

**增强规则：**

1. **加内容前**：先数现有元素，对照密度上限
2. **加图片**：必须 `max-height: min(50vh, 400px)`；如果页面已达密度上限，**自动拆页**并告知用户
3. **加文字**：超过 6 条 bullet？拆成续页
4. **修改后验证**：`.slide` 有 `overflow: hidden`，新元素用 `clamp()`，图片有 viewport 相对 max-height

---

## Phase 2: 风格选择

### Step 2.1: 叙事轴判断

根据 Phase 1 的问答，自动判断叙事轴：

| 叙事轴 | 特征 | 字体 | 节奏 | 背景 |
|--------|------|------|------|------|
| **叙事型** | 衬线为主，留白多，hero 节奏慢 | Cormorant / Playfair + IBM Plex Mono | hero 每 3-4 页一次 | WebGL 流体或纯色 |
| **展示型** | 非衬线为主，密度高，节奏快 | Archivo / Space Grotesk / Manrope | 少 hero，多网格 | 几何图形/渐变/纯色 |

### Step 2.2: 风格预览（Show Don't Tell）

> **"show, don't tell"** — 大多数人无法用语言描述设计偏好。让他们看到，而不是听描述。

**叙事型用户**：生成 3 个单页预览（封面页），展示不同主题风格。保存到 `~/.hermes/skills/productivity/web-ppt-skill/.previews/`。

```bash
mkdir -p ~/.hermes/skills/productivity/web-ppt-skill/.previews/
```

预览生成后自动打开，让用户在浏览器里看效果再选。

**展示型用户**：直接展示预设列表（见 `references/themes.md`），让用户选（风格差异更在于字体/色块，非沉浸式预览）。

### Step 2.3: 用户确认

**叙事型**："选 A（主题名）/ B / C / 混搭元素"
**展示型**："选预设名"

---

## Phase 3: 生成

### 生成前必读文件

| 文件 | 用途 | 何时读 |
|------|------|--------|
| `references/themes.md` | 选定主题的完整 CSS 变量 | 生成前 |
| `references/layouts.md` | 10 种布局骨架，直接粘贴 | 生成前 |
| `references/components.md` | 组件手册（字体、色、网格、图标）| 生成中 |
| `references/viewport-base.css` | 必须完整复制到每个演示 | 生成前 |
| `assets/template.html` | 完整可运行模板（含 JS 控制器）| 生成前 |

### ⚠️ P0 生成规则（必须通过，否则返工）

**1. 类名必须来自 template.html**
layouts.md 的骨架使用的所有类（`h-hero` / `h-xl` / `stat-card` / `pipeline` / `grid-2-7-5` 等）都在 `assets/template.html` 的 `<style>` 块里预定义。**不要发明新类名**。如果必须自定义，用 `style="..."` inline。

**2. 禁止用 emoji 作图标**（P0）
用 Lucide 图标：`data-lucide="target"`、`data-lucide="compass"` 等。不能用 🎯 💡 ✅。

**3. chrome 和 kicker 绝不能写同一句话**（P0）
- `.chrome` 左上 = **栏目标签**，跨页可复用（如 "Act II · Workflow"）
- `.kicker` = **本页独一份的引导句**，短、有钩子、是大标题的小前缀（如 "BUT"、"一个人，做了什么。"）
- 两者绝不互相翻译

**4. 图片只裁底部**（P0）
用 `height:Nvh` 固定高度 + `object-fit:cover` + `object-position:top center`，只裁底部。禁止用 `aspect-ratio`（会撑破）。

**5. 禁止 `align-self:end` 贴图**（P0）
用 grid 容器 + `align-items:start` 让图片贴顶。让左列 callout 贴底，给左列加 `flex column + justify-content:space-between`，不要动右列。

**6. CSS 负值必须用 `calc(-1 * ...)`**（P0）
```css
/* 错误 — 浏览器静默忽略整条规则 */
right: -clamp(28px, 3.5vw, 44px);

/* 正确 */
right: calc(-1 * clamp(28px, 3.5vw, 44px));
```

**7. 字体分工**（P0）
- 衬线 = 大标题、重点金句、数字大字（`h-hero` / `h-xl` / `lead` / `callout`）
- 非衬线 = 正文、描述（`body-zh`）
- 等宽 = kicker、元数据、chrome/foot（`meta` / `kicker`）

**8. 每个 slide 必须带主题类**（P0）
`light` / `dark` / `hero light` / `hero dark` 之一，不能只写 `hero`。

### 生成规则

1. **单文件 HTML**：所有 CSS/JS 内联，无外部依赖（图片除外）
2. **viewport-base.css 完整内嵌**：每个演示必须包含完整的 viewport-base.css
3. **字体**：从 Fontshare 或 Google Fonts 加载，不用系统字体
4. **横向翻页**：`scroll-snap-type: x mandatory`，键盘 ← → / 滚轮 / 触屏滑动 / 底部圆点
5. **动画**：基于 Scroll-triggered（Intersection Observer），每页 `.slide` 进入视口触发动画
6. **注释**：每个 section 加清晰注释块（`/* === SECTION NAME === */`）
7. **中文优化**：衬线用 Noto Serif SC，非衬线用 Noto Sans SC，等宽用 IBM Plex Mono

### 内联编辑（opt-in）

如果用户在 Phase 1 选了 Yes：

1. 左上角 hover 热区（80×80px）唤出编辑按钮
2. JS 延迟 400ms（避免 hover 链断裂）
3. 点击任意文字可编辑
4. Ctrl+S 保存到 localStorage + 下载 HTML 文件
5. **导出时必须剥离编辑状态**（`contenteditable`、`edit-active` 等）

---

## Phase 4: 交付

1. **打开预览**：`open [filename].html`
2. **告知用户**：
   - 文件路径、风格名称、页数
   - 导航：← → 键 / 滚轮 / 触屏滑动 / 底部圆点 / ESC 索引
   - 自定义方式：改 `:root` CSS 变量换色 / 换 `<link>` 换字体 / 加 `.reveal` 类触发动画
   - 内联编辑：左上角 hover 或按 E

---

## Phase 5: 部署 & 导出（可选）

交付后主动询问：

> "需要分享或导出吗？可以部署到 Vercel（免费，可分享任意设备），或导出 PDF（适合邮件/打印）。"

### 5A: Vercel 部署

```bash
bash scripts/deploy.sh <path-to-html-or-folder>
```

**注意**：
- 图片多的演示→部署整个文件夹，不要单独 HTML
- 文件名有空格→脚本已处理，但尽量用连字符
- 重新部署→URL 不变

### 5B: PDF 导出

```bash
bash scripts/export-pdf.sh <path-to-html> [output.pdf]
```

**注意**：
- 首次慢（Playwright + Chromium 下载 ~150MB）
- 超过 10MB 可加 `--compact` 降分辨率
- 动画不保留→替换为最终静态帧

### 5C: PPT 内容提取（Mode B 用户）

提取后的内容可以直接作为 Phase 3 的输入。

---

## 文件结构

```
web-ppt-skill/
├── SKILL.md                  ← 本文件
├── assets/
│   └── template.html         ← 完整可运行模板（含 JS 控制器）
└── references/
    ├── themes.md             ← 17 套主题预设
    ├── layouts.md            ← 10 种布局骨架
    ├── components.md         ← 组件手册
    ├── viewport-base.css     ← 响应式基础 CSS
    ├── animation.md          ← 动画模式参考
    ├── checklist.md          ← 质量检查清单（P0/P1/P2/P3）
    └── scripts/
        ├── extract-pptx.py   ← PPT 内容提取
        ├── deploy.sh         ← Vercel 部署脚本
        ├── export-pdf.sh     ← PDF 导出脚本
        └── image-utils.py    ← 图片处理工具
```

## 资源加载顺序

1. 读完本文件（SKILL.md）
2. Phase 1 澄清后，读 `themes.md` 确定主题
3. **Phase 2 叙事轴判断后**：叙事型 → 生成 3 张风格预览；展示型 → 展示主题列表
4. **动手前完整读** `assets/template.html` 的 `<style>` 块——类名唯一来源
5. 读 `layouts.md` 选布局（顶部有密度检查清单）
6. Phase 3 生成前，读 `checklist.md` P0 规则逐条对照
7. 细节调整时读 `components.md`
8. 生成后通读 `checklist.md`，逐项自检
