---
name: markitdown
description: "MarkItDown - 文档转Markdown工具，支持PDF/PPT/Word/图片"
triggers:
  - "markitdown"
  - "文档转换"
  - "PDF转Markdown"
  - "PPT转Markdown"
source:
  url: https://github.com/markitdown/markitdown
  auto_generated: false
---

# MarkItDown Skill

MarkItDown将各类文档转换为Markdown格式，支持PDF、PPT、Word、图片等。

## 触发场景
- "PDF转Markdown"
- "Word转Markdown"
- "PPT转Markdown"
- "文档转换"
- "提取文档内容"

## 基础用法

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("document.pdf")
print(result.text_content)

# 也支持URL
result = md.convert("https://example.com/document.docx")
```

## 支持格式
- PDF
- Word (.docx)
- PowerPoint (.pptx)
- Excel (.xlsx)
- HTML
- 图片（OCR提取文字）
- 音频（提取歌词）

## 安装

```bash
pip install markitdown

# 可选依赖
pip install python-pptx python-docx pdfplumber
pip install flask  # Web服务
```

## CLI用法

```bash
# 命令行转换
markitdown document.pdf -o output.md

# 指定输出
markitdown input.docx --output result.md
```

## Web服务

```python
from markitdown import MarkItDown
from flask import Flask, request, jsonify

app = Flask(__name__)
md = MarkItDown()

@app.route('/convert', methods=['POST'])
def convert():
    file = request.files['file']
    result = md.convert(file)
    return jsonify({'content': result.text_content})
```

## 与其他Skills联动
- 配合 `pdf` 做PDF处理
- 配合 `docx` 做Word处理
- 配合 `xlsx` 做Excel处理
- 配合 `rag-search` 做内容索引
