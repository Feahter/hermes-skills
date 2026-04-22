---
name: academic-paper
description: "Academic paper writing skill with 12-agent pipeline. v2.4: LaTeX output formatting hardening — mandatory apa7 class, text justification fix, table column width formula, bilingual abstract centering, standardized font stack, PDF must compile from LaTeX. Supports IMRaD, literature review, theoretical, case study, policy brief, and conference paper structures. APA 7.0 (default), Chicago, MLA, IEEE, Vancouver citation formats. Bilingual abstracts (zh-TW + EN). Multi-format output (LaTeX, DOCX, PDF, Markdown). Triggers on: write paper, academic paper, paper outline, write abstract, revise paper, check citations, convert to LaTeX, guide my paper, parse reviews, revision roadmap, 寫論文, 學術論文, 論文大綱, 寫摘要, 修改論文, 檢查引用, 引導我寫論文, 帶我規劃論文, 逐章規劃, 論文架構, 審查意見, 修訂路線圖."
metadata:
  version: "2.4"
  last_updated: "2026-03-08"
---

# Academic Paper — Academic Paper Writing Agent Team

A general-purpose academic paper writing tool — 12-agent pipeline covering all disciplines, with higher education domain as the default reference. v2.4 hardens LaTeX output formatting: mandatory `apa7` document class for APA 7.0, text justification override for `man` mode, table column width formula with `\tabcolsep` deduction, bilingual abstract centering, standardized font stack (Times New Roman + Source Han Serif TC VF + Courier New), and PDF compilation via tectonic.

## Quick Start

**Minimal command:**
```
Write a paper on the impact of AI on higher education quality assurance
```

```
Write a paper on the impact of declining birth rates on private university management strategies
```

**Execution flow:**
1. Configuration interview — paper type, discipline, citation format, output format
2. Literature search — systematic search strategy, source screening
3. Architecture design — paper structure, outline, word count allocation
4. Argumentation construction — claim-evidence chains, logical flow
5. Full-text drafting — section-by-section draft, register adjustment
6. Citation compliance + bilingual abstract (parallel)
7. Peer review — five-dimension scoring, revision suggestions
8. Output formatting — LaTeX/DOCX/PDF/Markdown

---

## Trigger Conditions

### Trigger Keywords

**English**: write paper, academic paper, paper outline, write abstract, revise paper, literature review paper, check citations, convert to LaTeX, convert format, format paper, conference paper, journal article, thesis chapter, research paper, guide my paper, help me plan my paper, step by step paper, draft manuscript, write methodology, write discussion, parse reviews, revision roadmap, help me with my revision, I got reviewer comments, convert citations

**繁體中文**: 寫論文, 學術論文, 論文大綱, 寫摘要, 修改論文, 文獻回顧論文, 檢查引用, 轉 LaTeX, 轉換格式, 研討會論文, 期刊文章, 學位論文, 研究論文, 引導我寫論文, 幫我規劃論文, 逐步寫論文, 寫方法論, 寫討論, 審查意見, 修訂路線圖, 幫我修改, 我收到審查意見, 轉換引用格式

### Plan Mode Activation

Activate `plan` mode (Socratic chapter-by-chapter guidance) when the user's **intent** matches any of the following patterns, **regardless of language**. Detect meaning, not exact keywords.

**Intent signals** (any one is sufficient):
1. User wants to be guided or led through paper writing, not just given a finished paper
2. User asks for step-by-step or chapter-by-chapter planning
3. User expresses uncertainty about how to start or structure a paper
4. User is a first-time paper writer or explicitly says they are a beginner
5. User has research results but doesn't know how to turn them into a paper
6. User wants to think through each section before writing

**Default rule**: When intent is ambiguous between `plan` and `full`, **prefer `plan`** — it is safer to guide a user who needs help than to produce a paper they can't use. The user can always switch to `full` later.

**Example triggers** (illustrative, not exhaustive):
"guide my paper", "help me plan my paper", "I don't know how to start", 「引導我寫論文」「幫我規劃論文」, or equivalent in any language

### Does NOT Trigger

| Scenario | Use Instead |
|----------|-------------|
| Deep research / fact-checking (not paper writing) | `deep-research` |
| Reviewing a paper (structured review) | `academic-paper-reviewer` |
| Full research-to-paper pipeline | `academic-pipeline` |

### Distinction from `deep-research`

| Feature | `academic-paper` | `deep-research` |
|---------|-------------------|-----------------|
| Primary output | Publishable paper draft | Research report |
| Structure | Journal-ready (IMRaD, etc.) | APA 7.0 report |
| Citation | Multi-format (APA/Chicago/MLA/IEEE/Vancouver) | APA 7.0 only |
| Abstract | Bilingual (zh-TW + EN) | Single language |
| Peer review | Simulated 5-dimension review | Editorial review |
| Output format | LaTeX/DOCX/PDF/Markdown | Markdown only |
| Revision loop | Max 2 rounds with targeted feedback | Max 2 rounds |

---

## Agent Team (12 Agents)

| # | Agent | Role | Phase |
|---|-------|------|-------|
| 1 | `intake_agent` | Configuration interview: paper type, discipline, journal, citation format, output format, language, word count; Handoff detection; Plan mode simplified interview | Phase 0 |
| 2 | `literature_strategist_agent` | Search strategy design, source screening, annotated bibliography, literature matrix | Phase 1 |
| 3 | `structure_architect_agent` | Paper structure selection, detailed outline, word count allocation, evidence mapping | Phase 2 |
| 4 | `argument_builder_agent` | Argument construction, claim-evidence chains, logical flow, counter-argument handling; Plan mode argument stress test | Phase 3 / Plan Step 3 |
| 5 | `draft_writer_agent` | Section-by-section full draft writing, discipline register adjustment, word count tracking | Phase 4 |
| 6 | `citation_compliance_agent` | Citation format verification, reference list completeness, DOI checking | Phase 5a |
| 7 | `abstract_bilingual_agent` | Bilingual abstract (zh-TW + EN), 5-7 keywords each | Phase 5b |
| 8 | `peer_reviewer_agent` | Simulated double-blind review, five-dimension scoring, revision suggestions (max 2 rounds) | Phase 6 |
| 9 | `formatter_agent` | Convert to LaTeX/DOCX/PDF/Markdown, journal formatting, cover letter, citation format conversion (APA 7 / Chicago / MLA / IEEE / Vancouver) | Phase 7 |
| 10 | `socratic_mentor_agent` | Plan mode Socratic mentor: chapter-by-chapter guidance, convergence criteria (4 signals), question taxonomy (4 types), INSIGHT extraction | Plan Step 0-3 |
| 11 | `visualization_agent` | Parse paper data and generate publication-quality figure code (Python matplotlib / R ggplot2) with APA 7.0 formatting, colorblind-safe palettes, and LaTeX integration | Phase 4 / Phase 7 |
| 12 | `revision_coach_agent` | Parse unstructured reviewer comments into structured Revision Roadmap; classify, map, and prioritize comments; works standalone without prior pipeline execution | Revision-Coach mode |

---

## Output Formats

### Text Formats
LaTeX (.tex + .bib), DOCX (via Pandoc), PDF (via LaTeX or Pandoc), Markdown.

### Figures
When the paper contains quantitative results, the `visualization_agent` can generate publication-ready figures in Python (matplotlib/seaborn) or R (ggplot2) with APA 7.0 formatting and colorblind-safe palettes. Figures are delivered as runnable code + LaTeX `\includegraphics` integration code. See `references/statistical_visualization_standards.md` for chart type decision trees and code templates.

### Citation Formats
APA 7.0 (default), Chicago (Author-Date or Notes-Bibliography), MLA 9, IEEE, Vancouver. The `formatter_agent` supports late-stage citation format conversion between any two supported formats via "Convert citations to [format]".

---

## Orchestration Workflow (8 Phases)

```
P0: CONFIG (Interactive)     -> intake_agent -> Paper Configuration Record
     ** User confirms **
P1: RESEARCH                 -> literature_strategist_agent -> Search Strategy + Source Corpus
     ** User reviews (optional) **
P2: ARCHITECTURE             -> structure_architect_agent -> Outline + Evidence Map
     ** User approves **
P3: ARGUMENTATION            -> argument_builder_agent -> Argument Blueprint
P4: DRAFTING                 -> draft_writer_agent -> Complete Draft
P5a: CITATIONS (||)          -> citation_compliance_agent -> Citation Audit Report
P5b: ABSTRACT (||)           -> abstract_bilingual_agent -> Bilingual Abstract + Keywords
P6: PEER REVIEW              -> peer_reviewer_agent -> Review Report (max 2 loops -> back to P4)
P7: FORMAT                   -> formatter_agent -> Final Output (LaTeX/DOCX/PDF/Markdown)
```

### Checkpoint Rules
1. **P0 -> P1**: User confirms Paper Configuration Record
2. **P2 -> P3**: User approves outline
3. **P6**: Max 2 revision loops; unresolved -> "Acknowledged Limitations"; Critical-severity blocks P7
4. User can skip P1 if providing own sources

---

## Operational Modes (9 Modes)

See `references/mode_selection_guide.md` for details.

| Mode | Trigger | Agents | Output |
|------|---------|--------|--------|
| `full` | "Write a paper" | All 9 (+ 11 if quantitative) | Complete paper draft (with figures if applicable) |
| `outline-only` | "Paper outline" | 1->2->3 | Detailed outline + evidence map |
| `revision` | "Revise paper" | 8->5->6 | Revised draft with tracked changes (uses `templates/revision_tracking_template.md`) |
| `abstract-only` | "Write abstract" | 1->7 | Bilingual abstract + keywords |
| `lit-review` | "Literature review" | 1->2 | Annotated bibliography + synthesis |
| `format-convert` | "Convert to LaTeX" / "Convert citations to [format]" | 9 only | Formatted document; includes citation format conversion (APA 7 / Chicago / MLA / IEEE / Vancouver) |
| `citation-check` | "Check citations" | 6 only | Citation error report |
| `plan` | "guide my paper" / "help me plan my paper" | 1->10->3->4 | Chapter Plan + INSIGHT Collection |
| `revision-coach` | "parse reviews" / "revision roadmap" / "I got reviewer comments" | 12 only | Revision Roadmap + optional Tracking Template + Response Letter Skeleton |

### Quick Mode Selection Guide

| Your Situation | Recommended Mode |
|----------------|-----------------|
| Starting from scratch with a clear RQ | `full` |
| Need help planning before writing | `plan` |
| Just need an outline | `outline-only` |
| Have a draft, received review feedback | `revision` |
| Have unstructured reviewer comments | `revision-coach` |
| Just need an abstract | `abstract-only` |
| Need to check/fix citations | `citation-check` |
| Need to convert format (LaTeX, DOCX) or citation style | `format-convert` |
| Want a systematic literature review paper | `lit-review` |

Not sure? Start with `plan` — it will guide you step by step.

### Mode Selection Logic

| User Input | Mode |
|------------|------|
| "Write a paper on..." | `full` |
| "Paper outline for..." | `outline-only` |
| "Revise this paper..." | `revision` |
| "Write an abstract..." | `abstract-only` |
| "Literature review on..." | `lit-review` |
| "Convert to LaTeX / citations to..." | `format-convert` |
| "Check citations..." | `citation-check` |
| "guide my paper" / "help me plan..." | `plan` |
| "I got reviewer comments" / "parse reviews" | `revision-coach` |


---

### Plan Mode: Chapter-by-Chapter Guided Planning

Core: Senior doctoral advisor guides users through each chapter via Socratic dialogue. Instead of writing directly, use probing questions to help users clarify their argument. Full detail in `agents/socratic_mentor_agent.md`.

```
Step 0: RESEARCH READINESS CHECK
    +-> Confirm materials: literature, data, research question
    -> If foundation lacking, recommend deep-research first

Step 1: THESIS CRYSTALLIZATION
    +-> Probe core thesis and counter-argument potential
    Extract [INSIGHT: thesis_statement]

Step 2: CHAPTER-BY-CHAPTER NEGOTIATION
    +-> Per chapter (Intro -> Lit Review -> Method -> Results -> Discussion -> Conclusion):
        - At least 2 rounds of Socratic dialogue
        - Extract Chapter Summary after each
    +-> [structure_architect_agent] -> Complete outline from all summaries

Step 3: ARGUMENT STRESS TEST
    +-> [socratic_mentor_agent + argument_builder_agent]
        -> Probe weakest points, test reversed arguments
    Output: Chapter Plan + INSIGHT Collection
    -> User can switch to full mode to produce paper
```

---

## Handoff Protocol: deep-research -> academic-paper

`intake_agent` automatically detects deep-research materials (RQ Brief / Bibliography / Synthesis / INSIGHT Collection) and skips redundant steps. See `deep-research/SKILL.md` Handoff Protocol for the complete handoff material format.

---

## Failure Paths

See `references/failure_paths.md` for details. Quick reference:

| Failure Scenario | Handling Strategy |
|---------|---------|
| Insufficient research foundation | Recommend running `deep-research` first |
| Wrong paper structure selected | Return to Phase 2, suggest alternative structure |
| Word count significantly over/under target | Identify problematic chapters, suggest trimming/expansion |
| Citation format entirely wrong | Re-run the entire citation phase |
| Peer review rejection | Analyze rejection reasons, suggest major revision or restructuring |
| Plan mode not converging | Suggest switching to outline-only mode |
| Incomplete handoff materials | List missing items, suggest supplementing or re-running |
| User abandons midway | Save completed Chapter Plan |

---

## Full Academic Pipeline

See `academic-pipeline/SKILL.md` for the complete workflow.

---

## Phase 0: Configuration Interview

See `agents/intake_agent.md` for the complete field definitions of the Phase 0 configuration interview. The interview covers 9 items: paper type, discipline, target journal, citation format, output format, language, abstract, word count, and existing materials. Outputs a Paper Configuration Record, awaiting user confirmation.

---

## Agent File References

| Agent | Definition File |
|-------|----------------|
| intake_agent | `agents/intake_agent.md` |
| literature_strategist_agent | `agents/literature_strategist_agent.md` |
| structure_architect_agent | `agents/structure_architect_agent.md` |
| argument_builder_agent | `agents/argument_builder_agent.md` |
| draft_writer_agent | `agents/draft_writer_agent.md` |
| citation_compliance_agent | `agents/citation_compliance_agent.md` |
| abstract_bilingual_agent | `agents/abstract_bilingual_agent.md` |
| peer_reviewer_agent | `agents/peer_reviewer_agent.md` |
| formatter_agent | `agents/formatter_agent.md` |
| socratic_mentor_agent | `agents/socratic_mentor_agent.md` |
| visualization_agent | `agents/visualization_agent.md` |
| revision_coach_agent | `agents/revision_coach_agent.md` |

---

## Reference Files

| Reference | Purpose | Used By |
|-----------|---------|---------|
| `references/apa7_extended_guide.md` | APA 7th extended guide (extends deep-research version) | citation_compliance, draft_writer, formatter |
| `references/apa7_chinese_citation_guide.md` | APA 7.0 Chinese citation complete specification (Taiwan academic conventions) | citation_compliance, draft_writer, formatter |
| `references/citation_format_switcher.md` | Multi-citation format switching rules (including Chinese formats) | citation_compliance, formatter |
| `references/paper_structure_patterns.md` | 6 paper structure patterns | structure_architect, intake |
| `references/academic_writing_style.md` | Academic writing style guide | draft_writer, peer_reviewer |
| `references/hei_domain_glossary.md` | Higher education terminology bilingual glossary | all agents (domain context) |
| `references/journal_submission_guide.md` | Journal submission guide | formatter, intake |
| `references/abstract_writing_guide.md` | Abstract writing guide | abstract_bilingual |
| `references/latex_template_reference.md` | LaTeX template reference | formatter |
| `references/failure_paths.md` | Failure path map (12 scenarios + handling strategies) | all agents |
| `references/mode_selection_guide.md` | 8 mode selection guide + transition paths | intake |
| `references/credit_authorship_guide.md` | CRediT 14 roles + ICMJE + AI policy + contribution matrix | intake, formatter, draft_writer |
| `references/funding_statement_guide.md` | Taiwan/international funding formats + statement templates | intake, formatter, draft_writer |
| `references/statistical_visualization_standards.md` | APA 7.0 figure guidelines, accessible color palettes, chart type decision tree, matplotlib/ggplot2 code templates | visualization |

Also references from `deep-research`:
- `deep-research/references/apa7_style_guide.md` — base APA 7 reference (this skill extends, not duplicates)

---

## Templates

| Template | Purpose |
|----------|---------|
| `templates/imrad_template.md` | IMRaD structure template |
| `templates/literature_review_template.md` | Literature review template |
| `templates/case_study_template.md` | Case study template |
| `templates/theoretical_paper_template.md` | Theoretical paper template |
| `templates/policy_brief_template.md` | Policy brief template |
| `templates/conference_paper_template.md` | Conference paper template |
| `templates/latex_article_template.tex` | LaTeX starter template |
| `templates/bilingual_abstract_template.md` | Bilingual abstract template |
| `templates/credit_statement_template.md` | Author x Role contribution matrix + CRediT statement output |
| `templates/funding_statement_template.md` | Funding source registration + statement output |
| `templates/revision_tracking_template.md` | Systematic tracker for reviewer comments and resolutions during revision (4 status types: RESOLVED, DELIBERATE_LIMITATION, UNRESOLVABLE, REVIEWER_DISAGREE) |

---

## Examples

| Example | Demonstrates |
|---------|-------------|
| `examples/imrad_hei_example.md` | Complete IMRaD paper example (higher education domain, English) |
| `examples/literature_review_example.md` | Literature review paper example |
| `examples/plan_mode_guided_writing.md` | Plan mode chapter-by-chapter guided dialogue example (blended learning topic) |
| `examples/chinese_paper_example.md` | Complete Chinese academic paper example (IMRaD, Chinese APA 7.0 citations) |
| `examples/revision_mode_example.md` | Revision mode complete workflow: peer review response + revision comparison table |

---

## Quality Standards

| # | Standard | Detail |
|---|----------|--------|
| W1 | Claims with citations | Every claim has a citation or paper's own data |
| W2 | Zero citation orphans | In-text <-> reference list must perfectly match |
| W3 | Consistent register | Academic tone appropriate for discipline |
| W4 | Logical flow | Clear transitions between paragraphs/sections |
| W5 | Word count compliance | Within +/-10% of target |
| A1 | Independent abstract writing | zh-TW and EN composed independently (not mechanical translation) |
| A2 | Structural alignment | Both abstracts cover same key points in same order |
| A3 | Keywords | 5-7 per language reflecting core concepts |
| A4 | Word count | EN: 150-300 words; zh-TW: 300-500 characters |
| C1 | Format compliance | 100% adherence to selected citation style |
| C2 | DOI inclusion | Every source with DOI must include it |
| C3 | Currency | Flag sources older than 10 years (unless seminal) |
| C4 | Self-citation ratio | Flag if >15% |
| P1 | Five-dimension scoring | Originality 20%, Method Rigour 25%, Evidence 25%, Argument 15%, Writing 15% |
| P2 | Actionable feedback | Every criticism includes specific suggestion |
| P3 | Max 2 revision rounds | Unresolved items become Acknowledged Limitations |
| M1 | AI disclosure | Every paper includes AI tool usage statement |
| M2 | Limitations section | Explicitly discuss study limitations |
| M3 | Ethics statement | When applicable (human subjects, sensitive data) |

---

## Output Language

Follows the user's language. Academic terminology is kept in English. Bilingual abstracts are always provided regardless of the main text language.

---

## Integration with Other Skills

| Combo | Result |
|-------|--------|
| `academic-paper` + `deep-research` | Research phase -> paper writing phase (auto-handoff) |
| `academic-paper` + `tw-hei-intelligence` | Evidence-based HEI paper with real MOE data |
| `academic-paper` + `report-to-website` | Interactive web version of the paper |
| `academic-paper` + `notebooklm-slides-generator` | Presentation slides from paper |
| `academic-paper` + `academic-paper-reviewer` | Peer review -> revision loop |

---

## Version History

|| Version | Date | Changes ||
|---------|------|---------|
|| 2.4 | 2026-03-08 | LaTeX output hardening: `apa7` class, `ragged2e` justification, table width formula, bilingual abstract centering, font stack, tectonic PDF compilation ||
|| 2.3 | 2026-03-08 | Added `visualization_agent` (11th) and `revision_coach_agent` (12th); Socratic convergence criteria; citation format conversion (APA 7 ↔ Chicago ↔ MLA ↔ IEEE ↔ Vancouver); Quick Mode Selection Guide; 9th mode: revision-coach ||
|| 2.0 | 2026-02 | NEW plan mode, deep-research handoff, Chinese APA 7.0 citation guide, failure paths, mode selection guide ||
|| 1.0 | 2026-01 | Initial release: 9-agent pipeline, 6 paper types, 5 citation formats, bilingual abstracts, multi-format output ||
