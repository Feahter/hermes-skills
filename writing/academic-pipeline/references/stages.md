# Pipeline Stages — Detailed Reference

This document provides comprehensive descriptions for each of the 9 pipeline stages.

---

## Stage 1: RESEARCH

**Skill Called**: `deep-research`
**Modes**: `socratic` | `full` | `quick`
**Entry**: No materials available
**Exit**: User confirmation checkpoint

### Description
Exploratory research phase using deep-research skill. The orchestrator does not conduct research—it dispatches the skill and manages the transition.

### Deliverables
| Deliverable | Description |
|-------------|-------------|
| RQ Brief | 1-2 page research question brief with objectives |
| Methodology | Proposed research methodology |
| Bibliography | Formatted reference list |
| Synthesis | Literature synthesis or research summary |

### Mode Selection
| User Type | Recommended Mode |
|-----------|-----------------|
| Novice / wants guidance | `socratic` |
| Experienced / wants direct output | `full` |
| Time-limited | `quick` |

### Handoff to Stage 2
Pass RQ Brief + Bibliography + Synthesis to `academic-paper` (plan/full mode).

---

## Stage 2: WRITE

**Skill Called**: `academic-paper`
**Modes**: `plan` | `full`
**Entry**: Research deliverables from Stage 1
**Exit**: User confirmation checkpoint

### Description
Paper drafting phase. Orchestrator dispatches academic-paper skill with research materials as input.

### Deliverables
| Deliverable | Description |
|-------------|-------------|
| Paper Draft | Full paper manuscript (structure varies by mode) |

### Mode Selection
| Mode | Description |
|------|-------------|
| `plan` | Socratic chapter-by-chapter guidance; user makes decisions at each section |
| `full` | AI generates complete paper draft autonomously |

### Handoff to Stage 2.5
Pass complete paper draft to `integrity_verification_agent` (Mode 1: pre-review).

---

## Stage 2.5: INTEGRITY (Pre-Review)

**Skill Called**: `integrity_verification_agent`
**Mode**: `pre-review`
**Entry**: Paper draft from Stage 2
**Exit**: PASS → Stage 3 / FAIL → fix → re-verify (max 3 rounds)

### Description
Mandatory integrity verification before review submission. Ensures all references, citations, data, and claims are not fabricated or erroneous.

### Verification Phases
| Phase | Scope | Requirement |
|-------|-------|-------------|
| A | Reference existence + bibliographic accuracy + ghost citations | 100% verification |
| B | Citation context spot-check | ≥30% of citations |
| C | Statistical data verification | 100% verification |
| D | Originality spot-check + self-plagiarism check | ≥30% spot-check |
| E | Claim verification (min 10 claims) | 30% spot-check |

### Pass Criteria
- Zero SERIOUS issues
- Zero MAJOR_DISTORTION verdicts
- Zero UNVERIFIABLE verdicts

### Result Handling
| Result | Action |
|--------|--------|
| PASS | Checkpoint → Stage 3 |
| FAIL | Produce correction list → fix items → re-verify |
| Still FAIL after 3 rounds | Notify user, list unverifiable items |

### Handoff to Stage 3
Pass verified paper + Integrity Report to `academic-paper-reviewer` (full mode).

---

## Stage 3: REVIEW (First Review)

**Skill Called**: `academic-paper-reviewer`
**Mode**: `full` (includes Devil's Advocate)
**Entry**: Verified paper from Stage 2.5
**Exit**: Editorial Decision checkpoint (MANDATORY)

### Review Team
| Role | Focus |
|------|-------|
| EIC (Editor-in-Chief) | Overall quality, structure, contribution |
| R1 (Reviewer 1) | Methodology |
| R2 (Reviewer 2) | Domain expertise |
| R3 (Reviewer 3) | Interdisciplinary connections |
| Devil's Advocate | Steel-man opposing arguments, identify weaknesses |

### Deliverables
| Deliverable | Description |
|-------------|-------------|
| 5 Review Reports | Individual reviews from each team member |
| Editorial Decision | Accept / Minor Revision / Major Revision / Reject |
| Revision Roadmap | Structured list of required changes |
| Socratic Revision Coaching | Guided dialogue to help user understand comments (max 8 rounds) |

### Decision Branches
| Decision | Next Stage |
|----------|------------|
| Accept | Stage 4.5 (FINAL INTEGRITY) |
| Minor Revision | Stage 4 (REVISE) with coaching |
| Major Revision | Stage 4 (REVISE) with coaching |
| Reject | Stage 2 (return to RESEARCH) or end pipeline |

### Handoff to Stage 4
Pass Revision Roadmap + paper to `academic-paper` (revision mode).

---

## Stage 4: REVISE

**Skill Called**: `academic-paper`
**Mode**: `revision`
**Entry**: Revision Roadmap + verified paper
**Exit**: User confirmation checkpoint

### Description
Address reviewer comments using Revision Roadmap as guide. Produces revised draft + Response to Reviewers document.

### Deliverables
| Deliverable | Description |
|-------------|-------------|
| Revised Draft | Paper with tracked changes |
| Response to Reviewers | Point-by-point response letter |

### Response Format (per comment)
```
Reviewer [N], Comment [M]:
[Original comment quote]

Response:
[Response explanation]

Changes made:
[Specific modification location and content]
(or: We respectfully disagree because... [rationale])
```

### Handoff to Stage 3'
Pass Revised Draft + Response to Reviewers to `academic-paper-reviewer` (re-review mode).

---

## Stage 3': RE-REVIEW (Second Review)

**Skill Called**: `academic-paper-reviewer`
**Mode**: `re-review`
**Entry**: Revised draft + Response to Reviewers + original Revision Roadmap
**Exit**: Editorial Decision checkpoint (MANDATORY)

### Description
Verification-focused review. Checks that all revision items were properly addressed and responses are consistent with actual changes.

### Deliverables
| Deliverable | Description |
|-------------|-------------|
| Verification Review Report | Revision response comparison table |
| New Issues List | Any newly identified issues |
| Editorial Decision | Accept / Minor / Major |

### Decision Branches
| Decision | Next Stage |
|----------|------------|
| Accept | Stage 4.5 (FINAL INTEGRITY) |
| Minor | Stage 4' (RE-REVISE) with Residual Coaching |
| Major | Stage 4' (RE-REVISE) with Residual Coaching |

### Handoff to Stage 4'
Pass new Revision Roadmap to `academic-paper` (revision mode).

---

## Stage 4': RE-REVISE

**Skill Called**: `academic-paper`
**Mode**: `revision`
**Entry**: New Revision Roadmap from Stage 3'
**Exit**: User confirmation checkpoint → Stage 4.5 (no return to review)

### Description
Final revision round addressing residual issues from Stage 3'. Maximum one re-revision allowed in pipeline.

### Key Constraint
**No return to review**: After Stage 4', pipeline proceeds directly to Stage 4.5 (FINAL INTEGRITY).

### Handoff to Stage 4.5
Pass final revised draft to `integrity_verification_agent` (Mode 2: final-check).

---

## Stage 4.5: FINAL INTEGRITY (Post-Revision)

**Skill Called**: `integrity_verification_agent`
**Mode**: `final-check`
**Entry**: Revised/re-revised draft
**Exit**: PASS (zero issues) → Stage 5 / FAIL → fix → re-verify

### Description
Final mandatory integrity verification before finalization. Must achieve 100% pass with zero issues.

### Verification Scope (Stricter than Stage 2.5)
| Phase | Scope | Requirement |
|-------|-------|-------------|
| A | Reference verification (including new references from revision) | 100% |
| B | Citation context verification | 100% (not spot-check) |
| C | Statistical data verification | 100% |
| D | Originality spot-check (newly added/modified paragraphs) | ≥50% (100% for new content) |
| E | Claim verification | 100% |

### Special Check
Compare with Stage 2.5 results to confirm all previous issues are resolved.

### Pass Criteria
- Zero SERIOUS issues
- Zero MAJOR_DISTORTION verdicts
- Zero UNVERIFIABLE verdicts
- **Must PASS with zero issues to proceed**

### Handoff to Stage 5
Pass final verified draft to `academic-paper` (format-convert mode).

---

## Stage 5: FINALIZE

**Skill Called**: `academic-paper`
**Mode**: `format-convert`
**Entry**: Final verified draft
**Exit**: MD + DOCX + (optional LaTeX) + PDF

### Description
Format paper for submission/publication. Mandatory formatting style selection.

### Workflow
```
1. Ask user: Which academic formatting style?
   - APA 7.0 / Chicago / IEEE / Other

2. Auto-produce: MD + DOCX

3. Ask about LaTeX:
   - Yes → Generate LaTeX (using corresponding document class)
   - No → Skip to PDF via Word

4. User confirms content correctness

5. Compile PDF via LaTeX + tectonic (NOT HTML-to-PDF)

6. Fonts: Times New Roman + Source Han Serif TC VF + Courier New
```

### Deliverables
| Deliverable | Format |
|-------------|--------|
| Final Paper | MD (primary) + DOCX |
| Final Paper (optional) | LaTeX |
| Final Paper | PDF (compiled from LaTeX) |

### Handoff to Stage 6
Pass all final deliverables to orchestrator for Process Summary generation.

---

## Stage 6: PROCESS SUMMARY

**Skill Called**: Orchestrator (auto-generated)
**Mode**: `auto`
**Entry**: All pipeline deliverables and session history
**Exit**: Process record MD + PDF

### Description
Automatically generates a Paper Creation Process Record documenting the complete human-AI collaboration history.

### Workflow
```
1. Ask user language preference:
   - Chinese (Traditional Chinese)
   - English
   - Both

2. Review session history and compile:
   - User's initial instructions (verbatim)
   - Key decision points and interventions
   - Direction corrections and reasons
   - Iteration count and review summaries
   - Intellectual insights raised by user
   - Quality requirement evolution
   - Pipeline statistics

3. Generate Markdown (MD)

4. Convert to LaTeX + compile PDF:
   - pandoc MD → LaTeX body
   - Package with cover page, TOC, headers/footers
   - tectonic compile PDF
```

### Required Sections
| Section | Content |
|---------|---------|
| Paper Information | Title, final deliverables list |
| Stage-by-Stage Process | Input/output/key decisions per stage, verbatim user quotes |
| Iteration Details | Review comment summaries, revision items, re-review results |
| Interaction Pattern Summary | User/Claude roles, intervention count, key turning points |
| User Key Decisions | Chronological list of important decisions |
| Key Lessons | Reusable lessons learned |
| **Collaboration Quality Evaluation** | Final chapter: 1-100 score + dimensional analysis + recommendations |

### Collaboration Quality Evaluation (Mandatory Final Chapter)

**Scoring Dimensions** (1-100 each, weighted average):
| Dimension | Focus |
|-----------|-------|
| Direction Setting | Clarity, timing, scope definition |
| Intellectual Contribution | Insight depth, original questions, concept challenges |
| Quality Gatekeeping | Visual inspection, formatting requirements, quality standards |
| Iteration Discipline | Direction correction, willingness to re-run, refusing to settle |
| Delegation Efficiency | When to intervene/let go, instruction precision, checkpoint efficiency |
| Meta-Learning | Feeding experience back to skills, requesting lesson recording |

**Score Ranges**:
| Score | Meaning |
|-------|---------|
| 90-100 | Exceptional — User intervention significantly elevated intellectual quality |
| 75-89 | Excellent — Correct directional decisions, effective iteration leverage |
| 60-74 | Good — Necessary decisions completed, some opportunities missed |
| 40-59 | Basic — Primarily "continue" button with little substantive intervention |
| 1-39 | Needs Improvement — Intervention may have disrupted workflow |

### Output Files
| File | Description |
|------|-------------|
| `paper_creation_process.md` / `paper_creation_process_en.md` | Markdown version |
| `paper_creation_process_zh.pdf` / `paper_creation_process_en.pdf` | Compiled PDF |

### Pipeline End
After Stage 6 completion, pipeline is finished. State tracker produces final audit trail.

---

## Checkpoint Types Summary

| Type | When | Content |
|------|------|---------|
| FULL | First checkpoint; after integrity boundaries; before finalization | Full deliverables + decision dashboard + all options |
| SLIM | After 2+ consecutive "continue" on non-critical stages | One-line status + auto-continue in 5 seconds |
| MANDATORY | Integrity FAIL; Review decision; Stage 5 | Cannot be skipped; requires explicit user input |

---

## State Transition Matrix

```
Stage 1 RESEARCH → [confirm] → Stage 2 WRITE
Stage 2 WRITE → [confirm] → Stage 2.5 INTEGRITY
Stage 2.5 INTEGRITY → [PASS] → Stage 3 REVIEW
                        [FAIL] → fix → re-verify (max 3 rounds)
Stage 3 REVIEW → [Accept] → Stage 4.5 FINAL INTEGRITY
                 [Minor/Major] → Stage 4 REVISE
                 [Reject] → Stage 2 or end
Stage 4 REVISE → [confirm] → Stage 3' RE-REVIEW
Stage 3' RE-REVIEW → [Accept/Minor] → Stage 4.5 FINAL INTEGRITY
                     [Major] → Stage 4' RE-REVISE
Stage 4' RE-REVISE → [confirm] → Stage 4.5 FINAL INTEGRITY (no return to review)
Stage 4.5 FINAL INTEGRITY → [PASS with zero issues] → Stage 5 FINALIZE
                            [FAIL] → fix → re-verify
Stage 5 FINALIZE → [MD + DOCX] → [ask LaTeX] → [confirm] → [PDF] → Stage 6
Stage 6 PROCESS SUMMARY → [MD] → [LaTeX] → [PDF] → end
```

---

## Error Recovery by Stage

| Stage | Error | Handling |
|-------|-------|----------|
| Intake | Cannot determine entry point | Ask user about materials and goals |
| 1 | deep-research not converging | Suggest mode switch or narrow scope |
| 2 | Missing research foundation | Suggest returning to Stage 1 |
| 2.5 | Still FAIL after 3 rounds | List unverifiable items; user decides |
| 3 | Reject decision | Options: Stage 2 restructure or end |
| 4 | Revision incomplete | List unaddressed items; ask to continue |
| 3' | Major issues remain | Enter Stage 4' for final revision |
| 4' | Issues remain after revision | Mark as Acknowledged Limitations → Stage 4.5 |
| 4.5 | Final verification FAIL | Fix and re-verify (max 3 rounds) |
| Any | User leaves midway | Save state; resume from breakpoint later |
| Any | Skill execution failure | Report error; suggest retry or skip |
