#!/usr/bin/env python3
"""
SkillCombinator 核心 pipeline v7
改进：反馈注入 + 复杂度门槛 + Trigger registry化

v7 新增：
- 反馈回路：用户纠正后自动记录，下次 discover 加权
- 复杂度门槛：短任务+单skill关键词 → 直连不过pipeline
- Trigger registry化：策略规则可配置化
"""

import json
import re
import jieba
import os
from pathlib import Path
from datetime import datetime

jieba.setLogLevel(20)

REGISTRY_PATH = Path.home() / ".hermes/.skill_registry.json"
FEEDBACK_PATH = Path.home() / ".hermes/.skill_combinator_feedback.json"
PHASE_ORDER = ["analysis", "planning", "generation", "execution", "validation", "integration"]

# ─── 复杂度门槛配置 ────────────────────────────────────────────
COMPLEXITY_THRESHOLD = 35  # 字符数以下 + 含单skill关键词 → 直连
SINGLE_SKILL_TRIGGERS = {
    "git": "git",
    "github": "github",
    "写代码": "coding-agent",
    "写小说": "novel-writing-sop",
    "写文章": "khazix-writer",
    "写诗": "songwriting-and-ai-music",
    "ppt": "html-ppt",
    "幻灯片": "html-ppt",
    "pr": "github",
    "issue": "github",
    "code review": "code-review-expert",
    "代码审查": "code-review-expert",
    "计划": "plan",
    "记账": "notion",
}


# ─── Trigger Registry（可配置化策略）──────────────────────────
# 不再 hardcode if-elif，改为 registry 扩展字段
TRIGGER_STRATEGIES = [
    # (task信号检测, skill name pattern, bonus分数, reason)
    # 优先级从高到低，命中即加
    {"signals": ["analysis", "audit", "检查", "诊断"], "name_kw": ["audit"], "bonus": 6, "phase": "analysis"},
    {"signals": ["prompt", "提示词"], "name_kw": ["prompt"], "bonus": 5, "phase": "generation"},
    {"signals": ["skill", "skills"], "name_kw": ["combinator"], "bonus": 5, "phase": "integration"},
    {"signals": ["分析"], "name_kw": ["analysis"], "bonus": 3, "phase": "analysis"},
    {"signals": ["orchestrat", "creator", "evolution", "from-github", "from-masters"], "name_kw": ["orchestrat", "creator", "evolution", "from-github", "from-masters"], "bonus": 2, "phase": "integration"},
    {"signals": ["写", "代码", "python", "脚本", "code", "数据"], "name_kw": ["code", "coding", "python", "jupyter", "script"], "bonus": 3, "phase": "execution"},
    {"signals": ["优化", "improve", "optimize"], "name_kw": ["optim", "improve"], "bonus": 2, "phase": "execution"},
    {"signals": ["研究", "research", "搜索"], "name_kw": ["deep-research", "explorer", "arxiv", "tavily"], "bonus": 2, "phase": "analysis"},
]


def load_registry():
    with open(REGISTRY_PATH) as f:
        return json.load(f)["skills"]


def load_feedback():
    """加载反馈文件，无则返回空结构"""
    if not FEEDBACK_PATH.exists():
        return {}
    try:
        with open(FEEDBACK_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_feedback(feedback: dict):
    """保存反馈文件"""
    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(FEEDBACK_PATH, "w") as f:
        json.dump(feedback, f, ensure_ascii=False, indent=2)


def record_feedback(task: str, chosen: list[str], rejected: list[str] = None):
    """
    记录用户对组合的反馈，用于下次 discover 加权。
    用法：record_feedback("分析代码", ["code-review-expert"], ["skill-audit"])
    """
    feedback = load_feedback()
    # 用任务关键词做 key（模糊匹配）
    task_key = task[:20].lower()
    if task_key not in feedback:
        feedback[task_key] = {"history": [], "skill_scores": {}}

    feedback[task_key]["history"].append({
        "ts": datetime.now().isoformat(),
        "chosen": chosen,
        "rejected": rejected or [],
    })

    for s in chosen:
        feedback[task_key]["skill_scores"][s] = feedback[task_key]["skill_scores"].get(s, 0) + 1
    for s in rejected or []:
        feedback[task_key]["skill_scores"][s] = feedback[task_key]["skill_scores"].get(s, 0) - 1

    save_feedback(feedback)
    return feedback


def apply_feedback(task: str, scores: dict) -> dict:
    """
    将反馈加权应用到 scores 上。
    找到最匹配的历史 task key，叠加 skill_scores。
    """
    feedback = load_feedback()
    task_lower = task.lower()

    best_key = None
    best_overlap = 0
    for key in feedback:
        # 简单前缀匹配
        if task_lower.startswith(key) or key.startswith(task_lower[:10]):
            overlap = len(key)
            if overlap > best_overlap:
                best_overlap = overlap
                best_key = key

    if best_key and feedback[best_key].get("skill_scores"):
        skill_scores = feedback[best_key]["skill_scores"]
        for name in scores:
            if name in skill_scores:
                scores[name] += skill_scores[name] * 0.5  # 反馈权重 0.5

    return scores


def tokenize(text):
    """中英文混合分词"""
    words = set(w.lower() for w in re.findall(r'[a-zA-Z0-9_]+', text.lower()))
    chinese = set(w.lower() for w in jieba.cut(text) if w.strip() and not w.isascii())
    return words | chinese


def complexity_gate(task: str) -> dict:
    """
    复杂度门槛：短任务 + 单skill关键词 → 直连
    返回 {"bypass": bool, "skill": str or None, "reason": str}
    """
    if len(task) >= COMPLEXITY_THRESHOLD:
        return {"bypass": False, "skill": None, "reason": f"task length {len(task)} >= {COMPLEXITY_THRESHOLD}"}

    task_lower = task.lower()
    for kw, skill in SINGLE_SKILL_TRIGGERS.items():
        # 英文词用 r'\b' 匹配词边界，避免 "github" 匹配 "git"
        if re.search(r'\b' + re.escape(kw) + r'\b', task_lower):
            return {"bypass": True, "skill": skill, "reason": f"'{kw}' matched → direct {skill}"}

    return {"bypass": False, "skill": None, "reason": "no single-skill trigger"}


# ─── Plan A: 真实数据加权（lazy load）────────────────────────────
# 避免每次 discover 都读文件，cache 5 分钟
_real_stats_cache: dict | None = None
_real_stats_ts: float = 0
_REAL_STATS_TTL = 300  # 5分钟


def _get_real_stats() -> dict:
    global _real_stats_cache, _real_stats_ts
    import time
    now = time.time()
    if _real_stats_cache is None or (now - _real_stats_ts) > _REAL_STATS_TTL:
        from pathlib import Path
        import sys
        exp_dir = Path(__file__).parent.parent.parent.parent / ".experiment_log"
        sys.path.insert(0, str(exp_dir))
        try:
            from skill_logger import SkillLogger
            logger = SkillLogger()
            _real_stats_cache = logger.get_real_invocation_stats(min_samples=1)
            _real_stats_ts = now
        except Exception:
            _real_stats_cache = {}
    return _real_stats_cache


def _get_cooccurrence() -> dict:
    from pathlib import Path
    import sys
    exp_dir = Path(__file__).parent.parent.parent / ".experiment_log"
    sys.path.insert(0, str(exp_dir))
    try:
        from skill_logger import SkillLogger
        logger = SkillLogger()
        return logger.get_skill_cooccurrence()
    except Exception:
        return {}


def _apply_real_data_boost(scores: dict, task: str) -> dict:
    """
    Plan A: 用真实调用成功率对候选 skill 做 boost。
    boost = (success_rate - 0.5) * 4
    成功100% → +2,  成功率0% → -2,  成功率50% → 0
    """
    real_stats = _get_real_stats()
    cooccur = _get_cooccurrence()

    for name in scores:
        stat = real_stats.get(name)
        if stat:
            # 成功率 boost
            boost = (stat["success_rate"] - 0.5) * 4
            scores[name] += boost

        # 协作链 boost：如果 co-occurring skill 也在候选里，互相加分
        coskills = cooccur.get(name, [])
        for co in coskills:
            if co in scores:
                scores[name] += 0.5

    return scores


# ─── Stage 1：搜索索引（纯内存，无 I/O）───────────────────────
def stage1_search_index(task: str, skills: dict, top_k: int = 20) -> list[tuple]:
    """
    Stage 1: 搜索索引
    从 registry triggers/keywords 匹配 + 反馈加权，不读文件，纯内存计算。
    返回 top_k 候选，按相关性得分排序。
    """
    task_words = tokenize(task)

    # 任务信号检测
    is_analysis = any(w in task_words for w in ['分析', '诊断', '检查', 'audit', 'analyze'])
    is_optimize = any(w in task_words for w in ['优化', 'improve', 'optimize'])
    is_coding   = any(w in task_words for w in ['写', '代码', 'python', '脚本', 'code', '数据'])
    is_multi    = any(w in task_words for w in ['组合', '协作', '多', '多个'])
    is_skill    = any(w in task_words for w in ['skill', 'skills'])
    is_prompt   = any(w in task_words for w in ['prompt', '提示词'])
    is_research = any(w in task_words for w in ['研究', 'research', '搜索'])

    scores = {}
    for name, s in skills.items():
        score = 0
        triggers = s.get("triggers", [])
        phases = s.get("phases", [])
        name_lower = name.lower()

        # Trigger overlap scoring
        for t in triggers:
            t_words = set(w.lower() for w in jieba.cut(t) if w.strip() and not w.isascii())
            t_words.update(re.findall(r'[a-zA-Z0-9_]+', t.lower()))
            overlap = task_words & t_words
            if overlap:
                score += len(overlap) * 2

        # Trigger Registry 策略（替代硬编码 if-elif）
        for strategy in TRIGGER_STRATEGIES:
            signals_match = any(sig in task_words for sig in strategy["signals"])
            name_match = any(kw in name_lower for kw in strategy["name_kw"])
            if signals_match and name_match:
                score += strategy["bonus"]
                break  # 优先级策略，命中即用

        if score > 0:
            scores[name] = score

    # 反馈加权
    scores = apply_feedback(task, scores)

    # Plan A: 真实数据 boost
    scores = _apply_real_data_boost(scores, task)

    return sorted(scores.items(), key=lambda x: -x[1])[:top_k]


# ─── Stage 2：短列表 + 轻量描述（按 category 去重）─────────────
def stage2_shortlist(matched: list[tuple], skills: dict, top_k: int = 6) -> list[dict]:
    """
    Stage 2: 短列表 + 轻量描述
    每个候选返回 {name, phase, summary}，让模型选择加载哪个。
    不加载 SKILL.md，纯从 registry 读 summary。
    """
    # 按 category 去重，每类最多 2 个
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
            s = skills.get(name, {})
            result.append({
                "name": name,
                "phase": s.get("phases", ["execution"])[0],
                "summary": s.get("summary", "")[:150] or "(无描述)",
                "score": score,
            })
            seen.add(name)
            if len(result) >= top_k:
                break
    return result


# ─── Stage 3：按需加载完整 Schema（决定执行时才读文件）─────────
def stage3_load_schema(name: str, skills: dict) -> dict:
    """
    Stage 3: 按需加载完整 schema
    只有模型决定执行某个 skill 时才调用此函数。
    读取完整 SKILL.md 内容（而非 registry cache）。
    """
    skill_path = skills[name].get("path")
    if not skill_path:
        return {"name": name, "error": "path not found in registry"}

    path = Path(skill_path)
    if not path.exists():
        return {"name": name, "error": f"SKILL.md not found: {path}"}

    content = path.read_text(encoding='utf-8')
    return {
        "name": name,
        "path": str(path),
        "content": content,
        "phase": skills[name].get("phases", ["execution"])[0],
        "triggers": skills[name].get("triggers", []),
    }


# ─── 旧接口（向后兼容）──────────────────────────────────────────
def select(matched: list[tuple], top_k: int = 6) -> list[str]:
    """Legacy select() for backward compatibility."""
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


# ─── 主入口：on_demand_discover（含复杂度门槛）─────────────────
def on_demand_discover(task: str, top_k: int = 6) -> dict:
    """
    三阶段按需发现（类 Glean 技能发现机制）：

    Stage 1: 搜索索引（registry triggers/keywords + 反馈加权）
    Stage 2: 短列表 + 轻量描述
    Stage 3: 按需加载完整 SKILL.md

    新增 v7：
    - 复杂度门槛：短任务 + 单skill关键词 → 直连不过 pipeline
    - 反馈回路：apply_feedback() 在 Stage 1 末尾应用

    用法：
      result = on_demand_discover("帮我分析代码审查问题")
      print(result["stage2_shortlist"])
      schema = stage3_load_schema("code-review-expert", skills)
    """
    skills = load_registry()

    # 复杂度门槛
    gate = complexity_gate(task)
    if gate["bypass"]:
        return {
            "task": task,
            "gate": gate,
            "bypass": True,
            "stage1_candidates": [],
            "stage2_shortlist": [],
            "chain": [gate["skill"]],
            "phases": [skills.get(gate["skill"], {}).get("phases", ["execution"])[0]],
            "reasoning": gate["reason"],
        }

    # Stage 1
    matched = stage1_search_index(task, skills)

    # Stage 2
    shortlist = stage2_shortlist(matched, skills, top_k=top_k)

    return {
        "task": task,
        "gate": gate,
        "bypass": False,
        "stage1_candidates": [{"name": n, "score": s} for n, s in matched],
        "stage2_shortlist": shortlist,
        "stage3_note": "用 stage3_load_schema(name, skills) 按需加载完整 SKILL.md",
    }


def run(task: str, top_k: int = 6) -> dict:
    """Legacy run() — 保持向后兼容。"""
    skills = load_registry()

    # 复杂度门槛
    gate = complexity_gate(task)
    if gate["bypass"]:
        return {
            "task": task,
            "gate": gate,
            "bypass": True,
            "matched": [],
            "selected": [gate["skill"]],
            "sequenced": [gate["skill"]],
            "composed": {"chain": [gate["skill"]], "phases": ["execution"], "reasoning": gate["reason"], "conflicts_resolved": []},
            "validated": {"valid": True, "issues": [], "recommendation": "ok"},
        }

    matched = stage1_search_index(task, skills)
    selected = select(matched, top_k=top_k)
    sequenced = sequence(selected, skills)
    composed = compose(sequenced, skills, task)
    validated = validate(sequenced, skills, task)
    return {
        "task": task,
        "gate": gate,
        "bypass": False,
        "matched": matched[:10],
        "selected": selected,
        "sequenced": sequenced,
        "composed": composed,
        "validated": validated,
    }


if __name__ == "__main__":
    import sys
    task = sys.argv[1] if len(sys.argv) > 1 else "帮我分析skill系统，给出优化建议"

    if "--on-demand" in sys.argv or "-o" in sys.argv:
        result = on_demand_discover(task)
    else:
        result = run(task)
    print(json.dumps(result, indent=2, ensure_ascii=False))
