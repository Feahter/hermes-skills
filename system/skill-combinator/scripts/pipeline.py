#!/usr/bin/env python3
"""
SkillCombinator 核心 pipeline v5
discover → select → sequence → compose → validate

修复 v4 问题:
- 移除 fuzzy fallback（+6/+3 给了无关 skill 如 metacognition-auditor）
- 改用精准 keyword-in-name 加分：audit skill +6，prompt skill +5，skill 组合 +4
- 无 trigger 命中时，完全依赖 keyword name matching
- Task 2(coding) 补 domain bonus：skill 名含 data/python/code +3
"""

import json
import re
import jieba
from pathlib import Path

jieba.setLogLevel(20)

REGISTRY_PATH = Path.home() / ".hermes/.skill_registry.json"
PHASE_ORDER = ["analysis", "planning", "generation", "execution", "validation", "integration"]


def load_registry():
    with open(REGISTRY_PATH) as f:
        return json.load(f)["skills"]


def tokenize(text):
    """中英文混合分词"""
    words = set(w.lower() for w in re.findall(r'[a-zA-Z0-9_]+', text.lower()))
    chinese = set(w.lower() for w in jieba.cut(text) if w.strip() and not w.isascii())
    return words | chinese


def discover(task: str, skills: dict) -> list[tuple]:
    task_words = tokenize(task)

    # 任务信号
    is_analysis = any(w in task_words for w in ['分析', '诊断', '检查', 'audit', 'analyze'])
    is_optimize = any(w in task_words for w in ['优化', 'improve', 'optimize'])
    is_coding   = any(w in task_words for w in ['写', '代码', 'python', '脚本', 'code', '数据'])
    is_multi    = any(w in task_words for w in ['组合', '协作', '多', '多个'])
    is_skill    = any(w in task_words for w in ['skill', 'skills'])
    is_prompt   = any(w in task_words for w in ['prompt', 'prompts'])

    scores = {}
    for name, s in skills.items():
        score = 0
        triggers = s.get("triggers", [])
        phases = s.get("phases", [])

        # 1. Trigger 匹配
        for t in triggers:
            t_words = set(w.lower() for w in jieba.cut(t) if w.strip() and not w.isascii())
            t_words.update(re.findall(r'[a-zA-Z0-9_]+', t.lower()))
            overlap = task_words & t_words
            if overlap:
                score += len(overlap) * 2

        # 2. Keyword-in-name bonus（精准，只在 name 含关键词时触发）
        #    无需 trigger 命中，name 本身够精准就直接加分
        name_lower = name.lower()

        # audit 类 skill（Task 1）
        if is_skill and is_analysis and 'audit' in name_lower:
            score += 6

        # prompt 类 skill（Task 3）
        elif is_prompt and 'prompt' in name_lower:
            score += 5

        # skill 组合/编排（Task 4）
        elif is_skill and is_multi and 'combinator' in name_lower:
            score += 5

        # analysis 类（非 audit 名称）
        elif is_analysis and 'analysis' in name_lower and 'audit' not in name_lower:
            score += 3

        # orchestration/skill 系统类
        elif is_skill and any(kw in name_lower for kw in ['orchestrat', 'creator', 'evolution', 'from-github', 'from-masters']):
            score += 2

        # coding/data 类（Task 2 补分）
        elif is_coding and any(kw in name_lower for kw in ['code', 'coding', 'python', 'data', 'jupyter', 'script']):
            score += 3

        # optimize/improve 类（Task 1/3 补分）
        elif is_optimize and any(kw in name_lower for kw in ['optim', 'improve', 'efficient']):
            score += 2

        if score > 0:
            scores[name] = score

    return sorted(scores.items(), key=lambda x: -x[1])


def select(matched: list[tuple], top_k: int = 6) -> list[str]:
    groups = {}
    for name, score in matched:
        parts = name.split("-")
        if len(parts) >= 2 and parts[0] in ['skill', 'meta']:
            cat = "-".join(parts[:2])
        else:
            cat = parts[0]
        if cat not in groups:
            groups[cat] = []
        groups[cat].append((name, score))

    all_items = []
    for cat, items in groups.items():
        items.sort(key=lambda x: -x[1])
        limit = 2 if cat.startswith('skill') else 1
        all_items.extend(items[:limit])

    all_items.sort(key=lambda x: -x[1])
    seen = set()
    result = []
    for name, score in all_items:
        if name not in seen:
            result.append(name)
            seen.add(name)
            if len(result) >= top_k:
                break
    return result


def sequence(names: list[str], skills: dict) -> list[str]:
    def key(name):
        ph = skills[name].get("phases", ["execution"])[0]
        return (PHASE_ORDER.index(ph) if ph in PHASE_ORDER else 3,)
    return sorted(names, key=key)


def compose(chain: list[str], skills: dict, task: str) -> dict:
    phases = [skills[n].get("phases", ["execution"])[0] for n in chain]
    if len(chain) == 1:
        reasoning = f"单 skill '{chain[0]}' 足以完成"
    else:
        reasoning = " → ".join(f"{n}({p})" for n, p in zip(chain, phases))
    return {
        "chain": chain,
        "phases": phases,
        "reasoning": reasoning,
        "conflicts_resolved": [],
    }


def validate(chain: list[str], skills: dict, task: str) -> dict:
    phases = [skills[n].get("phases", ["execution"])[0] for n in chain]
    issues = []
    for i in range(len(phases) - 1):
        a, b = phases[i], phases[i+1]
        try:
            if PHASE_ORDER.index(a) > PHASE_ORDER.index(b):
                issues.append(f"{a} → {b} 是逆向顺序")
        except ValueError:
            pass
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "recommendation": "ok" if not issues else "建议调整顺序",
    }


def run(task: str, top_k: int = 6) -> dict:
    skills = load_registry()
    matched = discover(task, skills)
    selected = select(matched, top_k=top_k)
    sequenced = sequence(selected, skills)
    composed = compose(sequenced, skills, task)
    validated = validate(sequenced, skills, task)
    return {
        "task": task,
        "matched": matched[:10],
        "selected": selected,
        "sequenced": sequenced,
        "composed": composed,
        "validated": validated,
    }


if __name__ == "__main__":
    import sys
    task = sys.argv[1] if len(sys.argv) > 1 else "帮我分析skill系统，给出优化建议"
    result = run(task)
    print(json.dumps(result, indent=2, ensure_ascii=False))
