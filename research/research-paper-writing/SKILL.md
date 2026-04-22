---
name: research-paper-writing
title: Research Paper Writing Pipeline
description: End-to-end pipeline for writing ML/AI research papers — from experiment design through analysis, drafting, revision, and submission. Covers NeurIPS, ICML, ICLR, ACL, AAAI, COLM. Integrates automated experiment monitoring, statistical analysis, iterative writing, and citation verification.
version: 1.1.0
author: Orchestra Research
license: MIT
dependencies: [semanticscholar, arxiv, habanero, requests, scipy, numpy, matplotlib, SciencePlots]
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Research, Paper Writing, Experiments, ML, AI, NeurIPS, ICML, ICLR, ACL, AAAI, COLM, LaTeX, Citations, Statistical Analysis]
    category: research
    related_skills: [arxiv, ml-paper-writing, subagent-driven-development, plan]
    requires_toolsets: [terminal, files]

---

# Research Paper Writing Pipeline

End-to-end pipeline for producing publication-ready ML/AI research papers targeting **NeurIPS, ICML, ICLR, ACL, AAAI, and COLM**. This skill covers the full research lifecycle: experiment design, execution, monitoring, analysis, paper writing, review, revision, and submission.

This is **not a linear pipeline** — it is an iterative loop. Results trigger new experiments. Reviews trigger new analysis. The agent must handle these feedback loops.

```
┌─────────────────────────────────────────────────────────────┐
│                    RESEARCH PAPER PIPELINE                  │
│                                                             │
│  Phase 0: Project Setup ──► Phase 1: Literature Review      │
│       │                          │                          │
│       ▼                          ▼                          │
│  Phase 2: Experiment     Phase 5: Paper Drafting ◄──┐      │
│       Design                     │                   │      │
│       │                          ▼                   │      │
│       ▼                    Phase 6: Self-Review      │      │
│  Phase 3: Execution &           & Revision ──────────┘      │
│       Monitoring                 │                          │
│       │                          ▼                          │
│       ▼                    Phase 7: Submission               │
│  Phase 4: Analysis ─────► (feeds back to Phase 2 or 5)     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## When To Use This Skill

Use this skill when:
- **Starting a new research paper** from an existing codebase or idea
- **Designing and running experiments** to support paper claims
- **Writing or revising** any section of a research paper
- **Preparing for submission** to a specific conference or workshop
- **Responding to reviews** with additional experiments or revisions
- **Converting** a paper between conference formats
- **Writing non-empirical papers** — theory, survey, benchmark, or position papers (see [Paper Types Beyond Empirical ML](#paper-types-beyond-empirical-ml))
- **Designing human evaluations** for NLP, HCI, or alignment research
- **Preparing post-acceptance deliverables** — posters, talks, code releases

## Core Philosophy

1. **Be proactive.** Deliver complete drafts, not questions. Scientists are busy — produce something concrete they can react to, then iterate.
2. **Never hallucinate citations.** AI-generated citations have ~40% error rate. Always fetch programmatically. Mark unverifiable citations as `[CITATION NEEDED]`.
3. **Paper is a story, not a collection of experiments.** Every paper needs one clear contribution stated in a single sentence. If you can't do that, the paper isn't ready.
4. **Experiments serve claims.** Every experiment must explicitly state which claim it supports. Never run experiments that don't connect to the paper's narrative.
5. **Commit early, commit often.** Every completed experiment batch, every paper draft update — commit with descriptive messages. Git log is the experiment history.

### Proactivity and Collaboration

**Default: Be proactive. Draft first, ask with the draft.**

| Confidence Level | Action |
|-----------------|--------|
| **High** (clear repo, obvious contribution) | Write full draft, deliver, iterate on feedback |
| **Medium** (some ambiguity) | Write draft with flagged uncertainties, continue |
| **Low** (major unknowns) | Ask 1-2 targeted questions via `clarify`, then draft |

| Section | Draft Autonomously? | Flag With Draft |
|---------|-------------------|-----------------|
| Abstract | Yes | "Framed contribution as X — adjust if needed" |
| Introduction | Yes | "Emphasized problem Y — correct if wrong" |
| Methods | Yes | "Included details A, B, C — add missing pieces" |
| Experiments | Yes | "Highlighted results 1, 2, 3 — reorder if needed" |
| Related Work | Yes | "Cited papers X, Y, Z — add any I missed" |

**Block for input only when**: target venue unclear, multiple contradictory framings, results seem incomplete, explicit request to review first.

---

## Phase 0: Project Setup

**Goal**: Establish the workspace, understand existing work, identify the contribution.

### Step 0.1: Explore the Repository

```bash
ls -la
find . -name "*.py" | head -30
find . -name "*.md" -o -name "*.txt" | xargs grep -l -i "result\|conclusion\|finding"
```

Look for: `README.md`, `results/`, `configs/`, `.bib` files, draft documents.

### Step 0.2: Organize the Workspace

```
workspace/
  paper/               # LaTeX source, figures, compiled PDFs
  experiments/         # Experiment runner scripts
  code/                # Core method implementation
  results/             # Raw experiment results
  tasks/               # Task/benchmark definitions
  human_eval/          # Human evaluation materials
```

### Step 0.3: Set Up Version Control

```bash
git init && git checkout -b paper-draft
```

Commit after every experiment batch: `"Add Monte Carlo constrained results (5 runs, Sonnet 4.6, policy memo task)"`

### Step 0.4: Identify the Contribution

Articulate before writing:
- **The What**: What is the single thing this paper contributes?
- **The Why**: What evidence supports it?
- **The So What**: Why should readers care?

### Step 0.5: Compute Budget

Estimate API/GPU costs, human evaluation costs. Add 30-50% contingency. Track spend as experiments run.

### Step 0.6: Multi-Author Coordination

Use Overleaf (browser-based), Git + LaTeX, or Overleaf + Git sync. Assign section ownership, agree on notation conventions early.

---

## Phase 1: Literature Review

**Goal**: Find related work, identify baselines, gather citations.

### Step 1.1: Identify Seed Papers

Start from existing citations in codebase:
```bash
grep -r "arxiv\|doi\|cite" --include="*.md" --include="*.bib"
find . -name "*.bib"
```

### Step 1.2: Search for Related Work

Use `web_search` for broad discovery, `web_extract` for fetching papers:
```
web_search("[main technique] + [application domain] site:arxiv.org")
web_extract("https://arxiv.org/abs/2303.17651")
```

Use iterative breadth-then-depth search (2-3 rounds). Delegate parallel queries via `delegate_task`.

### Step 1.3: Verify Every Citation (MANDATORY)

**NEVER generate BibTeX from memory. ALWAYS fetch programmatically.**

```
Citation Verification:
1. SEARCH → Query Semantic Scholar with keywords
2. VERIFY → Confirm paper exists in 2+ sources
3. RETRIEVE → Get BibTeX via DOI content negotiation
4. VALIDATE → Confirm the claim you're citing appears in the paper
5. ADD → Add verified BibTeX to bibliography
If ANY step fails → mark as [CITATION NEEDED]
```

See [references/citation-workflow.md](references/citation-workflow.md) for API code.

### Step 1.4: Organize Related Work

Group by **methodology**, not paper-by-paper:
- **Good**: "One line of work uses X's assumption [refs] whereas we use Y's assumption because..."
- **Bad**: "Smith et al. introduced X. Jones et al. introduced Y. We combine both."

---

## Phase 2: Experiment Design

**Goal**: Design experiments that directly support paper claims.

### Step 2.1: Map Claims to Experiments

| Claim | Experiment | Expected Evidence |
|-------|-----------|-------------------|
| "Our method outperforms baselines" | Main comparison (Table 1) | Win rate, statistical significance |
| "Effect is larger for weaker models" | Model scaling study | Monotonic improvement curve |
| "Convergence requires scope constraints" | Constrained vs unconstrained | Convergence rate comparison |

**Rule**: If an experiment doesn't map to a claim, don't run it.

### Step 2.2: Design Baselines

- **Naive baseline**: Simplest possible approach
- **Strong baseline**: Best known existing method
- **Ablation baselines**: Your method minus one component
- **Compute-matched baselines**: Same compute budget, different allocation

### Step 2.3: Define Evaluation Protocol

Specify: **Metrics** (with direction), **aggregation**, **statistical tests**, **sample sizes**.

### Step 2.4: Write Experiment Scripts

Follow patterns: incremental saving, artifact preservation, separation of generation/evaluation/visualization.

See [references/experiment-patterns.md](references/experiment-patterns.md) for complete patterns.

### Step 2.5: Design Human Evaluation (If Applicable)

Required for: NLP, HCI, alignment papers where automated metrics don't capture what you care about.

Key decisions: annotator type, scale (pairwise > Likert for LLM outputs), sample size (min 100 items, 3+ annotators), agreement metric (Krippendorff's alpha), platform (Prolific for quality).

See [references/human-evaluation.md](references/human-evaluation.md) for complete guide.

---

## Phase 3: Experiment Execution & Monitoring

**Goal**: Run experiments reliably, monitor progress, recover from failures.

### Step 3.1: Launch Experiments

```bash
nohup python run_experiment.py --config config.yaml > logs/experiment_01.log 2>&1 &
echo $!
```

### Step 3.2: Set Up Cron Monitoring

Use `cronjob` tool for periodic status checks. Respond `[SILENT]` if nothing changed.

### Step 3.3: Handle Failures

| Failure | Detection | Recovery |
|---------|-----------|----------|
| API rate limit | 402/429 errors | Wait, re-run (scripts skip completed work) |
| Process crash | PID gone | Re-run from last checkpoint |
| Timeout | Stuck, no log progress | Kill and skip |

**Key**: Scripts check for existing results and skip completed work.

### Step 3.4: Maintain Experiment Journal

Track the exploration tree (not just git commits):
```json
{"id": "exp_003", "parent": "exp_001", "hypothesis": "...", "config": {...}, 
 "key_metrics": {"win_rate": 0.85}, "analysis": "...", "next_steps": [...]}
```

---

## Phase 4: Result Analysis

**Goal**: Extract findings, compute statistics, identify the story.

### Step 4.1: Aggregate Results

Write analysis scripts that load result files, compute per-task and aggregate metrics.

### Step 4.2: Statistical Significance

Always compute: **error bars** (std dev or std error), **confidence intervals** (95% CI), **pairwise tests** (McNemar's), **effect sizes** (Cohen's d or h).

See [references/experiment-patterns.md](references/experiment-patterns.md) for implementations.

### Step 4.3: Identify the Story

Answer: (1) What is the main finding? (2) What surprised you? (3) What failed? (4) What follow-up is needed?

**Handling negative results**: Frame around analysis of why, or reframe as understanding contribution. Venues for null results: NeurIPS Datasets & Benchmarks, TMLR, workshops.

### Step 4.4: Create Figures and Tables

- **Figures**: Vector PDF, colorblind-safe (Okabe-Ito), self-contained captions
- **Tables**: `booktabs`, bold best value, direction symbols ($\uparrow$/$\downarrow$)

### Step 4.5: Write the Experiment Log (Bridge to Writeup)

Create `experiment_log.md` with: contribution statement, experiments run (with claim mapping), figures list, failed experiments, open questions.

**Git discipline**: Commit this alongside results.

---

## Iterative Refinement: Strategy Selection

Choose the right refinement approach based on your situation:

| Your Situation | Strategy | Why |
|---------------|----------|-----|
| Mid-tier model + constrained task | **Autoreason** | Generation-evaluation gap is widest |
| Frontier model + unconstrained | **Critique-and-revise** or single pass | Model self-evaluates well enough |
| Code with test cases | **Autoreason (code variant)** | Structured analysis before fixing |

**Core insight**: Autoreason's value depends on the gap between a model's generation and self-evaluation capability.

### Autoreason Loop (Summary)

1. **Critic** → finds problems (no fixes)
2. **Author B** → revises based on critique
3. **Synthesizer** → merges A and B
4. **Judge Panel** → 3 blind CoT judges rank via Borda count
5. **Convergence** → A wins k=2 consecutive passes

Key: k=2 convergence, CoT judges always, temperature 0.8 authors / 0.3 judges.

See [references/autoreason-methodology.md](references/autoreason-methodology.md) for complete prompts and details.

---

## Phase 5: Paper Drafting

> **📖 Full Phase 5 Reference**: [references/phase5-drafting.md](references/phase5-drafting.md)
>
> The detailed Phase 5 content (LaTeX templates, figures, tables, TikZ diagrams, latexdiff, SciencePlots, writing workflow, abstract formula, section-by-section guidance, etc.) has been moved to the reference document above.

**Goal**: Write a complete, publication-ready paper.

### The Narrative Principle

**The single most critical insight**: Your paper is not a collection of experiments — it's a story with one clear contribution supported by evidence.

Every successful ML paper centers on "the narrative": a short, rigorous, evidence-based technical story with a takeaway readers care about.

**Three Pillars** (must be crystal clear by end of introduction):

| Pillar | Description | Test |
|--------|-------------|------|
| **The What** | 1-3 specific novel claims | Can you state them in one sentence? |
| **The Why** | Rigorous empirical evidence | Do experiments distinguish your hypothesis from alternatives? |
| **The So What** | Why readers should care | Does this connect to a recognized community problem? |

**If you cannot state your contribution in one sentence, you don't yet have a paper.**

### Context Management for Large Projects

A paper project with 50+ experiment files, multiple result directories, and extensive literature notes can exceed the agent's context window.

| Drafting Task | Load Into Context | Do NOT Load |
|---------------|------------------|-------------|
| Writing Introduction | `experiment_log.md`, contribution statement, 5-10 most relevant paper abstracts | Raw result JSONs, full experiment scripts |
| Writing Methods | Experiment configs, pseudocode, architecture description | Raw logs, results from other experiments |
| Writing Results | `experiment_log.md`, result summary tables, figure list | Full analysis scripts, intermediate data |
| Writing Related Work | Organized citation notes, .bib file | Experiment files, raw PDFs |
| Revision pass | Full paper draft, specific reviewer concerns | Everything else |

**Principles**:
- `experiment_log.md` is the primary context bridge — it summarizes everything needed without loading raw data
- Load one section's context at a time when delegating
- Summarize, don't include raw files. For a 200-line result JSON, load a 10-line summary table

### Writing Workflow

```
Paper Writing Checklist:
- [ ] Step 1: Define the one-sentence contribution
- [ ] Step 2: Draft Figure 1 (core idea or most compelling result)
- [ ] Step 3: Draft abstract (5-sentence formula)
- [ ] Step 4: Draft introduction (1-1.5 pages max)
- [ ] Step 5: Draft methods
- [ ] Step 6: Draft experiments & results
- [ ] Step 7: Draft related work
- [ ] Step 8: Draft conclusion & discussion
- [ ] Step 9: Draft limitations (REQUIRED by all venues)
- [ ] Step 10: Plan appendix (proofs, extra experiments, details)
- [ ] Step 11: Complete paper checklist
- [ ] Step 12: Final review
```

### Two-Pass Refinement Pattern

When drafting with an AI agent, use a **two-pass** approach:

**Pass 1 — Write + immediate refine per section:**
Write a complete draft, then immediately refine it in the same context. This catches local issues while the section is fresh.

**Pass 2 — Global refinement with full-paper context:**
After all sections are drafted, revisit each section with awareness of the complete paper. This catches cross-section issues: redundancy, inconsistent terminology, narrative flow, and gaps.

```
Second-pass refinement prompt:
"Review the [SECTION] in the context of the complete paper.
- Does it fit with the rest of the paper? Are there redundancies?
- Is terminology consistent with Introduction and Methods?
- Does the narrative flow from the previous section and into the next?
Make minimal, targeted edits. Do not rewrite from scratch."
```

### Time Allocation

Spend approximately **equal time** on each of:
1. The abstract
2. The introduction
3. The figures
4. Everything else combined

**Why?** Most reviewers form judgments before reaching your methods. Readers encounter: title → abstract → introduction → figures → maybe the rest.

### LaTeX Error Checklist

Append this to every refinement prompt:

```
LaTeX Quality Checklist:
- [ ] No unenclosed math symbols ($ signs balanced)
- [ ] Only reference figures/tables that exist (\ref matches \label)
- [ ] No fabricated citations (\cite matches entries in .bib)
- [ ] Every \begin{env} has matching \end{env}
- [ ] No HTML contamination (</end{figure}> instead of \end{figure})
- [ ] No unescaped underscores outside math mode
- [ ] No duplicate \label definitions
- [ ] Numbers in text match actual experimental results
```

### Step 5.1: Abstract (5-Sentence Formula)

From Sebastian Farquhar (DeepMind):

```
1. What you achieved: "We introduce...", "We prove...", "We demonstrate..."
2. Why this is hard and important
3. How you do it (with specialist keywords for discoverability)
4. What evidence you have
5. Your most remarkable number/result
```

**Delete** generic openings like "Large language models have achieved remarkable success..."

### Step 5.2: Figure 1

Figure 1 is the second thing most readers look at (after abstract). Draft it before writing the introduction.

| Figure 1 Type | When to Use |
|---------------|-------------|
| **Method diagram** | New architecture or pipeline |
| **Results teaser** | One compelling result tells the whole story |
| **Problem illustration** | The problem is unintuitive |
| **Conceptual diagram** | Abstract contribution needs visual grounding |

**Rules**: Figure 1 must be understandable without reading any text. The caption alone should communicate the core idea.

### Step 5.3: Introduction (1-1.5 pages max)

Must include:
- Clear problem statement
- Brief approach overview
- 2-4 bullet contribution list (max 1-2 lines each in two-column format)
- Methods should start by page 2-3

### Step 5.4: Methods

Enable reimplementation:
- Conceptual outline or pseudocode
- All hyperparameters listed
- Architectural details sufficient for reproduction
- Present final design decisions; ablations go in experiments

### Step 5.5: Experiments & Results

For each experiment, explicitly state:
- **What claim it supports**
- How it connects to main contribution
- What to observe: "the blue line shows X, which demonstrates Y"

Requirements: error bars with methodology, hyperparameter search ranges, compute infrastructure, seed-setting methods.

### Step 5.6: Related Work

Organize methodologically, not paper-by-paper. Cite generously — reviewers likely authored relevant papers.

### Step 5.7: Limitations (REQUIRED)

All major conferences require this. Honesty helps:
- Reviewers are instructed not to penalize honest limitation acknowledgment
- Pre-empt criticisms by identifying weaknesses first
- Explain why limitations don't undermine core claims

### Step 5.8: Conclusion

- Restate the contribution in one sentence (different wording from abstract)
- Summarize key findings (2-3 sentences, not a list)
- Implications: what does this mean for the field?
- Future work: 2-3 concrete next steps

**Do NOT** introduce new results or claims in the conclusion.

### Writing Style

**Gopen & Swan's 7 Principles**:

| Principle | Rule |
|-----------|------|
| Subject-verb proximity | Keep subject and verb close |
| Stress position | Place emphasis at sentence ends |
| Topic position | Put context first, new info after |
| Old before new | Familiar info → unfamiliar info |
| One unit, one function | Each paragraph makes one point |
| Action in verb | Use verbs, not nominalizations |
| Context before new | Set stage before presenting |

**Word choice**:
- Be specific: "accuracy" not "performance"
- Eliminate hedging: drop "may" unless genuinely uncertain
- Consistent terminology throughout

See [references/writing-guide.md](references/writing-guide.md) for full explanations with examples.

### Professional LaTeX Packages

Add to any paper for professional quality (compatible with all major conference style files):

```latex
% Typography
\usepackage{microtype}              % Microtypographic improvements

% Tables
\usepackage{booktabs}               % Professional table rules
\usepackage{siunitx}                % Decimal alignment in tables

% Figures
\usepackage{graphicx}               % Include graphics
\usepackage{subcaption}             % Subfigures with (a), (b), (c)

% Diagrams
\usepackage{tikz}                   % Programmable vector diagrams
\usepackage[ruled,vlined]{algorithm2e}  % Professional pseudocode

% Cross-references
\usepackage{cleveref}               % Smart references (load AFTER hyperref)
```

### Template Quick Reference

| Conference | Main File | Style File | Page Limit |
|------------|-----------|------------|------------|
| NeurIPS 2025 | `main.tex` | `neurips.sty` | 9 pages |
| ICML 2026 | `example_paper.tex` | `icml2026.sty` | 8 pages |
| ICLR 2026 | `iclr2026_conference.tex` | `iclr2026_conference.sty` | 9 pages |
| ACL 2025 | `acl_latex.tex` | `acl.sty` | 8 pages |
| AAAI 2026 | `aaai2026-unified-template.tex` | `aaai2026.sty` | 7 pages |

Templates in `templates/` directory. See [templates/README.md](templates/README.md) for compilation instructions.

### Tables and Figures

**Tables** — use `booktabs`:

```latex
\begin{tabular}{lcc}
\toprule
Method & Accuracy $\uparrow$ & Latency $\downarrow$ \\
\midrule
Baseline & 85.2 & 45ms \\
\textbf{Ours} & \textbf{92.1} & 38ms \\
\bottomrule
\end{tabular}
```

**Figures**:
- **Vector graphics** (PDF) for all plots: `plt.savefig('fig.pdf')`
- **Colorblind-safe palettes** (Okabe-Ito or Paul Tol)
- Verify **grayscale readability**
- **Self-contained captions** — reader should understand without main text

### latexdiff for Revision Tracking

Essential for rebuttals — generates marked-up PDF showing changes:

```bash
latexdiff paper_v1.tex paper_v2.tex > paper_diff.tex
pdflatex paper_diff.tex

# For multi-file projects
latexdiff --flatten paper_v1.tex paper_v2.tex > paper_diff.tex
```

### SciencePlots for Publication-Quality Figures

```bash
pip install SciencePlots
```

```python
import matplotlib.pyplot as plt
import scienceplots

with plt.style.context(['science', 'no-latex']):
    fig, ax = plt.subplots(figsize=(3.5, 2.5))  # Single-column
    ax.plot(x, y, label='Ours', color='#0072B2')
    fig.savefig('paper/fig_results.pdf', bbox_inches='tight')
```

**Standard figure sizes**: Single column: `(3.5, 2.5)`, Double column: `(7.0, 3.0)`

### Ethics & Broader Impact Statement

Most venues require this. **What to include**:

| Component | Content | Required By |
|-----------|---------|-------------|
| **Positive societal impact** | How your work benefits society | NeurIPS, ICML |
| **Potential negative impact** | Misuse risks, specific failure modes | NeurIPS, ICML |
| **Environmental impact** | Compute carbon footprint | ICML, NeurIPS |
| **LLM disclosure** | Was AI used? | ICLR (mandatory), ACL |

**Common mistakes**:
- Writing "we foresee no negative impacts" (almost never true)
- Being vague: "this could be misused" without specifying how
- Forgetting to disclose LLM use at venues that require it

### Page Budget Management

When over the page limit:

| Cut Strategy | Saves | Risk |
|-------------|-------|------|
| Move proofs to appendix | 0.5-2 pages | Low |
| Condense related work | 0.5-1 page | Medium |
| Combine tables with subfigures | 0.25-0.5 page | Low |
| Reduce figure sizes | 0.25-0.5 page | High |

**Do NOT**: reduce font size, change margins, or remove required sections (limitations, broader impact).

---

## Phase 6: Self-Review & Revision

**Goal**: Simulate the review process before submission.

### Step 6.1: Simulate Reviews (Ensemble Pattern)

Generate N=3-5 independent reviews from different models/perspectives. **Default to negative bias**.

```json
{
  "summary": "2-3 sentence summary",
  "strengths": ["..."],
  "weaknesses": ["most critical weakness", ...],
  "soundness": 1-4,
  "presentation": 1-4,
  "contribution": 1-4,
  "overall": 1-10,
  "confidence": 1-5
}
```

Then feed to meta-reviewer for aggregation.

### Step 6.1b: Visual Review Pass (VLM)

Check compiled PDF for: figure quality, figure-caption alignment, layout issues, table formatting, grayscale readability.

### Step 6.2: Prioritize Feedback

| Priority | Action |
|----------|--------|
| **Critical** (technical flaw) | Must fix. May require new experiments |
| **High** (clarity, missing ablation) | Should fix in revision |
| **Medium** | Fix if time allows |
| **Low** | Note for future work |

### Step 6.3: Rebuttal Writing

Format: Point-by-point. Address every concern, lead with strongest responses, include new results if run during rebuttal. Use `latexdiff` for marked-up PDF.

See [references/reviewer-guidelines.md](references/reviewer-guidelines.md) for detailed rebuttal template.

---

## Phase 7: Submission Preparation

**Goal**: Final checks, formatting, and submission.

### Step 7.1: Conference Checklist

See [references/checklists.md](references/checklists.md) for NeurIPS 16-item, ICML broader impact, ICLR LLM disclosure, ACL limitations, universal pre-submission checklist.

### Step 7.2: Anonymization Checklist

```bash
- [ ] No author names/affiliations in PDF
- [ ] No acknowledgments (add after acceptance)
- [ ] Self-citations in third person: "Smith et al. [1] showed..."
- [ ] Use Anonymous GitHub for code links
- [ ] No institutional logos in figures
```

### Step 7.3: Pre-Compilation Validation

```bash
chktex main.tex -q -n2 -n24 -n13 -n1  # Lint LaTeX
# Verify citations exist in .bib
# Verify figures exist on disk
# Check for duplicate \label definitions
```

### Step 7.4: Final Compilation

```bash
rm -f *.aux *.bbl *.blg *.log *.out *.pdf
latexmk -pdf main.tex
```

### Step 7.5: Conference-Specific Requirements

| Venue | Special Requirements |
|-------|---------------------|
| **NeurIPS** | Paper checklist in appendix |
| **ICML** | Broader Impact Statement (after conclusion) |
| **ICLR** | LLM disclosure required |
| **ACL** | Mandatory Limitations section |
| **AAAI** | Strict style file — no modifications |

### Step 7.6: Conference Resubmission

Never copy LaTeX preambles between templates. Start fresh with target template, copy only content.

| From → To | Page Change | Key Adjustments |
|-----------|-------------|-----------------|
| NeurIPS → ICML | 9 → 8 | Cut 1 page, add Broader Impact |
| ICML → ICLR | 8 → 9 | Expand, add LLM disclosure |
| Any → AAAI | varies → 7 | Significant cuts |

### Step 7.7: arXiv Strategy

- Double-blind venues: Post to arXiv **after** submission deadline
- ICLR: Allows arXiv posting before submission
- Workshop papers: arXiv fine anytime

### Step 7.8: Research Code Packaging

Release clean, runnable code. Structure: README, requirements.txt, setup.py, LICENSE, configs/, src/, scripts/, data/.

---

## Phase 8: Post-Acceptance Deliverables

**Goal**: Maximize impact through presentation and community engagement.

### Step 8.1: Conference Poster

Size: typically 24"x36" or A0. Content: title, 1-sentence contribution, method figure, 2-3 key results. Top-left to bottom-right flow.

### Step 8.2: Conference Talk

| Type | Duration | Content |
|------|----------|---------|
| Spotlight | 5 min | Problem, approach, one key result |
| Oral | 15-20 min | Full story with ablations, limitations |

One idea per slide. Minimize text. Include takeaway slide.

### Step 8.3: Blog Post / Social Media

Post within 1-2 days of appearing on proceedings. Twitter thread: lead with result, not method. Blog: 800-1500 words for ML practitioners.

---

## Workshop & Short Papers

Workshop papers (4-6 pages): lower completeness bar, interesting ideas, preliminary results. Target workshops for: early-stage feedback, negative results, position pieces.

ACL Short Papers (4 pages): pick ONE claim, support thoroughly. Don't compress a long paper.

---

## Paper Types Beyond Empirical ML

See [references/paper-types.md](references/paper-types.md) for detailed guidance:

- **Theory Papers**: Contribution is a theorem/bound. Structure: Intro → Preliminaries → Main Results → Proof Sketches → Discussion.
- **Survey Papers**: Contribution is organization/synthesis. Best venues: TMLR, JMLR, ACM Computing Surveys.
- **Benchmark Papers**: Contribution is the benchmark itself. Must fill genuine evaluation gap. NeurIPS Datasets & Benchmarks track.
- **Position Papers**: Contribution is an argument. Must engage with counterarguments. ICML position track, workshops.

---

## Hermes Agent Integration

### Related Skills

| Skill | When to Use | How to Load |
|-------|-------------|-------------|
| **arxiv** | Phase 1: arXiv search, BibTeX | `skill_view("arxiv")` |
| **subagent-driven-development** | Phase 5: parallel section drafting | `skill_view("subagent-driven-development")` |
| **plan** | Phase 0: structured plans | `skill_view("plan")` |
| **diagramming** | Phase 4-5: architecture diagrams | `skill_view("diagramming")` |
| **data-science** | Phase 4: interactive analysis | `skill_view("data-science")` |

### Tool Usage Patterns

**Experiment monitoring**:
```
terminal("ps aux | grep <pattern>")
→ terminal("tail -30 <logfile>")
→ execute_code("analyze results JSON")
→ terminal("git add -A && git commit -m '<msg>'")
→ send_message("Experiment complete: <summary>")
```

**Parallel section drafting**:
```
delegate_task("Draft the Methods section based on configs. Include pseudocode, 
  hyperparameters, architectural details. Write in LaTeX using neurips2025 template.")
```

### State Management

Use `todo` for granular progress tracking. Use `memory` for key decisions across sessions. Run session startup protocol on each connect.

### Cron Monitoring

Schedule periodic checks with `[SILENT]` protocol when nothing changed. Use deadline tracking for conference submissions.

---

## Reference Documents

| Document | Contents |
|----------|----------|
| [references/phase5-drafting.md](references/phase5-drafting.md) | **NEW: Full Phase 5 guide** — LaTeX templates, figures, tables, TikZ, latexdiff, SciencePlots, section-by-section drafting |
| [references/writing-guide.md](references/writing-guide.md) | Gopen & Swan 7 principles, Lipton word choice, Steinhardt precision, figure design |
| [references/citation-workflow.md](references/citation-workflow.md) | Citation APIs, CitationManager class |
| [references/checklists.md](references/checklists.md) | NeurIPS, ICML, ICLR, ACL requirements |
| [references/reviewer-guidelines.md](references/reviewer-guidelines.md) | Evaluation criteria, scoring, rebuttal template |
| [references/sources.md](references/sources.md) | Complete bibliography |
| [references/experiment-patterns.md](references/experiment-patterns.md) | Design patterns, McNemar's test, bootstrapped CIs |
| [references/autoreason-methodology.md](references/autoreason-methodology.md) | Autoreason loop, prompts, Borda scoring |
| [references/human-evaluation.md](references/human-evaluation.md) | Annotation guidelines, agreement metrics, IRB guidance |
| [references/paper-types.md](references/paper-types.md) | Theory, survey, benchmark, position papers |

### LaTeX Templates

Templates in `templates/` for: **NeurIPS 2025**, **ICML 2026**, **ICLR 2026**, **ACL**, **AAAI 2026**, **COLM 2025**.

See [templates/README.md](templates/README.md) for compilation instructions.

### Key External Sources

**Writing**: [Neel Nanda](https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp/highly-opinionated-advice-on-how-to-write-ml-papers) | [Sebastian Farquhar](https://sebastianfarquhar.com/on-research/2024/11/04/how_to_write_ml_papers/) | [Gopen & Swan](https://cseweb.ucsd.edu/~swanson/papers/science-of-writing.pdf)

**APIs**: [Semantic Scholar](https://api.semanticscholar.org/) | [CrossRef](https://www.crossref.org/) | [arXiv](https://info.arxiv.org/help/api/basics.html)

**Venues**: [NeurIPS](https://neurips.cc/) | [ICML](https://icml.cc/) | [ICLR](https://iclr.cc/) | [ACL](https://aclweb.org/)
