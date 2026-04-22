#!/usr/bin/env python3
"""
report_cache.py — Skill Audit 报告缓存管理器

三层缓存机制：
1. Skill 内容指纹（SHA256）— 检测 skill 是否发生变化
2. 报告缓存 — 完整的扫描结果 JSON
3. 索引 — 记录所有历史报告的 skill 哈希快照

命中逻辑：计算所有 skill 的当前哈希 → 与索引中最新报告对比 →
        全部一致则返回缓存报告，否则重新扫描并更新缓存
"""

import json
import hashlib
import time
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

CACHE_DIR = Path("~/.hermes/.skill-audit-cache").expanduser()
INDEX_FILE = CACHE_DIR / "cache_index.json"


def _compute_skill_hash(skill_path: Path) -> str:
    """计算单个 skill 的内容指纹（SKILL.md + scripts/ 目录）"""
    m = hashlib.sha256()
    
    # SKILL.md
    sk_md = skill_path / "SKILL.md"
    if sk_md.exists():
        m.update(sk_md.read_bytes())
    
    # scripts/ 目录下的所有文件（递归，按路径排序保证顺序一致）
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        for f in sorted(scripts_dir.rglob("*")):
            if f.is_file():
                m.update(f.read_bytes())
    
    return m.hexdigest()[:16]


def compute_all_hashes(skills_root: Path, skill_keys: list[str]) -> dict[str, str]:
    """计算所有 skill 的当前哈希"""
    hashes = {}
    for key in skill_keys:
        skill_path = skills_root / key
        if skill_path.exists():
            hashes[key] = _compute_skill_hash(skill_path)
        else:
            hashes[key] = "missing"
    return hashes


def load_index() -> dict:
    """加载缓存索引"""
    if not INDEX_FILE.exists():
        return {"reports": [], "skills_root": "", "version": 1}
    try:
        return json.loads(INDEX_FILE.read_text())
    except Exception:
        return {"reports": [], "skills_root": "", "version": 1}


def save_index(index: dict):
    """保存缓存索引"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False, indent=2))


def load_report(report_path: Path) -> Optional[dict]:
    """加载指定报告"""
    if not report_path.exists():
        return None
    try:
        return json.loads(report_path.read_text())
    except Exception:
        return None


def check_cache(skills_root: Path, skill_keys: list[str]) -> tuple[bool, Optional[dict], str]:
    """
    检查缓存是否命中
    
    Returns: (cache_hit, report_data, cache_key)
    - cache_hit: True 表示缓存命中
    - report_data: 命中的报告数据（None 表示未命中）
    - cache_key: 命中的缓存键（如 "20260420_191523"）
    """
    index = load_index()
    
    # 检查是否同一种 skills root
    if index.get("skills_root") != str(skills_root):
        return False, None, ""
    
    reports = index.get("reports", [])
    if not reports:
        return False, None, ""
    
    # 计算当前哈希
    current_hashes = compute_all_hashes(skills_root, skill_keys)
    
    # 从最新到最旧遍历，找第一个哈希完全匹配的
    for report_meta in reversed(reports):
        cached_hashes = report_meta.get("skill_hashes", {})
        
        # 检查是否所有 skill 都匹配
        all_match = True
        for key in skill_keys:
            if current_hashes.get(key) != cached_hashes.get(key):
                all_match = False
                break
        
        if all_match:
            # 命中！加载完整报告
            report_path = CACHE_DIR / f"report_{report_meta['timestamp']}.json"
            report_data = load_report(report_path)
            if report_data:
                return True, report_data, report_meta["timestamp"]
    
    return False, None, ""


def save_report(
    skills_root: Path,
    skill_keys: list[str],
    report_data: dict,
    force: bool = False
) -> str:
    """
    保存报告并更新索引
    
    Returns: 报告时间戳键
    """
    index = load_index()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 计算当前所有 skill 的哈希
    hashes = compute_all_hashes(skills_root, skill_keys)
    
    # 保存完整报告
    report_path = CACHE_DIR / f"report_{timestamp}.json"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report_data, ensure_ascii=False, indent=2))
    
    # 更新索引（只保留最近 10 份报告）
    report_meta = {
        "timestamp": timestamp,
        "skill_hashes": hashes,
        "saved_at": datetime.now().isoformat(),
        "total_skills": len(skill_keys),
    }
    
    reports = index.get("reports", [])
    reports.append(report_meta)
    
    # 只保留最近 10 份
    if len(reports) > 10:
        # 删除最旧的报告文件
        for old_meta in reports[:-10]:
            old_path = CACHE_DIR / f"report_{old_meta['timestamp']}.json"
            if old_path.exists():
                old_path.unlink()
        reports = reports[-10:]
    
    index["reports"] = reports
    index["skills_root"] = str(skills_root)
    save_index(index)
    
    return timestamp


def get_latest_report() -> tuple[Optional[dict], str]:
    """获取最新一份报告"""
    index = load_index()
    reports = index.get("reports", [])
    if not reports:
        return None, ""
    
    latest = reports[-1]
    report_path = CACHE_DIR / f"report_{latest['timestamp']}.json"
    data = load_report(report_path)
    return data, latest["timestamp"]


def list_cached_reports() -> list[dict]:
    """列出所有缓存的报告"""
    index = load_index()
    return [
        {
            "timestamp": r["timestamp"],
            "saved_at": r["saved_at"],
            "total_skills": r["total_skills"],
        }
        for r in index.get("reports", [])
    ]


def dict_to_audit_results(data: dict, skills_root: str) -> dict[str, "AuditResult"]:
    """
    将缓存的 dict 转回 dict[str, AuditResult]
    用于缓存命中时重建对象供兼容性
    """
    # 延迟导入避免循环依赖
    sys.path.insert(0, str(Path(__file__).parent))
    from audit_runner import AuditResult

    results = {}
    skills_root_path = Path(skills_root)

    for key, item in data.get("skills", {}).items():
        # 重建 scan_result（只保留 summary 信息）
        class _ScanResultStub:
            pass
        sr = _ScanResultStub()
        sr.score = item.get("raw_score", 0)
        sr.categories = item.get("categories", {})
        sr.rules_triggered = [
            (_RuleStub(d["description"], d["severity"], d["category"]), [])
            for d in item.get("rules_triggered", [])
        ]

        class _SourceStub:
            pass
        src = _SourceStub()
        src.source = item.get("source", "unknown")
        src.author = item.get("author", "unknown")
        src.trust_score = item.get("trust_score", 1)
        src.license = item.get("license", "unknown")

        ar = AuditResult.__new__(AuditResult)
        ar.skill_name = item.get("skill_name", key.split("/")[-1])
        ar.skill_path = item.get("skill_path", str(skills_root_path / key))
        ar.source_info = src
        ar.scan_result = sr
        ar.final_score = item.get("final_score", 0)
        ar._score_breakdown = item.get("score_breakdown", {})
        ar.risk_level = item.get("risk_level", "⚪ CLEAN")
        ar.verdict = item.get("verdict", "")
        ar.notes = item.get("notes", "")
        ar.recommendations = item.get("recommendations", [])
        results[key] = ar

    return results


class _RuleStub:
    """缓存中规则信息的简易替代"""
    def __init__(self, description, severity, category):
        self.description = description
        self.severity = severity
        self.category = category

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        # 默认：列出缓存报告
        reports = list_cached_reports()
        if not reports:
            print("无缓存报告")
        else:
            print(f"共 {len(reports)} 份缓存报告：\n")
            for r in reports:
                stats = r.get("stats", {})
                print(f"  [{r['timestamp']}] {r['saved_at']}")
                print(f"    Skills: {r['total_skills']}")
                print()
    elif sys.argv[1] == "check":
        # 检查缓存状态
        skills_root = Path("~/.hermes/skills").expanduser()
        from audit_runner import AuditRunner
        
        runner = AuditRunner(skills_root=str(skills_root))
        # 获取 skill 列表（不扫描，只列目录）
        skill_keys = sorted([
            str(p.relative_to(skills_root))
            for p in skills_root.glob("*/*")
            if p.is_dir() and (p / "SKILL.md").exists()
        ])
        
        hit, data, key = check_cache(skills_root, skill_keys)
        if hit:
            print(f"✅ 缓存命中！报告: {key}")
            print(f"   Skills: {len(data.get('skills', {}))}")
            print(f"   时间: {data.get('metadata', {}).get('scan_time', 'unknown')}")
        else:
            print("❌ 缓存未命中，需要重新扫描")
    elif sys.argv[1] == "clear":
        # 清除所有缓存
        import shutil
        if CACHE_DIR.exists():
            shutil.rmtree(CACHE_DIR)
            print("✅ 缓存已清除")
        else:
            print("缓存目录不存在")
    else:
        print(f"用法: {sys.argv[0]} [check|clear]")
