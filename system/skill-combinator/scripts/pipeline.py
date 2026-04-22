#!/usr/bin/env python3
"""
SkillCombinator 核心 pipeline
discover → select → sequence → compose → validate
"""

import json
import re
import jieba
from pathlib import Path

jieba.setLogLevel(20)  # suppress jieba internals

REGISTRY_PATH = Path.home() / ".hermes/.skill_registry.json"
PHASE_ORDER = ["analysis", "planning", "generation", "execution", "validation", "integration"]


def load_registry():
    with open(REGISTRY_PATH) as f:
        return json.load(f)["skills"]


def tokenize(text):
    """中英文混合分词：英文按\w+，中文用 jieba"""
    words = set(w.lower() for w in re.findall(r'[a-zA-Z0-9_]+', text.lower()))
    chinese_words = set(w.lower() for w in jieba.cut(text) if w.strip() and not w.isascii())
    # 英文词 + 中文词集合
    return words | chinese_words


def discover(task: str, skills: dict) -> list[tuple]:
    """
    根据任务文本匹配最相关的 skills。
    jieba 中文分词 + 英文 \w+ 混合。
    返回 [(skill_name, score), ...] 按得分降序
    """
    task_words = tokenize(task)

    # 任务类型信号
    is_analysis = any(w in task_words for w in ['分析', '诊断', '检查', 'audit', 'analyze'])
    is_optimize = any(w in task_words for w in ['优化', 'improve', 'optimize'])
    is_coding = any(w in task_words for w in ['写', '代码', 'python', '脚本', 'code', '数据', '分析'])
    is_multi = any(w in task_words for w in ['组合', '协作', '多', '多个'])

    scores = {}
    for name, s in skills.items():
        score = 0
        triggers = [t.lower() for t in s.get("triggers", [])]
        phases = s.get("phases", [])

        for t in triggers:
            # trigger 也用 jieba 分词（中文部分）
            t_words = set(w.lower() for w in jieba.cut(t) if w.strip() and not w.isascii())
            t_words.update(re.findall(r'[a-zA-Z0-9_]+', t.lower()))

            overlap = task_words & t_words
            if overlap:
                score += len(overlap) * 2

        # Phase signal bonus：只在 trigger 匹配较少时补充，不压制 trigger 匹配
        # 计算 trigger 总得分，决定 bonus 强度
        trigger_total = sum(
            len((set(w.lower() for w in jieba.cut(t) if w.strip() and not w.isascii()) |
                 set(re.findall(r'[a-zA-Z0-9_]+', t.lower()))) & task_words) * 2
            for t in triggers
        )
        if trigger_total == 0:
            # 无 trigger 匹配时，用 phase bonus 作为 fallback 信号
            if is_optimize and 'execution' in phases and any('optim' in t.lower() or 'prompt' in t.lower() for t in triggers):
                score += 5
            elif is_optimize and phases == ['execution']:
                score += 1
            elif is_coding and phases == ['execution']:
                score += 2
            elif (is_analysis or is_optimize) and 'analysis' in phases:
                score += 1

        if score > 0:
            scores[name] = score

    return sorted(scores.items(), key=lambda x: -x[1])


def select(matched: list[tuple], top_k: int = 6) -> list[str]:
    """
    按 category 去重，保留每类最高分，最多 top_k 个。
    category = skill 名按 '-' 分割的前两段（如 skill-audit）
    skill 类最多保留 2 个（允许同族高分组）
    """
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
        # skill 类允许同类 2 个，其他只取 1 个
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
    """
    Phase 拓扑排序：analysis(0) → integration(5)。
    同 phase 按原始 matched 得分排列。
    """
    def key(name):
        ph = skills[name].get("phases", ["execution"])[0]
        return (PHASE_ORDER.index(ph) if ph in PHASE_ORDER else 3,)
    return sorted(names, key=key)


def compose(chain: list[str], skills: dict, task: str) -> dict:
    """
    生成组合方案。
    """
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
    """
    检查 phase 链是否有逆向。
    正常顺序：phase index 应递增（analysis → integration）
    """
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
    """
    完整 pipeline。
    返回 {"matched", "selected", "sequenced", "composed", "validated"}
    """
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
