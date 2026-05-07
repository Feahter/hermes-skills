---
name: office-toolkit
slug: office-toolkit
version: 1.0.0
description: "Unified skill for Microsoft Office documents — spreadsheets (.xlsx, .xlsm, .csv, .tsv) and Word documents (.docx). Use when the user wants to create, read, edit, or manipulate any Office file. Trigger on any mention of Excel, Word, spreadsheet, .xlsx, .docx, CSV, or requests for professional document deliverables with formatting (tables of contents, headings, page numbers, letterheads, charts, formulas). Handles tabular data processing, spreadsheet formula work, and polished Word document generation. Do NOT use for PDFs, Google Sheets/Docs, or non-Office formats."
prerequisites:
  env_vars:
    xlsx: []
    docx: []
license: Proprietary
metadata:
  hermes:
    tags: [Office, Excel, Word, Spreadsheet, DOCX, CSV, Productivity]
    category: productivity
  combinator:
    triggers:
      - Excel
      - xlsx
      - 电子表格
      - 表格处理
      - spreadsheet
      - CSV
      - 表格数据
      - Word doc
      - word document
      - .docx
      - Word document creation
      - 专业文档
      - 报告
      - 备忘录
      - letterhead
---

# Office Toolkit

Handles all Microsoft Office documents — spreadsheets (.xlsx, .csv, .tsv) and Word documents (.docx).

## Spreadsheet (xlsx)

### Requirements for Outputs
- **Professional font**: Arial or Times New Roman unless instructed otherwise
- **Zero formula errors**: #REF!, #DIV/0!, #VALUE!, #N/A, #NAME? are all forbidden
- **Preserve templates**: Match existing format/style conventions when editing

### Quick Reference
| Task | Approach |
|------|----------|
| Read/analyze | `openpyxl`, `pandas` |
| Create from scratch | `openpyxl` with proper formatting |
| Edit existing | Unpack → edit → repack via `openpyxl` |
| Convert formats | `pandas` for CSV ↔ Excel |
| Clean messy data | `pandas` restructuring |

### Tools
- `openpyxl`: Excel file creation and editing
- `pandas`: Data processing, CSV handling, chart data prep

---

## Word Document (docx)

### Overview
A .docx file is a ZIP archive containing XML files.

### Quick Reference
| Task | Approach |
|------|----------|
| Read/analyze content | `pandoc` or unpack for raw XML |
| Create new document | `docx-js` (JavaScript) — see Creating New Documents below |
| Edit existing document | Unpack → edit XML → repack |

### Tools
- `pandoc`: Format conversion, content extraction
- `docx-js`: Programmatic Word document creation
- XML editing: For tracked changes, comments, find-and-replace

## Related Skills
- `powerpoint`: For .pptx presentation files
- `pdf`: For PDF conversion and editing

---

## Usage Guidelines

**Trigger for spreadsheets when:** user mentions Excel, xlsx, spreadsheet, CSV, or wants data tables/charts computed.

**Trigger for Word docs when:** user mentions Word, docx, report, memo, letter, template, or wants formatted professional documents.

**Do NOT trigger when:** primary deliverable is a PDF, HTML report, Python script, database pipeline, or Google Sheets/Docs integration.
