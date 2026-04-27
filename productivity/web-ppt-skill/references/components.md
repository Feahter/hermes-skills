# 组件参考 · Components

template.html 已经定义好了所有样式，这里只写"这个组件长什么样、怎么用"。

---

## 目录

- [字体 Typography](#字体-typography)
- [Chrome & Foot](#chrome--foot)
- [Callout 引用框](#callout-引用框)
- [Stat 数字矩阵](#stat-数字矩阵)
- [Pipeline 流水线](#pipeline-流水线)
- [Tag & Kicker](#tag--kicker)
- [Figure 图片框](#figure-图片框)
- [Icons 图标](#icons-图标)
- [Ghost 巨型背景字](#ghost-巨型背景字)
- [Highlight 荧光标记](#highlight-荧光标记)

---

## 字体 Typography

**叙事轴（衬线为主）：**

| Class | 用途 | 字体 | 示例 |
|-------|------|------|------|
| `.h-hero` | 超大标题（封面/幕封）| Playfair Display 700, 10vw | 演讲标题 |
| `.h-sub` | 副标题 | Noto Serif SC 600 | 副标题 |
| `.h-xl` | 页面主标题 | Noto Serif SC 700 | 4.6vw |
| `.lead` | 引导段 | Noto Serif SC 400 | 比 body 大 |
| `.body-zh` | 正文（非衬线）| Noto Sans SC 400 | 信息密度文字 |
| `.kicker` | 小节提示 | IBM Plex Mono, 12px uppercase | 标题前缀 |
| `.meta` | 元信息 | IBM Plex Mono | 页脚/来源 |

**展示轴（非衬线为主）：**

| Class | 用途 | 字体 |
|-------|------|------|
| `.display` | 超大英文 | Archivo Black / Manrope / Syne |
| `.title` | 标题 | Space Grotesk / Plus Jakarta Sans |
| `.body` | 正文 | 对应主体的 body 字体 |

**字体分工原则**：
- **衬线**：标题、重点金句、数字 — "视觉重音"
- **非衬线**：正文描述、大段阅读 — "信息密度"
- **等宽**：kicker、meta、foot — "装饰节奏"

---

## Chrome & Foot

每一页的顶部和底部元信息条。

```html
<div class="chrome">
  <div>第一幕 · 硬数据</div>
  <div>02 / 25</div>
</div>

<!-- ... 内容 ... -->

<div class="foot">
  <div>项目名 · CodePilot　|　github.com/codepilot</div>
  <div>Act I · Dev Numbers</div>
</div>
```

---

## Callout 引用框

展示金句 / 关键观点 / 他人引言。

```html
<div class="callout">
  "这东西在三年前，
  需要一个十人团队做一年。"
  <div class="callout-src">— 一个观察者的判断</div>
</div>
```

**变体**：
- 不带 cite：去掉 `.callout-src`
- 带英文金句：`<em class="en">"Thin Harness, Fat Skills."</em>`
- Hero 页使用：外层加 `style="position:relative;z-index:2"`

---

## Stat 数字矩阵

展示数据指标。

```html
<div class="grid-6">
  <div class="stat-card">
    <div class="stat-label">Duration</div>
    <div class="stat-nb">64 <span class="stat-unit">天</span></div>
    <div class="stat-note">从 0 到现在</div>
  </div>
</div>
```

三段式：`stat-label`（等宽小字）→ `stat-nb`（巨型数字）→ `stat-note`（注释）

---

## Pipeline 流水线

展示工作流程。

```html
<div class="pipeline-section">
  <div class="pipeline-label">文本侧 · Text Pipeline</div>
  <div class="pipeline">
    <div class="step">
      <div class="step-nb">01</div>
      <div class="step-title">Draft</div>
      <div class="step-desc">AI 帮我起草初稿</div>
    </div>
  </div>
</div>
```

---

## Tag & Kicker

**Kicker**：标题上方的小提示文字（等宽、全大写）：

```html
<div class="kicker">过去 64 天 · 开发篇</div>
<h2 class="h-xl">一个人，做了什么。</h2>
```

**Tag**：独立标签胶囊：

```html
<div style="display:flex;gap:1.6vw;flex-wrap:wrap">
  <div class="tag">早上 10 点起床</div>
  <div class="tag">周二 / 四下午健身</div>
</div>
```

---

## Figure 图片框

**规则（血泪经验）**：

1. **必须用 `height:Nvh` 固定高度**，不要用 `aspect-ratio`
2. `object-position:top center`（已在 CSS 里设好），只允许裁底部
3. 图片网格里多张图时，用内联 grid：

```html
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1vh 1.2vw">
  <figure class="tile">...</figure>
  <figure class="tile">...</figure>
  <figure class="tile">...</figure>
</div>
```

**标准结构**：

```html
<figure class="tile">
  <div class="frame-img" style="height:26vh">
    <img src="images/xxx.png" alt="说明">
  </div>
  <figcaption class="frame-cap">
    <span class="pf">推特 · Twitter</span>
    <span class="nb">137K</span>
  </figcaption>
</figure>
```

**图片占位（设计阶段）**：

```html
<div class="img-slot r-4x3">
  <span class="plus">+</span>
  <span class="label">GitHub 截图位置</span>
</div>
```

---

## Icons 图标

**严禁使用 emoji**。用 Lucide via CDN（template.html 已引入）。

```html
<i data-lucide="compass" class="ico-lg"></i>     <!-- 大图标（pillar 用） -->
<i data-lucide="target" class="ico-md"></i>      <!-- 中图标（列表项用） -->
<i data-lucide="check-circle" class="ico-sm"></i><!-- 小图标（inline 用） -->
```

**常用图标名（按含义）**：

- 判断类：`compass`, `target`, `crosshair`, `search-check`
- 关系类：`share-2`, `users`, `network`, `link`, `handshake`
- 品牌类：`crown`, `gem`, `award`, `star`, `badge-check`
- 流程类：`workflow`, `route`, `arrow-right-left`, `repeat`
- 数据类：`grid-2x2`, `bar-chart-3`, `trending-up`, `activity`
- 审美类：`palette`, `brush`, `eye`, `sparkles`

---

## Ghost 巨型背景字

用作装饰性背景字，极低透明度，营造杂志感。

```html
<div class="ghost" style="right:-6vw;top:-8vh">BUT</div>
<div class="ghost" style="left:-8vw;bottom:-18vh;font-style:italic">Harness</div>
```

- 字号 34vw，opacity 0.06
- 内容：英文单词或章节序号（01/02/03、关键词 BUT/NOW/HERE）

**注意**：使用 ghost 的页面里，其他内容要加 `position:relative;z-index:2` 避免被压。

---

## Highlight 荧光标记

行内短语的"荧光笔"效果：

```html
<span class="hi">不是</span>
<span class="hi">一次性爆发</span>
```

适合场景：只对关键 1-3 个词使用，不要大面积用。

---

## 内联编辑相关组件（opt-in）

### 编辑热区

```html
<div class="edit-hotzone"></div>
```

固定在左上角 80×80px，hover 时唤出编辑按钮。

### 编辑按钮

```html
<button class="edit-toggle" id="editToggle" title="Edit mode (E)">✏️</button>
```

JS 控制可见性，不使用 CSS `~` sibling 选择器（会导致 hover 链断裂）。

---

## CSS 负值函数陷阱

**WRONG（浏览器静默忽略）：**
```css
right: -clamp(28px, 3.5vw, 44px);   /* 整条规则被忽略 */
margin-left: -min(10vw, 100px);
```

**CORRECT：**
```css
right: calc(-1 * clamp(28px, 3.5vw, 44px));  /* 有效 */
margin-left: calc(-1 * min(10vw, 100px));
```
