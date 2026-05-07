# aihot.today 数据解析笔记

## 关键发现

数据**不是**通过 API 或 JSON 加载，而是直接渲染在 HTML 里。`window.__NEXT_DATA__` 在此站点不存在。

## HTML 结构

每个来源的新闻卡片结构：

```html
<div class="bg-card ... max-w-[480px] ...">
  <!-- 来源 header -->
  <img alt="TechCrunch logo" />  <!-- alt 就是来源名 -->
  <span class="text-blue-600/80">05月07日 10:17</span>

  <!-- 新闻列表 -->
  <a href="https://techcrunch.com/2026/...">
    <div class="font-[500]">1. 巴里·迪勒信任山姆·奥特曼...</div>
    <div class="text-[14px] text-[#7a7b79]">莎拉·佩雷斯</div>
  </a>
</div>
```

## 解析要点

1. **找卡片**：`div` with `class` containing both `bg-card` AND `max-w`
2. **来源名**：从子级 `<img alt="XXX logo">` 的 alt 属性提取
3. **时间戳**：`span` with class containing `text-blue-600`
4. **新闻标题**：`a > div.font-[500]` 内，去掉开头的 `^\d+\.?\s*` 序号
5. **作者**：`a > div.text-[14px]`
6. **外链判断**：href 以 `http` 开头且包含来源域名

## 支持的来源域名

```
techcrunch.com/202  → TechCrunch
36kr.com/           → 36Kr
github.com/         → GitHub Trending
news.mit.edu        → MIT News
a16z.com            → A16Z
openai.com          → OpenAI
anthropic.com       → Anthropic
huggingface.co      → Hugging Face
arxiv.org           → arXiv
producthunt.com     → Product Hunt
news.ycombinator.com → Hacker News
```

## sourceList 数据结构

在页面 HTML 里的位置：`<script>self.__next_f.push([...])` 中内嵌 React 渲染树，key 是 `sourceList`（但在 Hermes 环境直接解析 HTML 即可，不需要从 JS 提取）。
