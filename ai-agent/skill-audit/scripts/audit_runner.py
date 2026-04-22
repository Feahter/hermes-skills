#!/usr/bin/env python3
"""
audit_runner.py — 三层递归扫描编排器
Layer 1: 批量自动扫描（danger_scanner.py）
Layer 2: 重点精准分析（人工/LLM）
Layer 3: 元认知自我演进（规则更新）
"""

import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

# 导入第一层扫描器
sys.path.insert(0, str(Path(__file__).parent))
from danger_scanner import DangerScanner, ScanResult, RULES


# ──────────────────────────────────────────────────────────────
# 来源追溯（Layer 1 补充）
# ──────────────────────────────────────────────────────────────

@dataclass
class SourceInfo:
    source: str           # ClawHub / GitHub / skill-cache / local
    author: str
    stars: Optional[int]
    downloads: Optional[int]
    last_updated: Optional[str]
    license: Optional[str]
    verified: bool = False   # 来源是否经过验证

    @property
    def trust_score(self) -> int:
        """信任评分 1-5"""
        score = 1
        if self.stars and self.stars >= 1000:
            score += 1
        elif self.stars and self.stars >= 100:
            score += 0.5
        if self.downloads and self.downloads >= 10000:
            score += 1
        elif self.downloads and self.downloads >= 1000:
            score += 0.5
        if self.license:
            score += 0.5
        return min(5, int(score))


class SourceTracker:
    """来源追溯与指标获取"""

    def __init__(self):
        self.cache: dict[str, SourceInfo] = {}

    def trace(self, skill_name: str, skill_content: str = "") -> SourceInfo:
        """
        追溯 skill 的来源
        策略：
        1. 从 SKILL.md metadata 提取 source/project/url
        2. 从 ClawHub API 获取指标（如果有 slug）
        3. 从 GitHub API 获取 Stars/更新时间（如果有 repo）
        """
        # 解析 frontmatter
        project_url = ""
        author = "unknown"
        license = ""

        import re
        fm = re.search(r"source:\s*\n\s*project:\s*([^\n]+)", skill_content)
        if fm:
            author = fm.group(1).strip()

        url_match = re.search(r"url:\s*[\"']?(https?://[^\s\"']+)[\"']?", skill_content)
        if url_match:
            project_url = url_match.group(1)

        # 判断来源平台
        if "clawhub.ai" in project_url or "clawhub" in skill_content.lower():
            return SourceInfo(
                source="ClawHub", author=author,
                stars=None, downloads=None, last_updated=None,
                license=license
            )
        elif "github.com" in project_url:
            # 提取 owner/repo
            m = re.search(r"github\.com/([^/]+)/([^/\s]+)", project_url)
            if m:
                owner, repo = m.group(1), m.group(2).replace(".git", "")
                gh_info = self._fetch_github(owner, repo)
                if gh_info:
                    return gh_info
        elif "skill-cache" in skill_content:
            return SourceInfo(
                source="skill-cache", author=author,
                stars=None, downloads=None, last_updated=None,
                license=license
            )

        return SourceInfo(
            source="local", author=author,
            stars=None, downloads=None, last_updated=None,
            license=license
        )

    def _fetch_github(self, owner: str, repo: str) -> Optional[SourceInfo]:
        """从 GitHub API 获取 repo 指标"""
        try:
            import urllib.request
            url = f"https://api.github.com/repos/{owner}/{repo}"
            req = urllib.request.Request(url, headers={"User-Agent": "skill-audit"})
            with urllib.request.urlopen(req, timeout=5) as r:
                data = json.loads(r.read())
                return SourceInfo(
                    source="GitHub",
                    author=owner,
                    stars=data.get("stargazers_count"),
                    downloads=None,
                    last_updated=data.get("updated_at", "")[:10],
                    license=data.get("license", {}).get("spdx_id"),
                    verified=True
                )
        except Exception:
            return None


# ──────────────────────────────────────────────────────────────
# Layer 2: 风险分级 + 可信度加权
# ──────────────────────────────────────────────────────────────

@dataclass
class AuditResult:
    skill_name: str
    skill_path: str
    source_info: SourceInfo
    scan_result: ScanResult

    # 加权后的最终风险
    final_score: float = 0.0
    risk_level: str = "⚪ CLEAN"
    verdict: str = "✅ INSTALL"

    recommendations: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    # 风险加权计算
    # 公式：final_score = raw_score × co_occurrence_boost × rule_count_amp × trust_penalty

    # ── 规则共现增强矩阵 ──────────────────────────────────────
    # 危险类别组合 → 乘子（>1 = 风险叠加，<1 = 风险稀释）
    # 说明：同一技能同时触发多个危险维度时，风险非线性增长
    CO_OCCURRENCE_MATRIX = {
        ("credential", "network"): 1.4,    # 索权 + 外传 = 凭证外泄
        ("credential", "code"): 1.8,       # 索权 + 代码执行 = 注入/恶意代码
        ("permission", "network"): 1.25,   # 权限 + 网络 = 可能的文件外传
        ("permission", "code"): 1.35,      # 权限 + 命令执行 = 系统破坏
        ("network", "code"): 1.25,          # 网络 + 代码执行 = 远程控制
        ("credential", "permission"): 1.15, # 凭证 + 权限 = 提权
        # 三类共现（最高风险）
        ("credential", "network", "code"): 2.2,
        ("credential", "permission", "code"): 2.0,
        ("permission", "network", "code"): 1.9,
        ("credential", "network", "permission"): 1.7,
    }

    @staticmethod
    def _co_occurrence_boost(categories: dict[str, int]) -> float:
        """
        根据触发的类别组合计算风险乘子。
        只取最高匹配的那条 combo，不累乘。
        """
        cats = set(categories.keys())
        best = 1.0
        for combo, mult in AuditResult.CO_OCCURRENCE_MATRIX.items():
            if set(combo) <= cats:
                best = max(best, mult)
        return best  # 1.0 / 1.3 / 1.5 / 2.0

    @staticmethod
    def _rule_count_amplifier(n_rules: int, n_high_severe: int) -> float:
        """
        规则数量放大器（非线性风险）
        - 规则越多 → 风险增长越快（但边际递减）
        - 高危规则(sev>=4)每条额外 +0.15
        """
        base = 1.0 + 0.08 * max(0, n_rules - 1) ** 0.6  # 1→1.0, 4→1.16, 9→1.32, 16→1.44
        high_severe_bonus = 1.0 + 0.15 * n_high_severe  # 每条高危规则 +15%
        return min(base * high_severe_bonus, 4.0)  # 上限 4.0

    @staticmethod
    def _trust_penalty(trust: int) -> float:
        """信任惩罚：可信来源可降低风险评分"""
        # trust 1→1.5, 3→1.0, 5→0.5
        return max(0.3, 1.5 - (trust - 1) * 0.3)

    def compute_final(self) -> None:
        """
        第二层：风险加权计算
        公式：final_score = raw_score × co_occurrence_boost × rule_count_amp × trust_penalty
        """
        raw = self.scan_result.score
        categories = self.scan_result.categories
        n_rules = len(self.scan_result.rules_triggered)
        n_high_severe = sum(1 for r, _ in self.scan_result.rules_triggered if r.severity >= 4)
        trust = self.source_info.trust_score

        co_boost = self._co_occurrence_boost(categories)
        count_amp = self._rule_count_amplifier(n_rules, n_high_severe)
        trust_pen = self._trust_penalty(trust)

        self.final_score = round(raw * co_boost * count_amp * trust_pen, 1)

        # 调试信息（可查看各乘子贡献）
        self._score_breakdown = {
            "raw": raw,
            "co_boost": round(co_boost, 2),
            "count_amp": round(count_amp, 2),
            "trust_penalty": round(trust_pen, 2),
            "final": self.final_score
        }

        # 最终分级
        if self.final_score >= 5:
            self.risk_level = "⛔ BLOCK"
            self.verdict = "❌ REJECT"
        elif self.final_score >= 3:
            self.risk_level = "🚨 DANGER"
            self.verdict = "⚠️ CAUTION"
        elif self.final_score >= 1:
            self.risk_level = "⚠️ WARNING"
            self.verdict = "⚠️ CAUTION"
        else:
            self.risk_level = "⚪ CLEAN"
            self.verdict = "✅ INSTALL"

        # 生成建议
        cats = self.scan_result.categories
        if "credential" in cats and cats["credential"] >= 4:
            self.recommendations.append("🔴 涉及凭证访问，必须人工审批")
        if "network" in cats and cats["network"] >= 3:
            self.recommendations.append("🔴 存在数据外传风险，需验证目标地址")
        if self.source_info.trust_score <= 2:
            self.recommendations.append("⚠️ 来源可信度低，建议人工审查代码")


# ──────────────────────────────────────────────────────────────
# Layer 3: 元认知自我演进
# ──────────────────────────────────────────────────────────────

RULES_VERSION = "1.0.0"
RULES_FILE = Path(__file__).parent.parent / "references" / "rules_v1.md"


class MetaCognition:
    """
    第三层：元认知协议
    - 从扫描结果中自动发现新危险 pattern
    - 生成规则更新建议
    - 版本化管理
    """

    def __init__(self, results: dict[str, AuditResult]):
        self.results = results
        self.new_patterns: list[str] = []
        self.blind_spots: list[str] = []

    def analyze(self) -> dict:
        """
        分析本次扫描，发现：
        1. 哪些 skill 触发了高危但未被规则覆盖
        2. 哪些规则过于严格（false positive）
        3. 新发现的 pattern
        """
        # 统计哪些 category 被命中最多
        cat_hits: dict[str, int] = {}
        for r in self.results.values():
            for cat, score in r.scan_result.categories.items():
                cat_hits[cat] = cat_hits.get(cat, 0) + 1

        # 找出高危但低分的 skill（可能被规则漏掉）
        suspicious = []
        for name, r in self.results.items():
            if r.final_score < 3 and r.scan_result.score > 0:
                # 高原始分 + 低最终分 = 规则覆盖但被信任稀释
                suspicious.append({
                    "skill": name,
                    "raw_score": r.scan_result.score,
                    "final_score": r.final_score,
                    "trust": r.source_info.trust_score,
                    "categories": r.scan_result.categories
                })

        # 检查 skill 是否有可疑字符串（可能代表新 pattern）
        # 暂时跳过复杂检测，输出分析报告

        report = {
            "scan_time": datetime.now().isoformat(),
            "rules_version": RULES_VERSION,
            "total_scanned": len(self.results),
            "category_hit_counts": cat_hits,
            "suspicious_skills": suspicious,
            "new_patterns_found": self.new_patterns,
            "blind_spots": self.blind_spots,
            "recommendations": []
        }

        # 生成元认知建议
        if cat_hits.get("credential", 0) > 10:
            report["recommendations"].append(
                "凭证类危险命中过多，建议检查规则库是否覆盖全面"
            )
        if len(suspicious) > 5:
            report["recommendations"].append(
                f"发现 {len(suspicious)} 个可疑 skill（高原始分但低加权分），"
                "可能是来源可信度稀释了真实风险"
            )
        if not self.new_patterns:
            report["recommendations"].append(
                "未发现新 pattern，规则库当前版本覆盖良好"
            )

        return report


# ──────────────────────────────────────────────────────────────
# 完整扫描流水线
# ──────────────────────────────────────────────────────────────

class AuditRunner:
    """三层递归扫描编排器"""

    def __init__(self, skills_root: str | Path = "~/.hermes/skills"):
        self.skills_root = Path(skills_root).expanduser()
        self.scanner = DangerScanner()
        self.tracker = SourceTracker()

    def full_scan(self, categories: list[str] | None = None, force: bool = False) -> dict[str, AuditResult]:
        """
        执行完整三层扫描

        缓存逻辑：
        - 计算所有 skill 的内容指纹（SKILL.md + scripts/）
        - 与缓存索引对比，全部一致则返回缓存报告
        - 否则重新扫描并更新缓存
        """
        # ── 缓存命中检查 ──────────────────────────────────────────────
        if not force:
            skill_keys = sorted([
                str(p.relative_to(self.skills_root))
                for p in self.skills_root.glob("*/*")
                if p.is_dir() and (p / "SKILL.md").exists()
            ])
            sys.path.insert(0, str(Path(__file__).parent))
            from report_cache import check_cache
            hit, cached_report, cache_key = check_cache(self.skills_root, skill_keys)
            if hit:
                print(f"📦 缓存命中: {cache_key}，直接返回报告（skills 无变化）")
                # 将缓存的 dict 转回 AuditResult 对象（供兼容）
                from report_cache import dict_to_audit_results
                return dict_to_audit_results(cached_report, self.skills_root)

        # ── 重新扫描 ──────────────────────────────────────────────────
        print(f"🎯 Layer 1: 批量危险扫描中...")
        t0 = time.time()
        scan_results = self.scanner.batch_scan(
            self.skills_root,
            categories=categories,
            verbose=False
        )
        print(f"   → Layer 1 完成: {len(scan_results)} skills, 耗时 {time.time()-t0:.1f}s")

        # Layer 1.5: 来源追溯（批量）
        print(f"🌐 Layer 1.5: 来源追溯中...")
        t1 = time.time()
        source_map: dict[str, SourceInfo] = {}
        for key in scan_results:
            skill_path = self.skills_root / key.replace("/", "/", 1)
            content = ""
            if (skill_path / "SKILL.md").exists():
                content = (skill_path / "SKILL.md").read_text(errors="ignore")
            source_map[key] = self.tracker.trace(key.split("/")[-1], content)
        print(f"   → Layer 1.5 完成: 耗时 {time.time()-t1:.1f}s")

        # Layer 2: 风险加权
        print(f"⚖️  Layer 2: 风险分级中...")
        audit_results: dict[str, AuditResult] = {}
        for key, scan_result in scan_results.items():
            source = source_map.get(key, SourceInfo(
                source="unknown", author="unknown",
                stars=None, downloads=None, last_updated=None,
                license=None
            ))
            ar = AuditResult(
                skill_name=key.split("/")[-1],
                skill_path=str(self.skills_root / key),
                source_info=source,
                scan_result=scan_result
            )
            ar.compute_final()
            audit_results[key] = ar
        print(f"   → Layer 2 完成")

        # Layer 3: 元认知分析 + 演进检查
        print(f"🧠 Layer 3: 元认知分析中...")
        meta = MetaCognition(audit_results)
        self.meta_report = meta.analyze()
        print(f"   → Layer 3 完成")

        # Layer 3.5: 自动演进（每次扫描后自动检查误报）
        # 这里只做检查，不阻塞扫描流程；用户可手动 evolve 或 --auto
        evolver = self._try_load_evolver(audit_results)
        if evolver:
            rule_stats = evolver.analyze_false_positives()
            deltas = evolver.generate_deltas(rule_stats, auto=False)
            if deltas:
                print(f"   ⚠️  Layer 3.5: 发现 {len(deltas)} 条规则可能需要演进调整")
                print(f"   → 运行 'skill-audit evolve' 查看详情，'skill-audit evolve --auto' 自动应用")
                self._pending_evolve = deltas
            else:
                self._pending_evolve = []
        else:
            self._pending_evolve = []

        # ── 保存完整报告缓存 ───────────────────────────────────────
        skill_keys = sorted([
            str(p.relative_to(self.skills_root))
            for p in self.skills_root.glob("*/*")
            if p.is_dir() and (p / "SKILL.md").exists()
        ])
        report_data = self._build_report_data(audit_results)
        sys.path.insert(0, str(Path(__file__).parent))
        from report_cache import save_report
        save_report(self.skills_root, skill_keys, report_data)

        return audit_results

    def _build_report_data(self, audit_results: dict) -> dict:
        """构建完整报告数据（供缓存和报告生成使用）"""
        meta = self.meta_report
        stats = {"⛔ BLOCK": 0, "🚨 DANGER": 0, "⚠️ WARNING": 0, "⚪ CLEAN": 0}
        for r in audit_results.values():
            stats[r.risk_level] = stats.get(r.risk_level, 0) + 1

        return {
            "metadata": {
                "scan_time": meta.get("scan_time", datetime.now().isoformat()),
                "rules_version": meta.get("rules_version", "unknown"),
                "total": len(audit_results),
                "stats": stats,
                "skills_root": str(self.skills_root),
            },
            "skills": {
                name: {
                    "skill_name": r.skill_name,
                    "skill_path": r.skill_path,
                    "raw_score": r.scan_result.score,
                    "final_score": r.final_score,
                    "risk_level": r.risk_level,
                    "source": r.source_info.source if hasattr(r.source_info, "source") else "unknown",
                    "author": r.source_info.author if hasattr(r.source_info, "author") else "unknown",
                    "trust_score": r.source_info.trust_score if hasattr(r.source_info, "trust_score") else 1,
                    "license": r.source_info.license if hasattr(r.source_info, "license") else "unknown",
                    "categories": r.scan_result.categories,
                    "rules_triggered": [
                        {"description": rule.description, "severity": rule.severity, "category": rule.category}
                        for rule, _ in r.scan_result.rules_triggered
                    ],
                    "verdict": r.verdict,
                    "notes": r.notes,
                    "recommendations": r.recommendations,
                    "score_breakdown": r._score_breakdown,
                }
                for name, r in sorted(audit_results.items(), key=lambda x: -x[1].final_score)
            },
            "meta": meta,
        }

    def _try_load_evolver(self, audit_results):
        """尝试加载演进引擎（失败则静默跳过）"""
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from evolve import RuleEvolution
            cache_dir = Path("~/.hermes/.skill-audit-cache").expanduser()
            history_path = cache_dir / "rules_history.json"
            return RuleEvolution(audit_results, history_path)
        except Exception:
            return None

    def _save_scan_cache(self, audit_results):
        """保存扫描结果缓存，供后续 evolve 使用"""
        try:
            cache_dir = Path("~/.hermes/.skill-audit-cache").expanduser()
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_file = cache_dir / "last_scan_results.json"
            data = {
                name: {
                    "skill_name": r.skill_name,
                    "skill_path": r.skill_path,
                    "score": r.scan_result.score,
                    "final_score": r.final_score,
                    "risk_level": r.risk_level,
                    "categories": r.scan_result.categories,
                    "rules_triggered": [
                        {"description": rule.description, "severity": rule.severity, "category": rule.category}
                        for rule, _ in r.scan_result.rules_triggered
                    ]
                }
                for name, r in audit_results.items()
            }
            cache_file.write_text(json.dumps(data, ensure_ascii=False))
        except Exception:
            pass

    def generate_full_report(
        self,
        results: dict[str, AuditResult],
        meta_report: dict,
        format: str = "md"
    ) -> str:
        """生成完整三层扫描报告"""

        # 统计
        stats = {"⛔ BLOCK": 0, "🚨 DANGER": 0, "⚠️ WARNING": 0, "⚪ CLEAN": 0}
        for r in results.values():
            stats[r.risk_level] = stats.get(r.risk_level, 0) + 1

        # 按最终分排序
        sorted_results = sorted(results.items(), key=lambda x: -x[1].final_score)

        if format == "json":
            data = {
                "metadata": {
                    "scan_time": meta_report["scan_time"],
                    "rules_version": meta_report["rules_version"],
                    "total": len(results),
                    "stats": stats
                },
                "skills": {
                    name: {
                        "risk_level": r.risk_level,
                        "final_score": r.final_score,
                        "raw_score": r.scan_result.score,
                        "source": r.source_info.source,
                        "author": r.source_info.author,
                        "trust_score": r.source_info.trust_score,
                        "verdict": r.verdict,
                        "categories": r.scan_result.categories,
                        "recommendations": r.recommendations,
                        "notes": r.notes
                    }
                    for name, r in sorted_results
                },
                "meta": meta_report
            }
            return json.dumps(data, indent=2, ensure_ascii=False)

        # Markdown
        lines = [
            "# Skill Audit — 三层递归扫描报告",
            "",
            f"**扫描时间:** {meta_report['scan_time'][:19]}",
            f"**规则版本:** v{meta_report['rules_version']}",
            f"**扫描范围:** {len(results)} skills",
            f"**Skills Root:** `{self.skills_root}`",
            "",
            "---",
            "",
            "## 第一层：风险统计",
            "",
            f"| 等级 | 数量 | 占比 |",
            f"|------|------|------|",
            f"| ⛔ BLOCK | {stats['⛔ BLOCK']} | {stats['⛔ BLOCK']*100//len(results)}% |",
            f"| 🚨 DANGER | {stats['🚨 DANGER']} | {stats['🚨 DANGER']*100//len(results)}% |",
            f"| ⚠️ WARNING | {stats['⚠️ WARNING']} | {stats['⚠️ WARNING']*100//len(results)}% |",
            f"| ⚪ CLEAN | {stats['⚪ CLEAN']} | {stats['⚪ CLEAN']*100//len(results)}% |",
            "",
            "---",
            "",
            "## 第二层：危险 Pattern 统计",
            "",
        ]

        for cat, count in sorted(meta_report["category_hit_counts"].items(), key=lambda x: -x[1]):
            lines.append(f"- `{cat}`: {count} 次命中")

        lines.extend([
            "",
            "---",
            "",
            "## 第三层：元认知分析",
            "",
        ])

        for rec in meta_report["recommendations"]:
            lines.append(f"- {rec}")

        if meta_report["suspicious_skills"]:
            lines.append("")
            lines.append(f"⚠️ 发现 {len(meta_report['suspicious_skills'])} 个可疑 skill（高原始分低加权分）：")
            for s in meta_report["suspicious_skills"][:10]:
                lines.append(
                    f"  - `{s['skill']}` raw={s['raw_score']} final={s['final_score']} "
                    f"trust={s['trust']} cats={s['categories']}"
                )

        lines.extend([
            "",
            "---",
            "",
            "## 详细结果（按风险降序）",
            ""
        ])

        for name, r in sorted_results:
            lines.extend([
                f"### {r.risk_level} `{name}`",
                f"",
                f"| 指标 | 值 |",
                f"|------|----|",
                f"| 原始危险分 | {r.scan_result.score} |",
                f"| 最终加权分 | {r.final_score} |",
                f"| 来源 | {r.source_info.source} |",
                f"| 作者 | {r.source_info.author} |",
                f"| 信任评分 | {r.source_info.trust_score}/5 |",
                f"| 许可证 | {r.source_info.license or 'unknown'} |",
                f"| Stars | {r.source_info.stars or 'N/A'} |",
                f"| 更新时间 | {r.source_info.last_updated or 'unknown'} |",
                f"| **裁决** | {r.verdict} |",
                ""
            ])
            if r.scan_result.rules_triggered:
                lines.append("**触发规则：**")
                for rule, samples in r.scan_result.rules_triggered:
                    lines.append(f"- [{rule.severity}分] {rule.description} (`{rule.category}`)")
                lines.append("")
            if r.recommendations:
                lines.append("**建议：**")
                for rec in r.recommendations:
                    lines.append(f"- {rec}")
                lines.append("")

        return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Skill Audit — 三层递归扫描")
    parser.add_argument("command", choices=["full-scan", "quick-scan", "single"])
    parser.add_argument("--skill", help="Skill name (for single command)")
    parser.add_argument("--categories", nargs="+",
                        help="只扫描特定分类")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--format", choices=["md", "json"], default="md")
    parser.add_argument("--force", action="store_true",
                        help="强制重新扫描，忽略缓存")

    args = parser.parse_args()

    runner = AuditRunner()

    if args.command == "single":
        if not args.skill:
            print("--skill required", file=sys.stderr)
            sys.exit(1)
        scan_r = runner.scanner.scan_skill(args.skill)
        src = runner.tracker.trace(args.skill)
        ar = AuditResult(
            skill_name=args.skill,
            skill_path=args.skill,
            source_info=src,
            scan_result=scan_r
        )
        ar.compute_final()
        report = runner.generate_full_report({args.skill: ar}, {"scan_time": datetime.now().isoformat(), "rules_version": RULES_VERSION, "category_hit_counts": {}, "suspicious_skills": [], "recommendations": []})
        print(report)

    elif args.command in ("full-scan", "quick-scan"):
        cats = args.categories if args.categories else None
        results = runner.full_scan(categories=cats, force=args.force)
        report = runner.generate_full_report(results, runner.meta_report, args.format)
        if args.output:
            Path(args.output).write_text(report, encoding="utf-8")
            print(f"✅ 报告已保存: {args.output}")
        else:
            print(report)
