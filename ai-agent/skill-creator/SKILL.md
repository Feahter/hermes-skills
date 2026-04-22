---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
---

# Skill Creator

A skill for creating new skills and iteratively improving them.

At a high level, the process of creating a skill goes like this:

- Decide what you want the skill to do and roughly how it should do it
- Write a draft of the skill
- Create a few test prompts and run claude-with-access-to-the-skill on them
- Help the user evaluate the results both qualitatively and quantitatively
  - While the runs happen in the background, draft some quantitative evals if there aren't any (if there are some, you can either use as is or modify if you feel something needs to change about them). Then explain them to the user (or if they already existed, explain the ones that already exist)
  - Use the `eval-viewer/generate_review.py` script to show the user the results for them to look at, and also let them look at the quantitative metrics
- Rewrite the skill based on feedback from the user's evaluation of the results (and also if there are any glaring flaws that become apparent from the quantitative benchmarks)
- Repeat until you're satisfied
- Expand the test set and try again at larger scale

Your job when using this skill is to figure out where the user is in this process and then jump in and help them progress through these stages. So for instance, maybe they're like "I want to make a skill for X". You can help narrow down what they mean, write a draft, write the test cases, figure out how they want to evaluate, run all the prompts, and repeat.

On the other hand, maybe they already have a draft of the skill. In this case you can go straight to the eval/iterate part of the loop.

Of course, you should always be flexible and if the user is like "I don't need to run a bunch of evaluations, just vibe with me", you can do that instead.

Then after the skill is done (but again, the order is flexible), you can also run the skill description improver, which we have a whole separate script for, to optimize the triggering of the skill.

Cool? Cool.

## 道层工具

遇到复杂 skill 创建/优化决策时，可用 `talent-mind` 进行三层递归分析（系统A/系统B双轨 + 元认知校准）。

## Quick-start example

Here's a complete minimal skill that shows all the pieces working together:

```markdown
---
name: my-first-skill
description: Does X. Use when the user mentions Y or wants to Z. Keywords: X, Y, Z.
---

# My First Skill

## What it does
Explain in 1-2 sentences what this skill enables.

## When to trigger
List the exact contexts where this skill should activate.


## Step-by-step guide

> 详细内容 → `references/test-evaluation.md`（测试评估完整流程）
> 详细内容 → `references/improvement.md`（持续改进）
> 详细内容 → `references/description-optimization.md`（Description 优化）
> 详细内容 → `references/platform-notes.md`（Claude.ai / Cowork 特定说明）

---

## Reference files

> 详细内容 → `references/schemas.md`（完整 schema，包含 assertions 字段）

