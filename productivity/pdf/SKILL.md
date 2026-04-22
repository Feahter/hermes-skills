---
name: pdf
description: Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs, combining or merging multiple PDFs into one, splitting PDFs apart, rotating pages, adding watermarks, creating new PDFs, filling PDF forms, encrypting/decrypting PDFs, extracting images, and OCR on scanned PDFs to make them searchable. If the user mentions a .pdf file or asks to produce one, use this skill.
license: Proprietary. LICENSE.txt has complete terms
metadata:
  combinator:
    triggers: ['PDF', 'pdf', '读取PDF', '合并PDF', '提取PDF']
---

# PDF Processing Guide

## Overview

This guide covers essential PDF processing operations. For command-line reference, see `references/commands.md`. For form filling, see `FORMS.md`.

## Quick Start

```python
from pypdf import PdfReader, PdfWriter

# Read a PDF
reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")

# Extract text
text = ""
for page in reader.pages:
    text += page.extract_text()
```

## Python Libraries

### pypdf - Merge, Split, Rotate

#### Merge PDFs
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### Split PDF
```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

#### Extract Metadata
```python
reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"Title: {meta.title}, Author: {meta.author}")
```

#### Rotate Pages
```python
reader = PdfReader("input.pdf")
writer = PdfWriter()
page = reader.pages[0]
page.rotate(90)  # Rotate 90 degrees clockwise
writer.add_page(page)
with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - Text and Table Extraction

#### Extract Text with Layout
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### Extract Tables
```python
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

### reportlab - Create PDFs

> **MANDATORY RULE** — Every reportlab script MUST import and call `setup_chinese_pdf()` first:
> ```python
> import sys, os
> sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))
> from setup_chinese_pdf import setup_chinese_pdf
> cn_font, styles = setup_chinese_pdf()  # MUST be the very first reportlab operation
> ```

#### Basic PDF Creation
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))
from setup_chinese_pdf import setup_chinese_pdf

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

cn_font, styles = setup_chinese_pdf()  # First!

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter
c.setFont(cn_font, 12)
c.drawString(100, height - 100, "Hello World!")
c.save()
```

#### PDF with Multiple Pages
```python
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

cn_font, styles = setup_chinese_pdf()  # First!

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
story = [
    Paragraph("Report Title", styles['Title']),
    Spacer(1, 12),
    Paragraph("Body text content", styles['Normal']),
    PageBreak(),
    Paragraph("Page 2", styles['Heading1']),
]
doc.build(story)
```

#### Chinese/CJK Content
```python
cn_font, styles = setup_chinese_pdf()

# All styles already use CJK font — use directly
title = Paragraph("报告标题", styles['Title'])
body = Paragraph("中文内容可以正常显示", styles['Normal'])
```

**Never** use Helvetica, Times-Roman, Courier for Chinese text — they render as solid black boxes.

#### Windows PowerShell with Chinese
On Windows, use base64 encoding to pass Chinese content through the shell:
```powershell
python -c "import base64,os; open('gen_report.py','wb').write(base64.b64decode('<PAYLOAD>'))"
python gen_report.py
```

## Command-Line Tools

See `references/commands.md` for complete reference. Quick examples:

```bash
# Extract text
pdftotext input.pdf output.txt

# Merge PDFs
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# Split
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf

# Rotate
qpdf input.pdf output.pdf --rotate=+90:1

# Extract images
pdfimages -j input.pdf output_prefix
```

## Common Tasks

### Extract Text from Scanned PDFs
```python
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path('scanned.pdf')
text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image) + "\n\n"
print(text)
```

### Add Watermark
```python
from pypdf import PdfReader, PdfWriter

watermark = PdfReader("watermark.pdf").pages[0]
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### Password Protection
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()
for page in reader.pages:
    writer.add_page(page)
writer.encrypt("userpassword", "ownerpassword")
with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

## Quick Reference

| Task | Best Tool | Code/Command |
|------|-----------|--------------|
| Merge PDFs | pypdf | `writer.add_page(page)` |
| Split PDFs | pypdf | Loop pages, one per file |
| Extract text | pdfplumber | `page.extract_text()` |
| Extract tables | pdfplumber | `page.extract_tables()` |
| Create PDFs | reportlab | Canvas or Platypus |
| Command line | qpdf | `qpdf --empty --pages ...` |
| OCR | pytesseract | Convert to image first |
| Fill forms | pypdf/pdf-lib | See FORMS.md |

## Next Steps

- For complete command reference, see `references/commands.md`
- For form filling, see `FORMS.md`
- For advanced features (pypdfium2, pdf-lib, JavaScript), see `REFERENCE.md`
