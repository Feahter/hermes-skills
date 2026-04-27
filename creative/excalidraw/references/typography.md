# Typography in Excalidraw

Excalidraw supports text elements, but lacks an automatic text measurement system. All positioning must be calculated manually.

## Text Positioning Rules

### Absolute Positioning (Required)

Unlike web-based diagramming tools, Excalidraw text **does not flow**. You must calculate:

1. **Position** (`x`, `y`) — top-left corner of the text bounding box
2. **Size** (`width`, `height`) — manually set, must encompass the rendered text

### Font Size Guidelines

| Use Case | Min fontSize |
|----------|-------------|
| Body / labels | 16 |
| Primary titles | 20 |
| Secondary annotations only | 14 (sparingly) |

**Never use fontSize below 14.**

### Text Width Estimation

No DOM access in Excalidraw JSON. Estimate manually:

```
avgCharWidth ≈ fontSize × 0.55   // for proportional fonts at common sizes
estimatedWidth ≈ text.length × avgCharWidth
```

**For mixed CJK (Chinese/Japanese/Korean):** Each CJK character ≈ `fontSize × 1.0` (full-width). For mixed text, use a weighted average.

### Vertical Rhythm

| Line height multiplier | Result at fontSize=16 |
|----------------------|----------------------|
| 1.2× | 19px per line |
| 1.5× | 24px per line |
| 1.8× | 29px per line |

```javascript
const FONT_SIZE = 16;
const LINE_HEIGHT = 1.5;
const LINE_SPACING = FONT_SIZE * LINE_HEIGHT; // 24px

// Multi-line text positioning
const lines = text.split('\n');
lines.forEach((line, i) => {
  const y = startY + i * LINE_SPACING;
  // emit text element at (x, y)
});
```

## Pretext for Precise Measurement

When generating Excalidraw JSON programmatically, use `@chenglou/pretext` to calculate exact text dimensions before emitting elements.

### Workflow

```
1. prepare(text, fontSpec)           // one-time measurement
2. layout(prepared, maxWidth, lineHeight)  // returns { height, lineCount }
3. Calculate element positions using height/lineCount
4. Emit Excalidraw JSON with correct dimensions
```

### Example

```javascript
import { prepare, layout } from '@chenglou/pretext';

function measureForExcalidraw(text, fontSize = 16) {
  const prepared = prepare(text, `${fontSize}px Inter, sans-serif`);
  const { height, lineCount } = layout(prepared, 200, fontSize * 1.5);
  return {
    height,
    lineCount,
    width: 200, // maxWidth you passed
    lineHeight: fontSize * 1.5,
  };
}

// Use in element generation
const label = measureForExcalidraw('Label text', 16);
// Emit Excalidraw text element with:
// x: calculated left edge
// y: calculated top edge
// width: label.width
// height: label.height
```

## Common Patterns

### Labeled Arrow (text on arrow)

```javascript
// Arrow with centered label above it
const arrowLength = Math.sqrt(dx*dx + dy*dy);
const labelWidth = estimateWidth(labelText, 16);
const labelX = startX + dx/2 - labelWidth/2;
const labelY = startY + dy/2 - 12; // 12 ≈ half line height above arrow center
```

### Multi-line Box Label

```javascript
const LINE_H = 24; // 16px * 1.5
const lines = wrapText(label, maxWidth, 16);
lines.forEach((line, i) => {
  // emit text element at (boxX + padding, boxY + headerHeight + i * LINE_H)
});
```

## Important

- Excalidraw text elements **do not auto-resize**. Set `width` large enough to contain the text.
- `autoResize: true` on text elements enables auto-width, but Excalidraw recalculates on load — your initial `width`/`height` values are approximate hints.
- For diagrams with lots of text, pre-calculate with Pretext in your generation script before emitting JSON.
