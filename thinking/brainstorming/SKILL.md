---
name: brainstorming
description: 头脑风暴技能 - 创意发散与思路拓展。触发：需要创意想法、解决方案发散、思路拓展、多方案对比。For English-language project idea generation via constraints, see 'creative-ideation' instead.
metadata:
  combinator:
    triggers:
      - brainstorming
      - 头脑风暴
      - 创意发散
      - 想办法
      - 多方案
      - 思路拓展
      - 创意写作
      - ideation
      - 创意
      - brainstorm
---

# Brainstorming

---
# Brainstorming Ideas Into Designs

## Overview

Help turn ideas into fully formed designs and specs through natural collaborative dialogue.

Start by understanding the current project context, then ask questions one at a time to refine the idea. Once you understand what you're building, present the design in small sections (200-300 words), checking after each section whether it looks right so far.

## The Process

**Understanding the idea:**
- Check out the current project state first (files, docs, recent commits)
- Ask questions one at a time to refine the idea
- Prefer multiple choice questions when possible, but open-ended is fine too
- Only one question per message - if a topic needs more exploration, break it into multiple questions
- Focus on understanding: purpose, constraints, success criteria

**Exploring approaches:**
- Propose 2-3 different approaches with trade-offs
- Present options conversationally with your recommendation and reasoning
- Lead with your recommended option and explain why

**Presenting the design:**
- Once you believe you understand what you're building, present the design
- Break it into sections of 200-300 words
- Ask after each section whether it looks right so far
- Cover: architecture, components, data flow, error handling, testing
- Be ready to go back and clarify if something doesn't make sense

## After the Design

**Documentation:**
- Write the validated design to `docs/plans/YYYY-MM-DD-<topic>-design.md`
- Use elements-of-style:writing-clearly-and-concisely skill if available
- Commit the design document to git

**Implementation (if continuing):**
- Ask: "Ready to set up for implementation?"
- Use superpowers:using-git-worktrees to create isolated workspace
- Use superpowers:writing-plans to create detailed implementation plan

## Key Principles

- **One question at a time** - Don't overwhelm with multiple questions
- **Multiple choice preferred** - Easier to answer than open-ended when possible
- **YAGNI ruthlessly** - Remove unnecessary features from all designs
- **Explore alternatives** - Always propose 2-3 approaches before settling
- **Incremental validation** - Present design in sections, validate each
- **Be flexible** - Go back and clarify when something doesn't make sense


## §Absorbed Sub-skills

These narrow thinking skills are absorbed into this umbrella (archived → content preserved in references/):

| Sub-skill | Absorbed as | Reason |
|-----------|------------|--------|
| `thinking/six-thinking-hats` | `references/six-thinking-hats.md` | De Bono's parallel thinking — a brainstorming variant |
| `thinking/blade-of-logic` | `references/blade-of-logic.md` | Logical analysis — a brainstorming refinement |
| `thinking/ladder-of-abstraction` | `references/ladder-of-abstraction.md` | Abstraction shifting — a brainstorming tool |
| `thinking/mirror-of-perspectives` | `references/mirror-of-perspectives.md` | Perspective-taking — a brainstorming catalyst |

## Quick-Reference: Sub-Skill Workflows

### Six Thinking Hats (from six-thinking-hats)
> De Bono's parallel thinking — six dimensions: facts, emotion, risk, value, creativity, process control.
- Best for: major decisions, team discussions, comprehensive analysis

### Blade of Logic (from blade-of-logic)
> Propositional reasoning — extract propositions, apply symbolic operators, build logical chains.
- Best for: analyzing argumentation, spotting logical fallacies, academic writing

### Ladder of Abstraction (from ladder-of-abstraction)
> Move text between concrete (sensory detail) and abstract (philosophical concept).
- Best for: creative writing, speech refinement, concept clarification

### Mirror of Perspectives (from mirror-of-perspectives)
> Find the unique angle that makes the problem trivially simple.
- Best for: breakthrough thinking, product design, strategic decisions