#!/usr/bin/env python3
"""
evolve.py — Skill-Audit 演进引擎
参考 skill-evolution-manager 模式：
  evolution.json  →  rules_history.json（规则演进史）
  merge_evolution.py → merge_rule_delta.py（合并规则增量）
  smart_stitch.py  →  stitch_rules.py（将规则变更缝合回 danger_scanner.py）

触发条件：
  1. scan 后发现 false positive > 30% → 自动触发
  2. 手动：skill-audit evolve
  3. 手动：skill-audit evolve --auto（自动模式，无确认）

关键约束（来自 reflect-learn）：
  - 不直接修改正文，通过增量 JSON 持久化
  - 每次演进生成新版本，不覆盖历史
  - 有人工确认环节（除非 --auto）
"""

import json
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


# ──────────────────────────────────────────────────────────────
# 规则演进历史数据模型（对应 evolution.json）
# ──────────────────────────────────────────────────────────────

@dataclass
class RuleDelta:
    """单次规则变更记录"""
    version: str                     # e.g. "1.0.0→1.1.0"
    timestamp: str
    trigger: str                     # 触发原因
    rule_id: str                     # 对应 danger_scanner.py 中的规则标识
    action: str                      # "downgrade" | "upgrade" | "add" | "remove" | "new_pattern"
    old_severity: Optional[int]
    new_severity: Optional[int]
    reason: str                      # 变更理由
    evidence: list[str]               # 支持证据（skill 名称列表）
    false_positive_rate: float        # 该规则的误报率
    accepted: bool = True             # 是否已确认


@dataclass
class RulesHistory:
    """规则演进历史（对应 rules_history.json）"""
    current_version: str
    total_evolutions: int
    last_evolved: Optional[str]
    deltas: list  # list of RuleDelta as dict
    false_positive_stats: dict  # rule_id → {"total": N, "fp": M}


# ──────────────────────────────────────────────────────────────
# 核心演进逻辑
# ──────────────────────────────────────────────────────────────

class RuleEvolution:
    """
    演进引擎：分析扫描结果 → 发现误报规则 → 生成增量 → 缝合
    """

    # 误报判定阈值：某规则在 N 个 clean skill 中触发 > FP_THRESHOLD 则为误报
    FP_THRESHOLD = 0.30

    # 演进触发条件
    # 原策略：fp_rate > 30% 且 clean 命中 >= 3
    # 问题：final_score < 1 的 clean 集碰不到高频规则（如 terminal/code/exec），永远是 0
    # 新策略：规则在大量 skill 中普遍触发，但 high_risk 占比低 → 过于宽泛
    TRIGGER_FP_RATE = 0.20   # high_risk 占比 < 20% → 规则过于宽泛
    TRIGGER_HIT_COUNT = 20    # 某规则命中 > 20 个 skill

    def __init__(self, audit_results: dict, rules_history_path: Path):
        self.audit_results = audit_results
        self.rules_history_path = rules_history_path
        self.history = self._load_history()
        self.deltas: list[RuleDelta] = []

    # ── 1. 加载历史 ──────────────────────────────────────────

    def _load_history(self) -> RulesHistory:
        if self.rules_history_path.exists():
            data = json.loads(self.rules_history_path.read_text())
            return RulesHistory(
                current_version=data["current_version"],
                total_evolutions=data["total_evolutions"],
                last_evolved=data.get("last_evolved"),
                deltas=[RuleDelta(**d) for d in data.get("deltas", [])],
                false_positive_stats=data.get("false_positive_stats", {})
            )
        return RulesHistory(
            current_version="1.0.0",
            total_evolutions=0,
            last_evolved=None,
            deltas=[],
            false_positive_stats={}
        )

    def _save_history(self) -> None:
        self.rules_history_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "current_version": self.history.current_version,
            "total_evolutions": self.history.total_evolutions,
            "last_evolved": self.history.last_evolved,
            "deltas": [asdict(d) for d in self.history.deltas],
            "false_positive_stats": self.history.false_positive_stats
        }
        self.rules_history_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    # ── 2. False Positive 分析 ───────────────────────────────

    def analyze_false_positives(self) -> dict[str, dict]:
        """
        分析每个规则的误报率。
        策略：统计规则在各风险分段的命中分布。
        如果规则主要命中的是 final_score < 3 的 skill（而非最高风险段），
        说明该规则过于宽泛，缺乏特异性。
        """
        # 统计每个规则在各分段的命中
        rule_stats: dict[str, dict] = {}

        for skill_name, result in self.audit_results.items():
            # 兼容 dict（来自缓存）和对象（直接传入）
            if isinstance(result, dict):
                final_score = result.get("final_score", result.get("score", 0))
                rules_triggered = result.get("rules_triggered", [])
                scan_result_rules = []
                for r in rules_triggered:
                    @dataclass
                    class FakeRule:
                        category: str
                        description: str
                        severity: int
                    scan_result_rules.append((FakeRule(
                        category=r.get("category", ""),
                        description=r.get("description", ""),
                        severity=r.get("severity", 1)
                    ), None))
                rules_triggered = scan_result_rules
            else:
                final_score = result.final_score
                rules_triggered = result.scan_result.rules_triggered

            # 按分桶统计
            if final_score < 1.0:
                bucket = "clean"
            elif final_score < 3.0:
                bucket = "medium"
            else:
                bucket = "high_risk"

            for rule, _ in rules_triggered:
                rule_key = f"{rule.category}:{rule.description}"
                if rule_key not in rule_stats:
                    rule_stats[rule_key] = {
                        "rule_id": rule_key,
                        "category": rule.category,
                        "description": rule.description,
                        "severity": rule.severity,
                        "total_hits": 0,
                        "clean_hits": 0,       # final_score < 1
                        "medium_hits": 0,      # 1 <= final_score < 3
                        "high_risk_hits": 0,   # final_score >= 3
                        "affected_skills": []
                    }
                stats = rule_stats[rule_key]
                stats["total_hits"] += 1
                stats[f"{bucket}_hits"] += 1
                if skill_name not in stats["affected_skills"]:
                    stats["affected_skills"].append(skill_name)

        # 计算各分桶占比（用于判断宽泛程度）
        for stats in rule_stats.values():
            total = max(stats["total_hits"], 1)
            # 宽泛度 = (clean + medium) / total；越高说明越泛化
            stats["broad_rate"] = round((stats["clean_hits"] + stats["medium_hits"]) / total, 3)
            # 特异性 = high_risk / total；越高说明越专一于高风险
            stats["specificity"] = round(stats["high_risk_hits"] / total, 3)

        return rule_stats

    # ── 3. 生成规则增量 ───────────────────────────────────────

    def generate_deltas(self, rule_stats: dict[str, dict], auto: bool = False) -> list[RuleDelta]:
        """
        基于误报分析生成规则变更建议。
        仅当 auto=False 时生成需要确认的 delta；auto=True 时直接生成已接受的 delta。
        """
        new_deltas: list[RuleDelta] = []
        current = self.history.current_version  # e.g. "1.0.0"

        for rule_key, stats in sorted(rule_stats.items(), key=lambda x: -x[1]["broad_rate"]):
            fp_rate = stats["broad_rate"]
            total = stats["total_hits"]
            clean = stats["clean_hits"]
            high_risk = stats["high_risk_hits"]

            # 触发条件：命中够多 + 宽泛度高（broad_rate > 70%，即命中主要集中在非高风险 skill）
            if total >= self.TRIGGER_HIT_COUNT and stats["broad_rate"] > 0.70:
                # 判断严重程度
                if stats["severity"] >= 4:
                    # 高严重度规则的误报更不能忍，降级
                    new_sev = max(1, stats["severity"] - 2)
                    action = "downgrade"
                    reason = (
                        f"宽泛度 {stats['broad_rate']:.0%}（非高风险命中 {clean + stats['medium_hits']}/{total}），"
                        f"原 severity={stats['severity']} 过高，在大量 skill 中普遍触发"
                    )
                elif stats["severity"] >= 3:
                    new_sev = stats["severity"] - 1
                    action = "downgrade"
                    reason = f"宽泛度 {stats['broad_rate']:.0%}，降为 WARNING 级"
                else:
                    new_sev = stats["severity"]
                    action = "flag"
                    reason = f"宽泛度 {stats['broad_rate']:.0%}，但已是最低级，仅标记"

                delta = RuleDelta(
                    version=f"{current}→{current}",  # 版本不变，累积在 history 里
                    timestamp=datetime.now().isoformat(),
                    trigger=f"broad_rate={stats['broad_rate']:.0%}, total={total}",
                    rule_id=rule_key,
                    action=action,
                    old_severity=stats["severity"],
                    new_severity=new_sev,
                    reason=reason,
                    evidence=stats["affected_skills"][:5],
                    false_positive_rate=fp_rate,
                    accepted=auto  # auto=True 则直接接受
                )
                new_deltas.append(delta)

        return new_deltas

    # ── 4. 合并增量到历史 ────────────────────────────────────

    def merge_deltas(self, deltas: list[RuleDelta]) -> None:
        """将新 delta 合并到历史，更新统计数据"""
        for delta in deltas:
            # 更新 false_positive_stats
            rid = delta.rule_id
            if rid not in self.history.false_positive_stats:
                self.history.false_positive_stats[rid] = {"total": 0, "fp": 0, "evolutions": 0}
            stats = self.history.false_positive_stats[rid]
            # 从当前审计结果重新统计（简化：直接用本次 delta 的数据）
            stats["evolutions"] += 1

        self.history.deltas.extend(deltas)
        self.history.total_evolutions += len([d for d in deltas if d.accepted])
        self.history.last_evolved = datetime.now().isoformat()
        self._save_history()

    # ── 5. 生成规则变更补丁（供人工确认） ───────────────────

    def generate_patch_proposal(self, deltas: list[RuleDelta]) -> str:
        """生成供人工Review的变更建议"""
        lines = [
            "# 规则演进补丁建议",
            "",
            f"**当前版本:** {self.history.current_version}",
            f"**待应用变更:** {len(deltas)} 条",
            f"**自动模式:** 否（需人工确认）",
            "",
            "---",
            ""
        ]
        for i, d in enumerate(deltas):
            lines.extend([
                f"## [{i+1}] {d.action.upper()}: `{d.rule_id}`",
                f"- 规则描述: {d.reason}",
                f"- 变更: severity {d.old_severity} → {d.new_severity}",
                f"- 误报率: {d.false_positive_rate:.0%}",
                f"- 证据（受影响 skill）: {', '.join(d.evidence)}",
                ""
            ])

        lines.extend([
            "---",
            "",
            "## 操作选项",
            "",
            "```",
            "evolve --accept      # 接受全部变更",
            "evolve --reject      # 拒绝全部变更",
            "evolve --accept 1,3  # 只接受第1、3条",
            "```",
            ""
        ])
        return "\n".join(lines)

    # ── 6. 缝合回 danger_scanner.py ──────────────────────────

    def stitch_rules(self, accepted_deltas: list[RuleDelta]) -> str:
        """
        将已接受的 delta 缝合回 RULES 列表。
        生成 rules_v{N}.py 文件，实际使用时 import 该文件覆盖 RULES。
        不直接修改 danger_scanner.py（保留原始规则库）。
        """
        if not accepted_deltas:
            return "No deltas to stitch."

        # 生成规则覆盖文件
        override_lines = [
            "#!/usr/bin/env python3",
            f"# Auto-generated by skill-audit evolve on {datetime.now().isoformat()}",
            f"# Version: {self.history.current_version}",
            "",
            "# This file overrides RULES in danger_scanner.py",
            "# It reflects learned false-positive adjustments from scan history.",
            "",
            "RULE_OVERRIDES = {",
        ]

        for d in accepted_deltas:
            if d.action == "downgrade" and d.new_severity is not None:
                override_lines.append(
                    f'    "{d.rule_id}": {d.new_severity},  # {d.reason[:60]}...'
                )

        override_lines.extend([
            "}",
            "",
            "# Affected skills (for audit trail):",
        ])
        for d in accepted_deltas:
            override_lines.append(f"#   - {d.rule_id}: {', '.join(d.evidence[:3])}")

        override_path = self.rules_history_path.parent / f"rules_v{self.history.current_version}.py"
        override_path.write_text("\n".join(override_lines))

        # 生成缝合报告
        lines = [
            "✅ 规则已演进缝合",
            "",
            f"覆盖规则文件: `{override_path.name}`",
            f"变更数量: {len(accepted_deltas)} 条",
            "",
            "| 规则 | 原 severity | 新 severity | 误报率 |",
            "|------|------------|-------------|--------|",
        ]
        for d in accepted_deltas:
            lines.append(
                f"| `{d.rule_id[:40]}` | {d.old_severity} | {d.new_severity} | "
                f"{d.false_positive_rate:.0%} |"
            )

        return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────

def load_last_scan_results(results_dir: Path) -> dict:
    """从上次扫描结果加载（或重新扫描）"""
    # 优先从缓存读取
    cache_file = results_dir / "last_scan_results.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text())
    # 否则返回空（调用方需重新扫描）
    return {}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Skill-Audit 演进引擎")
    parser.add_argument("command", choices=["evolve", "status", "patch"])
    parser.add_argument("--auto", action="store_true",
                        help="自动模式：直接应用变更，无需人工确认")
    parser.add_argument("--accept", help="接受指定序号，多个用逗号分隔")
    parser.add_argument("--reject", action="store_true", help="拒绝所有待处理变更")
    parser.add_argument("--results-dir", default="~/.hermes/.skill-audit-cache",
                        help="扫描结果缓存目录")
    args = parser.parse_args()

    results_dir = Path(args.results_dir).expanduser()
    history_path = results_dir / "rules_history.json"

    if args.command == "status":
        # 显示当前状态
        if history_path.exists():
            h = json.loads(history_path.read_text())
            print(f"当前版本: {h['current_version']}")
            print(f"演进次数: {h['total_evolutions']}")
            print(f"上次演进: {h.get('last_evolved', '从未')}")
            print(f"规则变更记录: {len(h.get('deltas', []))} 条")
        else:
            print("从未进行过演进")
        return

    if args.command == "evolve":
        # 加载上次扫描结果
        results = load_last_scan_results(results_dir)
        if not results:
            print("没有找到上次扫描结果，请先运行: skill-audit full-scan")
            return

        evolver = RuleEvolution(results, history_path)

        # 分析误报
        print("🔍 分析误报模式中...")
        rule_stats = evolver.analyze_false_positives()

        # 生成增量
        deltas = evolver.generate_deltas(rule_stats, auto=args.auto)
        if not deltas:
            print("✅ 未发现需要演进的规则，当前规则库运行良好")
            return

        print(f"📋 发现 {len(deltas)} 条规则需要调整")

        if args.auto:
            # 自动模式：直接应用
            evolver.merge_deltas(deltas)
            report = evolver.stitch_rules(deltas)
            print(report)
        elif args.accept:
            # 部分接受
            indices = [int(x) for x in args.accept.split(",")]
            accepted = [deltas[i] for i in indices if i < len(deltas)]
            for d in accepted:
                d.accepted = True
            evolver.merge_deltas(accepted)
            report = evolver.stitch_rules(accepted)
            print(report)
        elif args.reject:
            print("已拒绝所有变更")
        else:
            # 显示建议，等待确认
            print(evolver.generate_patch_proposal(deltas))

    if args.command == "patch":
        # 显示历史补丁
        if history_path.exists():
            h = json.loads(history_path.read_text())
            deltas = h.get("deltas", [])
            if deltas:
                print(f"共 {len(deltas)} 条历史变更：")
                for d in deltas[-10:]:
                    print(f"  [{d['action']}] {d['rule_id'][:50]} | {d['old_severity']}→{d['new_severity']} | {d['reason'][:50]}")
            else:
                print("无历史变更记录")
        else:
            print("无演进历史")


if __name__ == "__main__":
    main()
