# Pretext 精排集成 — SVG 卡片文本换行

## 核心问题

当前 SVG 卡片使用字符数估算换行，无法处理**中英文混合宽度差异**和**实际字体度量**，导致：

- 英文严重压缩或溢出
- 中文字符间距不均
- 固定行高估算导致段落高度不准

## Pretext 集成方案

使用 `@chenglou/pretext` 做精确文本度量，在生成 SVG 之前计算真实高度，再生成正确尺寸的 SVG。

### 步骤 1：CDN 引入

```html
<script type="module">
import { prepare, layout } from 'https://cdn.jsdelivr.net/npm/@chenglou/pretext@+esm';
</script>
```

### 步骤 2：Node.js 环境测量（生成时）

```javascript
// generate-card.mjs
import { prepare, layout } from '@chenglou/pretext';

function measureText(text, fontSize, fontFamily, maxWidth) {
  const prepared = prepare(text, `${fontSize}px ${fontFamily}`);
  const { height, lineCount } = layout(prepared, maxWidth, fontSize * 1.5);
  return { height, lineCount };
}

// 示例
const result = measureText('你的多行文本内容', 15, 'KingHwa_OldSong', 400);
console.log(result.height, result.lineCount); // → 精确高度，行数
```

### 步骤 3：动态计算 SVG 高度

```javascript
function generateCard(config) {
  const { title, content, author, template } = config;

  // 用 Pretext 精确测量每段高度
  const contentMetrics = measureText(content, 15, 'KingHwa_OldSong', 400);
  const titleMetrics  = measureText(title, 20, 'KingHwa_OldSong', 400);

  // 动态总高度 = 标题高度 + 分隔线 + 内容高度 + 分隔线 + 作者
  const totalHeight =
    titleMetrics.height  + 30 +   // 标题 + 间距
    2 +                           // 分隔线
    contentMetrics.height + 30 +  // 内容 + 间距
    2 +                           // 分隔线
    20;                           // 作者

  // 生成精确高度的 SVG
  return `<svg width="${template.width}" height="${totalHeight}" ...>`;
}
```

### 步骤 4：中英混合换行处理

Pretext 基于 Unicode 字符宽度计算（`Intl.Segmenter`），自动处理：

- 全角中文标点：`，`、`。`、`！`
- 半角英文/数字：`a`、`1`
- 混合段落：`Hello世界 123 你好`

无需手动指定"中文几个算一个字"，Pretext 内部以 grapheme 粒度分割。

## 模板高度查表（快速路径）

对于标准模板，可用预计算经验值：

| 模板 | 字体大小 | 最大宽度 | 每行高度 | 每字符宽度(中) | 每字符宽度(英) |
|------|---------|---------|---------|--------------|--------------|
| Literary | 15px | 400px | 22px | 15px | 8px |
| Logic | 14px | 560px | 21px | 14px | 7px |
| Concept | 15px | 480px | 22px | 15px | 8px |
| Micro | 14px | 400px | 21px | 14px | 7px |

```
估算行数 = ceil(字符数 × 平均字符宽度 / 最大宽度)
估算高度 = 估算行数 × 每行高度
```

**推荐做法：** 精确场景（正式发布/打印）用 Pretext 测量；草稿预览用估算查表。

## 实现检查清单

- [ ] 安装 `@chenglou/pretext`（如在 Node.js 环境）：`npm install @chenglou/pretext`
- [ ] 浏览器端使用 ESM CDN（如 Vite/Playwright 场景）
- [ ] `prepare()` 只调一次，`layout()` 按需多次调用
- [ ] 生成 SVG 前调用测量，获取真实高度后再写 `<svg>` 标签
- [ ] 英文/数字混合时，`averageCharWidth` 取中英混合平均值（如 0.55）
