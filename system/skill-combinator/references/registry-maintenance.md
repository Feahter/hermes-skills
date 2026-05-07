# Skill Registry 维护指南

**问题信号**：磁盘 skill 数量 ≠ 注册表数量，或组合涌现结果异常。

---

## 快速诊断

```bash
# 1. 比对磁盘数量 vs 注册表数量
python3 -c "
import json
from pathlib import Path
hermes_home = Path.home() / '.hermes/skills'
registry = json.load(open(Path.home() / '.hermes/.skill_registry.json'))['skills']
disk = len(list(hermes_home.rglob('SKILL.md')))
print(f'Disk SKILL.md: {disk}')
print(f'Registry entries: {len(registry)}')
print(f'Diff: {disk - len(registry)}')
"

# 2. 检查无效路径（skill 删了但注册表未更新）
python3 -c "
import json
from pathlib import Path
registry = json.load(open(Path.home() / '.hermes/.skill_registry.json'))['skills']
for name, info in registry.items():
    if not Path(info.get('path','')).exists():
        print(f'ORPHAN: {name} → {info.get(\"path\")}')
"

# 3. 检查注册表指向嵌套路径的 skill（插件副本）
python3 -c "
import json
from pathlib import Path
registry = json.load(open(Path.home() / '.hermes/.skill_registry.json'))['skills']
for name, info in registry.items():
    if '/plugins/' in info.get('path',''):
        print(f'NESTED PLUGIN: {name} → {info.get(\"path\")}')
"
```

---

## 已知的 Orphan 模式

| 模式 | 原因 | 清理方式 |
|------|------|---------|
| **空顶级目录** | skill 删除后目录残留 | `rm -rf ~/.hermes/skills/{empty_dir}` |
| **嵌套插件副本** | 插件安装到 skill 内部 | `rm -rf ~/.hermes/skills/{category}/{skill}/plugins/` |
| **小写 skill.md** | 命名大小写不一致（Mac） | glob 不匹配，只进磁盘不进注册表 |
| **.git 等隐藏目录** | 误传入 skill 目录 | glob 排除 `.` 开头的目录（已在 pipeline 中修复） |

---

## 清理流程

```
1. 运行快速诊断（上面第 1 步）
2. 若 diff > 0：
   a. 运行第 2 步找无效路径
   b. 手动清理空目录和插件副本
   c. 重新扫描：python3 ~/.hermes/scripts/skill_registry.py
3. 验证：diff 应为 0
4. 测试组合涌现：python3 ~/.hermes/skills/system/skill-combinator/scripts/pipeline.py "测试"
```

---

## 本次发现（2026-05-04）

- 空残留目录：gaming, inference-sh, gifs, diagramming, scripts, domain
- 嵌套副本：`productivity/frontend-slides/plugins/frontend-slides/skills/frontend-slides/`（完整 skill 包被复制进自身）
- Registry 清理后：204 skills，全部路径有效

---

## 重建注册表

```bash
python3 ~/.hermes/scripts/skill_registry.py
```

> 注意：重建是覆盖式写入，无需手动清空缓存。只需确保磁盘 SKILL.md 干净后再执行。
