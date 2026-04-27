# 质量检查清单 · Checklist

来自 magazine-web-ppt × frontend-slides 真实迭代经验。生成前通读，生成后逐项自检。

---

## 🔴 P0 · 一定不能犯的错

### 0. 生成前必须通过的类名校验

**现象**：layouts.md 骨架粘到新 HTML，样式全部丢失——大标题变成非衬线、数据大字报字体小得像正文、pipeline 糊成一坨。

**根因**：`assets/template.html` 的 `<style>` 块里没有对应类的定义，浏览器 fallback 到默认样式。

**做法**：
- **生成前，必须先 `Read` `assets/template.html`**，确认 layouts.md 里用到的类都已定义
- 常见遗漏：`h-hero / h-xl / h-sub / h-md / lead / meta-row / stat-card / stat-label / stat-nb / stat-unit / stat-note / pipeline-section / pipeline-label / pipeline / step / step-nb / step-title / step-desc / grid-2-7-5 / grid-2-6-6 / grid-2-8-4 / grid-3-3 / frame / img-cap / callout-src`
- 如果某个类确实缺了，**在 template.html 的 `<style>` 里补上**，不要在每页 inline 重写
- 生成后打开浏览器，如果"大标题是非衬线"或"pipeline 挤在一行"，100% 是这个问题

### 1. 不要用 emoji 作图标

**现象**：在杂志风格里用 emoji（🎯 💡 ✅）会立刻破坏格调。

**做法**：用 Lucide 图标库：
```html
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
<i data-lucide="target" class="ico-md"></i>
<script>lucide.createIcons();</script>
```
常用图标名：`target / palette / search-check / compass / share-2 / crown / check-circle / x-circle / plus / arrow-right`

### 2. 图片只允许裁底部

**现象**：用 `aspect-ratio` 撑图，网格会在父容器不足时撑破或图片关键信息被切掉。

**做法**：
```html
<figure class="frame-img" style="height:26vh">
  <img src="screenshot.png">
</figure>
```
CSS 里 `.frame-img img` 已经预设 `object-position:top`，只裁底。

**禁止**：
```html
<!-- 坏例 -->
<figure class="frame-img" style="aspect-ratio: 16/9">...</figure>
```

### 3. chrome 和 kicker 不要写同一句话

**现象**：左上角 `.chrome` 写"Design First · 设计先行"，`.kicker` 又写"Phase 01 · 设计阶段"——同义重复，AI 味浓。

**做法**：
- `.chrome` = **杂志页眉 / 栏目标签**，跨页可复用（如 "Act II · Workflow"、"Data · Result"）
- `.kicker` = **本页独一份的引导句**，短、有钩子、是大标题的小前缀（如 "BUT"、"一个人，做了什么。"）
- 一个描述栏目，一个描述这一页——绝不互相翻译

### 4. 每个 slide 必须带主题类

**现象**：只写 `hero` 不带主题色，WebGL 背景无法切换，light 页灰蒙蒙。

**做法**：
- hero 页用 `hero light` / `hero dark`
- 正文页用 `light` / `dark`
- **不能只写 `hero`**

### 5. 不能全是 light 正文页

**现象**：除封面 `hero dark` 外，全写 `light`——视觉平淡，没有呼吸感。

**做法**：
- 8 页以上必须有 ≥1 `hero dark` + ≥1 `hero light`
- 必须有 `dark` 正文页制造节奏对比
- 连续 3 页以上同主题 = 不允许

### 6. CSS 负值必须用 `calc(-1 * ...)`

**现象**：`-clamp()`、`-min()`、`-max()` 浏览器静默忽略，无报错，元素位置错误。

**做法**：
```css
/* 错误 — 浏览器忽略整条规则 */
right: -clamp(28px, 3.5vw, 44px);

/* 正确 */
right: calc(-1 * clamp(28px, 3.5vw, 44px));
```

### 7. 禁止 `align-self:end` 贴图

**现象**：在 `<figure>` 上加 `align-self:end`，如果父容器不是 grid，失效且图片掉到页面底部被遮挡。

**做法**：
- 图文混排必须用 `.frame.grid-2-7-5`（或 `.grid-2-6-6`）
- 图片用 `height:Nvh + max-height:56vh + object-fit:cover`，自然贴顶
- 要让左列 callout 贴底，给左列加 `flex column + justify-content:space-between`

---

## 🟡 P1 · 排版节奏

### 8. 大标题字数限制

- `h-hero`（最大）：≤ 5 字，用 `white-space:nowrap` 防止换行
- `h-xl`（次大）：≤ 10 字，可用 `<br>` 手工断行
- 长标题不要依赖自动换行

### 9. WebGL 背景透明度

- dark hero：遮罩 12-15%（WebGL 明显透出）
- light hero：遮罩 16-20%（隐约可见，不抢字）
- 普通 light/dark 页：遮罩 92-95%（几乎不透）

### 10. 图片不要用原图奇葩比例

无论原图什么比例，固定用 **16:10 / 4:3 / 3:2 / 1:1 / 16:9**。

### 11. 不要给图片加厚边框 / 阴影

最多 4px 极淡圆角 + 极淡底噪。不要加 `box-shadow`、不要加粗 border。

### 12. 字体分工三轨制

| 类型 | 字体 | 类 |
|------|------|-----|
| 大标题、金句、数字 | 衬线（Noto Serif SC / Playfair） | `.h-hero` / `.h-xl` / `.lead` / `.callout` |
| 正文、描述 | 非衬线（Noto Sans SC） | `.body-zh` |
| 元数据、标签 | 等宽（IBM Plex Mono） | `.meta` / `.kicker` / `.chrome` / `.foot` |

---

## 🟢 P2 · 视觉打磨

### 13. Hero 页和非 hero 页要交替

推荐节奏（8 页示例）：
```
封面(hero dark) → 数据大字报 → 左文右图 → Pipeline
→ 章节幕封(hero light) → 大引用 → 问题页(hero dark) → 结尾
```

### 14. 大字报页和密集页要交替

大字报（big numbers）和密集页（pipeline / image grid）交替，听众眼睛才不累。

### 15. 同一概念术语统一

全文同一个词只有一种写法。优先用英文（Skills / Harness / Pipeline / Workflow）。

### 16. 底部 chrome 页码格式一致

用 `XX / 总页数`（如 `05 / 27`）。不要在右上角加动态页码。

---

## 🔵 P3 · 操作细节

### 17. 图片路径用相对路径

放在 `images/` 文件夹下，HTML 里用 `images/xxx.png`，不要用绝对路径。

### 18. 页码在 `.chrome` 里写死

JS 动态算总页数，但 `.chrome` 里的 `XX / N` 是写死的。加页/删页时要手工改 N。

### 19. 不要用 `height:100vh` 硬设

用 `min-height:80vh + align-content:center`，更稳定，不被浏览器工具栏遮挡。

---

## ✅ 最终自检清单

```
预检（生成前）
  □ 已读过 template.html 的 <style>，确认所需类都存在
  □ 已决定每页用哪个 Layout（1-10）
  □ 已画出"主题节奏表"：每页明确 hero dark / hero light / light / dark
  □ 节奏表满足硬规则：无连续 3 页同主题 / 有 ≥1 hero dark + ≥1 hero light（8 页以上）
  □ <title> 已改为实际 deck 标题（grep "[必填]" 应无结果）

内容
  □ 没有使用 emoji 作图标
  □ chrome 和 kicker 写法不重复
  □ 术语用法统一

排版
  □ 大标题字数符合上限，无 1 字 1 行
  □ 图片网格用 height:Nvh 而非 aspect-ratio
  □ 无 align-self:end
  □ 无 CSS 负值函数（-clamp / -min / -max）

字体
  □ 衬线/非衬线/等宽分工正确

视觉
  □ hero 页和 non-hero 页交替
  □ 连续 3 页无同主题
  □ 无厚重边框和阴影

交互
  □ ← → 翻页正常
  □ 底部圆点数量与总页数匹配
  □ chrome 里的页码和实际页号一致
```

全勾完，才是合格的 PPT。
