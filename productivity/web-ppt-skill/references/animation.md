# 动画参考 · Animation

基于 Intersection Observer 的滚动触发动画系统。所有动画通过 `.reveal` 类触发。

---

## 基础动画原则

1. **滚动触发，而非时间触发** — Intersection Observer 检测 slide 进入视口
2. **交错延迟** — 子元素依次出现，制造节奏感
3. **克制使用** — 一页一个主动画，不过度

---

## 核心类

| 类 | 效果 |
|---|---|
| `.reveal` | 淡入 + 上移 30px |
| `.reveal-left` | 淡入 + 左移 |
| `.reveal-right` | 淡入 + 右移 |
| `.reveal-scale` | 淡入 + 缩放 |
| `.visible` | 由 JS 添加，表示元素已进入视口 |

---

## Reveal 基础动画

```css
.reveal {
  opacity: 0;
  transform: translateY(30px);
  transition:
    opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1),
    transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide.visible .reveal {
  opacity: 1;
  transform: translateY(0);
}
```

---

## 交错延迟

```css
.reveal:nth-child(1) { transition-delay: 0.1s; }
.reveal:nth-child(2) { transition-delay: 0.2s; }
.reveal:nth-child(3) { transition-delay: 0.3s; }
.reveal:nth-child(4) { transition-delay: 0.4s; }
.reveal:nth-child(5) { transition-delay: 0.5s; }
.reveal:nth-child(6) { transition-delay: 0.6s; }
```

---

## 叙事轴动画（慢节奏）

适合衬线+留白的叙事型内容：

```css
.reveal {
  transition-duration: 0.8s; /* 更慢 */
  transition-timing-function: cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
```

---

## 展示轴动画（快节奏）

适合非衬线+密度的展示型内容：

```css
.reveal {
  transition-duration: 0.4s;
  transition-timing-function: cubic-bezier(0.16, 1, 0.3, 1);
}
```

---

## 视差背景动画

Hero 页的 WebGL/渐变背景随滚动轻微视差：

```js
window.addEventListener('scroll', () => {
  const scrolled = window.scrollY;
  document.querySelector('.bg-canvas').style.transform = `translateX(${scrolled * 0.1}px)`;
});
```

---

## Ghost 文字动画

巨型背景字淡入（opacity: 0.06）：

```css
.ghost {
  animation: ghostFadeIn 1.2s ease-out forwards;
  animation-delay: 0.3s;
  opacity: 0;
}

@keyframes ghostFadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 0.06; transform: translateY(0); }
}
```

---

## 数字计数器动画

进入视口时数字从 0 滚动到目标值：

```js
function animateCount(el, target, duration = 1500) {
  let start = 0;
  const step = target / (duration / 16);
  const timer = setInterval(() => {
    start += step;
    if (start >= target) {
      el.textContent = target;
      clearInterval(timer);
    } else {
      el.textContent = Math.floor(start);
    }
  }, 16);
}
```

---

## 主题切换过渡

WebGL 背景在 hero 页之间平滑插值：

```js
// 读取当前 slide 的 data-theme，JS 控制器根据主题切换 shader 参数
const themeMap = {
  'light': { bg: '#f1efea', accent: '#0a0a0b' },
  'dark': { bg: '#0a0a0b', accent: '#f1efea' },
  'hero light': { bg: '#f1efea', opacity: 0.85 },
  'hero dark': { bg: '#0a0a0b', opacity: 0.15 }
};
```
