# Peekaboo 命令勘误

本文档记录 peekaboo 实际行为与文档/猜测不符之处，持续更新。

---

## ⚠️ 已发现错误

### dock 子命令 — 位置参数，非 `--name`

**错误写法（文档常见）：**
```bash
peekaboo dock launch --name Safari
peekaboo dock right-click --name Finder
peekaboo dock hide --name Safari
```

**正确写法（实测）：**
```bash
peekaboo dock launch Safari
peekaboo dock right-click Finder
peekaboo dock hide Safari
```

**来源：** `peekaboo dock --help`，`--name` 不是有效选项。

---

### click — 用 `--coords` 而非 `--at`

**错误写法：**
```bash
peekaboo click --at 100,100
```

**正确写法：**
```bash
peekaboo click --coords 100,100
```

**来源：** `peekaboo click --help` 确认。

---

## 🔍 验证方法

```bash
peekaboo <subcommand> --help   # 查看子命令真实语法
peekaboo tools                  # 列出所有子命令
```

---

## 已知良好命令（实测✓）

| 命令 | 状态 |
|------|------|
| `peekaboo see --app iTerm2 --json` | ✅ snapshot_id 在 `data.snapshot_id` |
| `peekaboo click --coords 100,100` | ✅ |
| `peekaboo list apps` | ✅ |
| `peekaboo permissions status` | ✅ |
| `peekaboo permissions grant` | ✅ |
