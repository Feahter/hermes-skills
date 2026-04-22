---
name: academic-pipeline
description: "Orchestrator: research → write → integrity check → review → revise → re-review → re-revise → final integrity → finalize. Coordinates deep-research, academic-paper, academic-paper-reviewer with mandatory integrity verification and two-stage peer review. Triggers: academic pipeline, research to paper, full paper workflow, paper pipeline, end-to-end paper."
metadata:
  version: "2.7"
  last_updated: "2026-04-20"
  depends_on: "deep-research, academic-paper, academic-paper-reviewer"
---

# Academic Pipeline v2.7

Lightweight orchestrator for the complete academic workflow. Does not perform substantive work — only detects stages, recommends modes, dispatches skills, manages transitions, tracks state.

> **Detailed stage descriptions**: `references/stages.md`

## Quick Start

| Command | Entry Point |
|---------|-------------|
| `I want to write a research paper on...` | Stage 1 (RESEARCH) |
| `I already have a paper, help me review it` | Stage 2.5 (INTEGRITY) |
| `I received reviewer comments, help me revise` | Stage 4 (REVISE) |

**Flow**: Detect stage → Recommend mode → Dispatch skill → Wait for confirmation → Track state

## Trigger Conditions

**Keywords**: academic pipeline, research to paper, full paper workflow, paper pipeline, end-to-end paper, research-to-publication

**Non-triggers** (use specific skill directly):
| Scenario | Skill |
|----------|-------|
| Search/literature review only | `deep-research` |
| Write paper only | `academic-paper` |
| Review paper only | `academic-paper-reviewer` |
| Check citations only | `academic-paper` (citation-check) |
| Convert format only | `academic-paper` (format-convert) |

## Pipeline Stages

| Stage | Name | Skill | Modes | Deliverables |
|-------|------|-------|-------|--------------|
| 1 | RESEARCH | `deep-research` | socratic/full/quick | RQ Brief, Methodology, Bibliography, Synthesis |
| 2 | WRITE | `academic-paper` | plan/full | Paper Draft |
| **2.5** | **INTEGRITY** | **`integrity_verification_agent`** | **pre-review** | **Integrity report + corrected paper** |
| 3 | REVIEW | `academic-paper-reviewer` | full | 5 reviews + Editorial Decision + Revision Roadmap |
| 4 | REVISE | `academic-paper` | revision | Revised Draft + Response to Reviewers |
| **3'** | **RE-REVIEW** | **`academic-paper-reviewer`** | **re-review** | **Verification review + residual issues** |
| **4'** | **RE-REVISE** | **`academic-paper`** | **revision** | **Second revised draft** |
| **4.5** | **FINAL INTEGRITY** | **`integrity_verification_agent`** | **final-check** | **Final verification (100% pass)** |
| 5 | FINALIZE | `academic-paper` | format-convert | MD + DOCX + (LaTeX) + PDF |
| **6** | **PROCESS SUMMARY** | **orchestrator** | **auto** | **Process record MD + PDF** |

## State Machine

```
1 RESEARCH → [confirm] → 2 WRITE → [confirm] → 2.5 INTEGRITY
2.5 INTEGRITY → [PASS] → 3 REVIEW | [FAIL] → fix + re-verify (max 3)
3 REVIEW → [Accept] → 4.5 | [Minor/Major] → 4 | [Reject] → 2 or end
4 REVISE → [confirm] → 3' RE-REVIEW
3' RE-REVIEW → [Accept/Minor] → 4.5 | [Major] → 4' RE-REVISE
4' RE-REVISE → [confirm] → 4.5 (no return to review)
4.5 → [PASS zero issues] → 5 FINALIZE | [FAIL] → fix + re-verify
5 FINALIZE → MD+DOCX → [ask LaTeX] → PDF → 6 PROCESS SUMMARY → end
```

Full transitions: `references/pipeline_state_machine.md`

## Adaptive Checkpoint System

**Rule**: After each stage, prompt user and wait for confirmation.

| Type | When | Behavior |
|------|------|----------|
| FULL | First checkpoint; integrity boundaries; before finalization | Full deliverables + dashboard + options |
| SLIM | After 2+ consecutive "continue" on non-critical stages | One-line + auto-continue in 5s |
| MANDATORY | Integrity FAIL; Review decision; Stage 5 | Cannot skip; explicit input required |

**Adaptive rules**:
1. First checkpoint → always FULL
2. 2+ consecutive "continue" → prompt awareness
3. Integrity boundaries (2.5, 4.5) → always MANDATORY
4. Review decisions (3, 3') → always MANDATORY
5. Before finalization (5) → always MANDATORY
6. Other stages → start FULL, downgrade to SLIM if "just continue"
7. 4+ auto-continues → insert FULL checkpoint

**Dashboard (FULL checkpoints)**:
```
━━━ Stage [X] Complete ━━━
Word count: [N] | References: [N] | Coverage: [N]/[T]
Deliverables: [list]
Flagged: [issues or "None"]
Ready for Stage [Y]?
1. View progress ("status")  2. Adjust settings  3. Pause
```

## Agents

| Agent | Role | File |
|-------|------|------|
| `pipeline_orchestrator_agent` | Main orchestrator | `agents/pipeline_orchestrator_agent.md` |
| `state_tracker_agent` | State tracker | `agents/state_tracker_agent.md` |
| `integrity_verification_agent` | Integrity verifier | `agents/integrity_verification_agent.md` |

## Orchestrator Workflow

**Step 1: Intake & Detection**
```
Materials? → None=1, Research data=2, Draft=2.5, Verified=3, 
             Comments=4, Revised=3', Final draft=5
Goal? → Full or partial workflow
Confirm entry point with user
```

**Step 2: Mode Recommendation**
| User Type | Stage 1 | Stage 2 | Stage 3 |
|-----------|---------|---------|---------|
| Novice/wants guidance | socratic | plan | guided |
| Experienced | full | full | full |
| Time-limited | quick | full | quick |

**Step 3: Stage Execution**
```
1. Inform user which Stage begins
2. Load skill's SKILL.md
3. Launch skill with recommended mode
4. Monitor completion
5. Compile deliverables
6. Update state (state_tracker_agent)
7. [MANDATORY] Prompt checkpoint, wait for confirmation
```

**Step 4: Transition**
| From → To | Handoff |
|-----------|---------|
| 1 → 2 | RQ Brief + Bibliography + Synthesis → academic-paper |
| 2 → 2.5 | Paper draft → integrity_verification_agent |
| 2.5 → 3 | Verified paper → academic-paper-reviewer |
| 3 → 4 | Revision Roadmap → academic-paper (revision) |
| 4 → 3' | Revised draft + Response → academic-paper-reviewer |
| 3' → 4' | New Roadmap → academic-paper (revision) |
| 4/4' → 4.5 | Revision → integrity_verification_agent |
| 4.5 → 5 | Verified draft → academic-paper (format-convert) |

## Integrity Review Protocol

### Stage 2.5: Pre-Review Integrity
**Scope**:
| Phase | Scope | Requirement |
|-------|-------|-------------|
| A | References + bibliographic accuracy + ghost citations | 100% |
| B | Citation context spot-check | ≥30% |
| C | Statistical data | 100% |
| D | Originality + self-plagiarism | ≥30% |
| E | Claim verification (min 10 claims) | 30% |

**Pass**: Zero SERIOUS + zero MAJOR_DISTORTION + zero UNVERIFIABLE

### Stage 4.5: Final Integrity
Stricter than 2.5: B=100%, D≥50% (100% new content), E=100%. Must PASS zero issues.

## Two-Stage Review

### Stage 3: First Review
- **Team**: EIC + R1(methodology) + R2(domain) + R3(interdisciplinary) + Devil's Advocate
- **Output**: 5 reviews + Editorial Decision + Revision Roadmap + Socratic coaching
- **Decisions**: Accept→4.5 | Minor/Major→4 | Reject→2 or end

### Stage 3': Verification Review
- **Input**: Revised draft + Response + original Roadmap
- **Output**: Verification table + new issues + Editorial Decision
- **Decisions**: Accept/Minor→4.5 | Major→4'

**Coaching**: Max 8 rounds (3→4), 5 rounds (3'→4'). Say "just fix it" to skip.

## External Review Protocol

For real journal reviewer comments.

**Workflow**: Receive comments(text/PDF/DOCX) → Parse → Strategic coaching → Revise + Response → Self-verify

**Differences from internal**:
| Aspect | Internal | External |
|--------|----------|----------|
| Comments | AI simulated | Human reviewers |
| Format | Structured Roadmap | Unstructured text |
| Strategy | Accept wholesale OK | Must judge accept/reject |
| Acceptance | AI verification | Human ultimately decides |

## Mid-Entry Protocol

Users enter from any stage:
1. Detect available materials
2. Identify gaps vs. target stage
3. Suggest backfilling if prerequisites missing
4. Direct entry if materials sufficient

**Cannot skip Stage 2.5** (except with prior integrity report + unmodified content).

## Stage 6: Process Summary

**Trigger**: After Stage 5 completion

**Workflow**:
```
1. Ask language: Chinese / English / Both
2. Compile: initial instructions, decisions, iterations, insights, stats
3. Generate Markdown
4. LaTeX + tectonic → PDF
```

**Required sections**: Paper Info, Stage-by-Stage Process, Iteration Details, Interaction Pattern Summary, Key Decisions, Lessons, **Collaboration Quality Evaluation**

**Collaboration Quality Evaluation** (1-100 per dimension):
| Dimension | Focus |
|-----------|-------|
| Direction Setting | Clarity, timing, scope |
| Intellectual Contribution | Insight, original questions |
| Quality Gatekeeping | Visual inspection, standards |
| Iteration Discipline | Direction correction, re-runs |
| Delegation Efficiency | When to intervene/let go |
| Meta-Learning | Feeding experience to skills |

**Output**: `paper_creation_process.md` + `paper_creation_process.pdf`

## Progress Dashboard

Say "status" or "pipeline status":
```
+=============================================+
|   Academic Pipeline Status                  |
+=============================================+
| Topic: [topic]                              |
+---------------------------------------------+
| Stage 1   RESEARCH          [v] Completed   |
| Stage 2   WRITE             [v] Completed   |
| Stage 2.5 INTEGRITY         [v] PASS        |
| Stage 3   REVIEW (1st)      [v] Major       |
| Stage 4   REVISE            [v] Completed  |
| Stage 3'  RE-REVIEW (2nd)   [v] Accept     |
| Stage 4'  RE-REVISE         [-] Skipped     |
| Stage 4.5 FINAL INTEGRITY   [..] In Progress|
| Stage 5   FINALIZE          [ ] Pending     |
| Stage 6   PROCESS SUMMARY   [ ] Pending    |
+=============================================+
```

## Error Recovery

| Stage | Error | Handling |
|-------|-------|----------|
| Intake | Cannot determine entry | Ask about materials/goals |
| 1 | deep-research not converging | Mode switch or narrow scope |
| 2 | Missing research | Return to Stage 1 |
| 2.5 | FAIL after 3 rounds | List unverifiable; user decides |
| 3 | Reject | Options: Stage 2 or end |
| 4 | Revision incomplete | List unaddressed; ask continue |
| 3' | Major issues remain | Enter Stage 4' |
| 4' | Issues remain | Acknowledged Limitations → 4.5 |
| 4.5 | Final FAIL | Fix + re-verify (max 3) |
| Any | User leaves | Save state; resume later |
| Any | Skill failure | Report; retry or skip |

## Reference Files

**Agents**: `agents/pipeline_orchestrator_agent.md`, `agents/state_tracker_agent.md`, `agents/integrity_verification_agent.md`

**References**:
| File | Purpose |
|------|---------|
| `references/stages.md` | **Detailed stage descriptions** |
| `references/pipeline_state_machine.md` | Complete state transitions |
| `references/plagiarism_detection_protocol.md` | Phase D originality |
| `references/mode_advisor.md` | Cross-skill decision tree |
| `references/claim_verification_protocol.md` | Phase E claims |
| `references/team_collaboration_protocol.md` | Team coordination |
| `shared/handoff_schemas.md` | 9 cross-skill schemas |

**Templates**: `templates/pipeline_status_template.md`

**Examples**: `examples/full_pipeline_example.md`, `examples/mid_entry_example.md`

## Version Info

| Item | Content |
|------|---------|
| Version | 2.7 |
| Last Updated | 2026-04-20 |
| Maintainer | Cheng-I Wu |
| Depends On | deep-research v2.0+, academic-paper v2.0+, academic-paper-reviewer v1.1+ |

## Changelog

| Version | Changes |
|---------|---------|
| 2.7 | Split SKILL.md: detailed stages → `references/stages.md`; main file → ~250 lines |
| 2.6 | Enhanced handoff schemas, adaptive checkpoints, Phase E claim verification |
| 2.5 | External Review Protocol for real journal feedback |
| 2.4 | Stage 6 PROCESS SUMMARY with Collaboration Quality Evaluation |
| 2.3 | Stage 5 FINALIZE with LaTeX formatting |
| 2.2 | Checkpoint semantics, mode switching, state ownership |
| 2.1 | Plagiarism detection (Phase D), originality verification |
| 2.0 | Integrity checks (2.5, 4.5), two-stage review, mandatory checkpoints |
| 1.0 | Initial 5+1 stage pipeline |
