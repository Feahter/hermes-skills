# 页面布局库（Layouts）

10 种常用布局骨架，每种都是完整可粘贴的 `<section class="slide">` 代码块，直接改文案/图片即可。

---

## ⚠️ 生成前必读

### A. 类名必须来自 template.html

layouts.md 使用的所有类（`h-hero` / `h-xl` / `stat-card` / `pipeline` / `step` / `grid-2-7-5` 等）都在 `assets/template.html` 的 `<style>` 块里预定义。

**不要发明新类名**。如果必须自定义，用 `style="..."` inline。

### B. 密度上限（工程纪律）

| 类型 | 上限 |
|------|------|
| 内容页 bullet | ≤ 6 条 |
| 特性网格卡片 | ≤ 6 张 |
| 代码行数 | ≤ 10 行 |
| 引用行数 | ≤ 3 行 |

**超出自动拆页，不要问用户。**

### C. 图片比例规范

| 场景 | 推荐比例 |
|------|---------|
| 左文右图主图 | 16:10 或 4:3 + `max-height:56vh` |
| 图片网格（多图） | **固定 `height:26vh`**，不用 aspect-ratio |
| 左小图 + 右文字 | 1:1 或 3:2 |
| 全屏主视觉 | 16:9 + `max-height:64vh` |

图片必须包在 `<figure class="frame-img">` 里，`object-fit:cover + object-position:top center`，只裁底部。

### D. 叙事轴与主题节奏

叙事轴决定 hero 使用频率：
- **叙事轴**：每 3-4 页一个 hero 页（封面/幕封/金句/问题）
- **展示轴**：少 hero，多网格和卡片

**禁止**：连续 3 页以上相同主题 / 整份 deck 无 hero

---

## 0. 基础 Slide 外壳

```html
<section class="slide [light|dark|hero light|hero dark]">
  <div class="chrome">
    <div>栏目名 · 章节名</div>
    <div>页码 / 总数</div>
  </div>
  <!-- 主内容 -->
  <div class="foot">
    <div>页脚说明 · Page Description</div>
    <div>— · —</div>
  </div>
</section>
```

### chrome 和 kicker 不要写同一句话

| 位置 | 角色 | 内容性质 |
|------|------|---------|
| `.chrome` 左上 | 栏目标签，跨页可复用 | 稳定的"栏目名"或"章节分类" |
| `.kicker` | 本页钩子，大标题前缀 | 短句、有戏剧性，每页都应不同 |

---

## Layout 1: 开场封面（Hero Cover）

```html
<section class="slide hero dark">
  <div class="chrome">
    <div>分享 · 2026.04.22</div>
    <div>Vol.01</div>
  </div>
  <div class="frame" style="display:grid; gap:4vh; align-content:center; min-height:80vh">
    <div class="kicker">私享会 · 分享者名</div>
    <h1 class="h-hero">演讲标题</h1>
    <h2 class="h-sub">副标题</h2>
    <p class="lead" style="max-width:60vw">
      一句话简介，描述这场分享的核心。
    </p>
    <div class="meta-row">
      <span>分享者</span><span>·</span><span>Title / Company</span>
    </div>
  </div>
  <div class="foot">
    <div>一场关于 XX 的分享</div>
    <div>— 2026 —</div>
  </div>
</section>
```

---

## Layout 2: 章节幕封（Act Divider）

```html
<section class="slide hero [light|dark]">
  <div class="chrome">
    <div>第一幕 · 硬数据</div>
    <div>Act I · 01 / 25</div>
  </div>
  <div class="frame" style="display:grid; gap:6vh; align-content:center; min-height:80vh">
    <div class="kicker">Act I</div>
    <h1 class="h-hero" style="font-size:8.5vw">幕封标题</h1>
    <p class="lead" style="max-width:55vw">先看数字，再谈方法。</p>
  </div>
  <div class="foot">
    <div>第一幕引子</div>
    <div>— · —</div>
  </div>
</section>
```

---

## Layout 3: 数据大字报（Big Numbers）

```html
<section class="slide light">
  <div class="chrome">
    <div>过去 64 天 · 开发篇</div>
    <div>Act I / Dev · 02 / 25</div>
  </div>
  <div class="frame" style="padding-top:6vh">
    <div class="kicker">过去 64 天 · 开发篇</div>
    <h2 class="h-xl">一个人，做了什么。</h2>
    <p class="lead" style="margin-bottom:5vh">从 0 到开源 CodePilot。</p>

    <div class="grid-6" style="margin-top:6vh">
      <div class="stat-card">
        <div class="stat-label">Duration</div>
        <div class="stat-nb">64 <span class="stat-unit">天</span></div>
        <div class="stat-note">从 0 到现在</div>
      </div>
      <!-- 更多 stat-card ... -->
    </div>
  </div>
  <div class="foot">
    <div>项目 · CodePilot　|　github.com/codepilot</div>
    <div>Act I · Dev Numbers</div>
  </div>
</section>
```

---

## Layout 4: 左文右图（Quote + Image）

```html
<section class="slide light">
  <div class="chrome">
    <div>身份反差 · The Twist</div>
    <div>03 / 25</div>
  </div>
  <div class="frame grid-2-7-5" style="padding-top:6vh">
    <!-- 左列：标题 + 正文 + callout，flex column 让 callout 贴列底 -->
    <div style="display:flex; flex-direction:column; justify-content:space-between; gap:3vh">
      <div>
        <div class="kicker">BUT</div>
        <h2 class="h-xl" style="white-space:nowrap; font-size:7.2vw">我不是程序员。</h2>
        <p class="lead" style="margin-top:3vh">
          大学毕业之后再也没写过一行代码。过去十年做的是 UI 设计和 AI 特效。
        </p>
      </div>
      <div class="callout">
        "这东西在三年前，需要一个十人团队做一年。"
        <div class="callout-src">— 一个观察者的判断</div>
      </div>
    </div>
    <!-- 右列：图片用标准比例 -->
    <figure class="frame-img" style="aspect-ratio:16/10; max-height:56vh">
      <img src="images/product.png" alt="产品截图">
      <figcaption class="img-cap">产品名 · 截图</figcaption>
    </figure>
  </div>
  <div class="foot">
    <div>Page 03 · 身份反差</div>
    <div>— · —</div>
  </div>
</section>
```

---

## Layout 5: 图片网格（多图对比）

```html
<section class="slide light">
  <div class="chrome">
    <div>平台粉丝实证</div>
    <div>Act I / Ops · 05 / 27</div>
  </div>
  <div class="frame" style="padding-top:5vh">
    <div class="kicker">Proof · 粉丝实证</div>
    <h2 class="h-xl">10 个平台 · 6 张截图</h2>

    <div class="grid-3-3" style="margin-top:4vh">
      <figure class="frame-img" style="height:26vh">
        <img src="images/weibo.png" alt="微博 289K">
        <figcaption class="img-cap">微博 · 289K</figcaption>
      </figure>
      <!-- 更多 frame-img ... -->
    </div>
  </div>
  <div class="foot">
    <div>截图时间 · 2026.04</div>
    <div>Page 05 · 粉丝实证</div>
  </div>
</section>
```

**关键**：每个 `frame-img` 写死 `height:NNvh`（不用 aspect-ratio），图片自动 `object-fit:cover`。

---

## Layout 6: 两列流水线（Pipeline）

```html
<section class="slide light">
  <div class="chrome">
    <div>我的工作流 · Workflow</div>
    <div>Act II · 15 / 27</div>
  </div>
  <div class="frame">
    <div class="kicker">Pipeline · 流水线</div>
    <h2 class="h-xl">两条流水线</h2>

    <div class="pipeline-section">
      <div class="pipeline-label">文本侧 · Text Pipeline</div>
      <div class="pipeline">
        <div class="step">
          <div class="step-nb">01</div>
          <div class="step-title">Draft</div>
          <div class="step-desc">AI 帮我起草初稿</div>
        </div>
        <div class="step">
          <div class="step-nb">02</div>
          <div class="step-title">Polish</div>
          <div class="step-desc">AI 润色去 AI 味</div>
        </div>
        <!-- 更多 step ... -->
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 15 · 我的内容工厂</div>
    <div>Workflow</div>
  </div>
</section>
```

---

## Layout 7: 悬念收束 / 问题页（Hero Question）

```html
<section class="slide hero dark">
  <div class="chrome">
    <div>留给你的问题</div>
    <div>24 / 27</div>
  </div>
  <div class="frame" style="display:grid; gap:8vh; align-content:center; min-height:80vh">
    <div class="kicker">The Question</div>
    <h1 class="h-hero" style="font-size:7vw; line-height:1.15">
      你的公司里，<br>哪些岗位本来就<br>不该由人来做？
    </h1>
    <p class="lead" style="max-width:50vw">
      这个问题，不是技术问题，是架构问题。
    </p>
  </div>
  <div class="foot">
    <div>Page 24 · The Question</div>
    <div>— · —</div>
  </div>
</section>
```

---

## Layout 8: 大引用页（Big Quote）

```html
<section class="slide light">
  <div class="chrome">
    <div>The Takeaway · 核心金句</div>
    <div>18 / 25</div>
  </div>
  <div class="frame" style="display:grid; gap:5vh; align-content:center; min-height:80vh">
    <div class="kicker">Quote · 金句</div>
    <blockquote style="font-family:var(--serif-zh); font-weight:700; font-size:5.8vw; line-height:1.2; letter-spacing:-.01em; max-width:72vw">
      "没有交接，所有人都构建。"
    </blockquote>
    <p class="lead" style="max-width:55vw; opacity:.65">
      Without the handoff, everyone builds.<br>And that makes all the difference.
    </p>
    <div class="meta-row">
      <span>— Luke Wroblewski</span><span>·</span><span>2026.04.16</span>
    </div>
  </div>
  <div class="foot">
    <div>Page 18 · 金句</div>
    <div>— · —</div>
  </div>
</section>
```

---

## Layout 9: 并列对比（Before / After）

```html
<section class="slide light">
  <div class="chrome">
    <div>模式对比</div>
    <div>10 / 25</div>
  </div>
  <div class="frame grid-2-6-6" style="padding-top:6vh">
    <div>
      <div class="kicker">BEFORE</div>
      <h2 class="h-xl">旧模式</h2>
      <p class="lead">传统的工作方式，效率低下。</p>
    </div>
    <div>
      <div class="kicker">AFTER</div>
      <h2 class="h-xl">新模式</h2>
      <p class="lead">AI 加持后，一个人顶一支团队。</p>
    </div>
  </div>
  <div class="foot">
    <div>Page 10 · 模式对比</div>
    <div>— · —</div>
  </div>
</section>
```

---

## Layout 10: 图文混排（Lead Image + Side Text）

```html
<section class="slide [light|dark]">
  <div class="chrome">
    <div>产品特性</div>
    <div>06 / 25</div>
  </div>
  <div class="frame grid-2-7-5" style="padding-top:6vh">
    <figure class="frame-img" style="aspect-ratio:16/9; max-height:56vh">
      <img src="images/dashboard.png" alt="仪表盘截图">
      <figcaption class="img-cap">产品仪表盘</figcaption>
    </figure>
    <div style="display:flex; flex-direction:column; justify-content:center; gap:3vh">
      <div>
        <div class="kicker">特性一</div>
        <h2 class="h-xl">标题</h2>
        <p class="lead">详细说明文字，不要超过 2 段。</p>
      </div>
    </div>
  </div>
  <div class="foot">
    <div>Page 06 · 产品特性</div>
    <div>— · —</div>
  </div>
</section>
```

---

## 主题节奏规划（生成前必做）

### 叙事轴节奏模板（8 页示例）

| 页 | 主题 | 布局 | 备注 |
|---|---|---|---|
| 1 | `hero dark` | 封面 | 开场 |
| 2 | `light` | 数据大字报 | 抛出数据 |
| 3 | `dark` | 左文右图 | 对比/故事 |
| 4 | `light` | Pipeline | 流程 |
| 5 | `hero light` | 章节幕封 | 呼吸 |
| 6 | `dark` | 左文右图 or 大引用 | |
| 7 | `hero dark` | 问题页 | 悬念收束 |
| 8 | `light` | 大引用/结尾 | 收尾 |

**先画节奏表对齐，再动手写 slide。**

### 展示轴节奏要点

- hero 少，主要用 `light` / `dark` 正文页
- 多用 grid-3-3（图片网格）、stat-card（数据）、pipeline（流程）
- 每 5-6 页可插一个 `hero` 打破节奏

---

## 密度检查清单（生成后自检）

```bash
# 检查所有 slide 的主题
grep 'class="slide' output.html

# 检查是否有连续 3+ 页相同主题
grep -c 'class="slide light' output.html  # 应该 < 总页数/2

# 检查 bullet 数量（每页应 ≤ 6）
grep -o '<li>' output.html | wc -l

# 检查是否有 overflow 风险（高分辨率下测试）
# 打开浏览器开发者工具，设为 1920×1080，检查是否滚动条出现
```
