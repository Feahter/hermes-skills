# write-a-skill 核心规则（高影响字段规范）

以下三条规则直接影响 skill 的触发质量和可维护性，**起草时必须优先遵守**。

---

## 规则 1：Description 是 agent 唯一看到的决策依据

Description 是 agent 在加载 skill 时**唯一能看到的内容**——它出现在 `available_skills` 列表中，agent 凭此决定是否加载该 skill。

**格式要求（≤ 1024 chars）：**
- 第一句：功能描述（what it does）
- 第二句：触发条件（"Use when ..."）
- 第三人称，精确触发词

```
# Good
Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when user mentions PDFs, forms, or document extraction.

# Bad
Helps with documents.
```

**⚠️ 这条规则是 description-optimization.md 和 improve_description.py 的前提——不理解"description = 唯一决策依据"，eval 和优化都是盲目的。**

---

## 规则 2：SKILL.md ≤ 100 行

强制**渐进披露**。主文件只放最高频路径，细节下沉到 reference 文件。

- SKILL.md 超过 100 行 → 拆分到 `references/*.md`
- 单个 reference 文件超过 500 行 → 继续拆分

---

## 规则 3：何时加脚本

**加脚本的场景：**
- 操作是确定性的（验证、格式化）
- 同一段代码会被反复生成
- 错误需要显式处理

脚本节省 token，提高可靠性。**不确定要不要加时，不加。**

---

## 实践检查清单

起草完成后，逐项核对：

- [ ] Description 包含 triggers（"Use when..."）
- [ ] SKILL.md 行数 ≤ 100
- [ ] 无时间敏感信息
- [ ] 术语一致
- [ ] 有具体示例
- [ ] 引用层级不超过一层深
