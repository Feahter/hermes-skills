#!/usr/bin/env python3
"""
danger_scanner.py — 危险 Pattern 扫描器
第一层：系统A直觉扫描，高速批量处理 SKILL.md 内容
"""

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ──────────────────────────────────────────────────────────────
# 危险 Pattern 规则库（可演进，支持版本化）
# ──────────────────────────────────────────────────────────────

@dataclass
class DangerRule:
    pattern: str          # 正则或字符串
    severity: int        # 1-5 分
    category: str         # permission/network/code/credential
    description: str     # 人类可读描述
    match_type: str = "regex"  # "regex" | "string" | "path"

    def matches(self, content: str, skill_path: str = "") -> list[str]:
        """返回所有匹配项"""
        if self.match_type == "regex":
            return re.findall(self.pattern, content, re.IGNORECASE | re.MULTILINE)
        elif self.match_type == "string":
            return [m.group(0) for m in re.finditer(re.escape(self.pattern), content, re.I)]
        elif self.match_type == "path":
            # 路径感知：只匹配文件路径上下文
            matches = []
            for line in content.split('\n'):
                if re.search(self.pattern, line, re.I):
                    matches.append(line.strip())
            return matches
        return []


# 规则库（按 severity 分级）
RULES: list[DangerRule] = [
    # ── ⛔ BLOCK (severity=5) ── 最高危
    DangerRule(
        pattern=r"MEMORY\.md|USER\.md|SOUL\.md|IDENTITY\.md",
        severity=5, category="credential",
        description="访问 Agent 记忆/身份文件",
        match_type="regex"
    ),
    DangerRule(
        pattern=r"\.netrc",
        severity=5, category="credential",
        description="访问明文密码文件",
        match_type="regex"
    ),
    # [来自 skill-vetter] 浏览器 cookie/session 访问
    DangerRule(
        pattern=r"browser.*cookie|cookie.*session|session.* hijack",
        severity=5, category="credential",
        description="浏览器 cookie/session 访问",
        match_type="regex"
    ),
    DangerRule(
        pattern=r"/etc/|/System/|/usr/sbin/",
        severity=5, category="permission",
        description="修改系统文件",
        match_type="regex"
    ),
    DangerRule(
        pattern=r"rm\s+-rf\s|rm\s+-rf\s+\$|rm\s+-rf\s+\.",
        severity=5, category="code",
        description="危险删除命令",
        match_type="regex"
    ),
    DangerRule(
        pattern=r"base64.*decode|decode.*base64|frombase64|atob",
        severity=5, category="code",
        description="Base64 解码（代码混淆）",
        match_type="regex"
    ),
    DangerRule(
        pattern=r"base64.*decode|decode.*base64|frombase64|atob",
        severity=5, category="code",
        description="Base64 解码（代码混淆）",
        match_type="regex"
    ),
    DangerRule(
        pattern=r"eval\s*\(|exec\s*\(|__import__|compile\s*\(",
        severity=5, category="code",
        description="动态代码执行",  # [来自 skill-vetter]
        match_type="regex"
    ),
    # [来自 skill-vetter] 安装未声明的包（隐藏依赖）
    DangerRule(
        pattern=r"pip install(?!\s+--|\s+-r|\s+-e)|npm install(?!\s+--|\s+-S|\s+-D|\s+-E)|yarn add(?!\s+--)",
        severity=4, category="permission",
        description="安装未声明的包（隐藏依赖）",
        match_type="regex"
    ),

    # ── 🚨 DANGER (severity=3-4) ── 高风险
    DangerRule(
        pattern=r"~/\.ssh|~/\.aws|~/.gcp|~/.config/wecom|~/.config/tencent",
        severity=4, category="credential",
        description="访问敏感凭证目录",
        match_type="path"
    ),
    # [来自 skill-vetter] 请求凭证/token（vs 使用已有凭证则降为 WARNING）
    # 关键词：request|require|needs.*token|ask.*for|索取|请求.*凭证
    DangerRule(
        pattern=r"(请求|索取|require|request|ask\s+for|needs?\s+)(.{0,20})?(api[_-]?key|apikey|api_key|secret[_-]?key|token|auth|credential|password|passwd|secret)",
        severity=3, category="credential",
        description="请求凭证/token",  # [来自 skill-vetter]
        match_type="regex"
    ),
    DangerRule(
        pattern=r"send.*data.*external|exfiltrat|外传|发送到.*外部|cURL.*http:\/\/(?!.*https)",
        severity=4, category="network",
        description="数据外传风险",
        match_type="regex"
    ),
    DangerRule(
        pattern=r"curl\s+http:\/\/(?!.*https)|wget\s+http:\/\/",
        severity=3, category="network",
        description="非加密传输（HTTP）",
        match_type="regex"
    ),
    DangerRule(
        pattern=r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",  # IP 地址而非域名
        severity=3, category="network",
        description="网络调用到 IP 地址",
        match_type="regex"
    ),
    DangerRule(
        pattern=r"npm\s+install\s+-g|pip\s+install\s+--user|apt-get\s+install",
        severity=3, category="permission",
        description="全局安装包（可能污染系统）",
        match_type="regex"
    ),
    DangerRule(
        pattern=r"sudo\s+|chmod\s+777|chown\s+",
        severity=3, category="permission",
        description="请求管理员/危险权限",
        match_type="regex"
    ),
    DangerRule(
        pattern=r"~\/\.bashrc|~\/\.zshrc|~\/\.profile|~\/\.zprofile",
        severity=3, category="permission",
        description="修改 shell 配置文件",
        match_type="path"
    ),
    DangerRule(
        pattern=r"subprocess|os\.system|spawn\(|Popen\(",
        severity=3, category="code",
        description="命令执行",
        match_type="regex"
    ),
    DangerRule(
        pattern=r"compress|obfusc|mminify|uglif",
        severity=3, category="code",
        description="代码混淆/压缩",
        match_type="regex"
    ),

    # ── ⚠️ WARNING (severity=1-2) ── 警告，需复核
    DangerRule(
        pattern=r"~\/\.config|~\/\.local|~\/\.cache",
        severity=2, category="permission",
        description="访问用户配置目录",
        match_type="path"
    ),
    DangerRule(
        pattern=r"download|fetch|get.*from.*url",
        severity=2, category="network",
        description="网络下载行为",
        match_type="regex"
    ),
    DangerRule(
        pattern=r"read.*file|write.*file|patch|edit.*file",
        severity=1, category="permission",
        description="文件读写操作",
        match_type="regex"
    ),
    DangerRule(
        pattern=r"terminal\(|bash|shell|cmd.exe|powershell",
        severity=2, category="code",
        description="终端命令执行",
        match_type="regex"
    ),
]


# ──────────────────────────────────────────────────────────────
# 扫描结果数据结构
# ──────────────────────────────────────────────────────────────

@dataclass
class ScanResult:
    skill_name: str
    skill_path: str
    score: int = 0
    rules_triggered: list[tuple[DangerRule, list[str]]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def severity_label(self) -> str:
        if self.score >= 5:
            return "⛔ BLOCK"
        elif self.score >= 3:
            return "🚨 DANGER"
        elif self.score >= 1:
            return "⚠️ WARNING"
        else:
            return "⚪ CLEAN"

    @property
    def categories(self) -> dict[str, int]:
        """各危险类别的最高分"""
        cat_scores: dict[str, int] = {}
        for rule, _ in self.rules_triggered:
            cat_scores[rule.category] = max(cat_scores.get(rule.category, 0), rule.severity)
        return cat_scores


# ──────────────────────────────────────────────────────────────
# 核心扫描器
# ──────────────────────────────────────────────────────────────

class DangerScanner:
    def __init__(self, rules: list[DangerRule] | None = None):
        self.rules = rules or RULES

    def scan_skill(self, skill_path: str | Path) -> ScanResult:
        """扫描单个 skill 的 SKILL.md"""
        skill_path = Path(skill_path)
        skill_name = skill_path.name
        skill_dir = skill_path if skill_path.is_dir() else skill_path.parent

        # 读取 SKILL.md（主文件）
        content = ""
        sk_md = skill_dir / "SKILL.md"
        if sk_md.exists():
            content = sk_md.read_text(encoding="utf-8", errors="ignore")

        # 也扫描 scripts/ 和 references/
        for subdir in ("scripts", "references", "assets"):
            for f in (skill_dir / subdir).glob("*"):
                if f.is_file() and f.suffix in (".py", ".sh", ".js", ".ts", ".yaml", ".yml"):
                    try:
                        content += "\n" + f.read_text(encoding="utf-8", errors="ignore")
                    except Exception:
                        pass

        result = ScanResult(skill_name=skill_name, skill_path=str(skill_dir))

        for rule in self.rules:
            matches = rule.matches(content, str(skill_dir))
            if matches:
                result.rules_triggered.append((rule, matches[:5]))  # 最多5条示例
                result.score += rule.severity

        # 如果没有任何文件，大概率是空 skill
        if not content.strip():
            result.warnings.append("SKILL.md 为空或仅含空白字符")

        return result

    def batch_scan(
        self,
        skills_root: str | Path,
        categories: list[str] | None = None,
        verbose: bool = False
    ) -> dict[str, ScanResult]:
        """
        批量扫描 skills_root 下的所有 skills
        categories: None = 扫描全部；list = 只扫描指定分类目录
        """
        skills_root = Path(skills_root)
        results: dict[str, ScanResult] = {}

        # 收集所有 skill 目录
        skill_dirs: list[tuple[str, Path]] = []
        if categories:
            for cat in categories:
                cat_path = skills_root / cat
                if cat_path.exists():
                    skill_dirs.extend(
                        (cat, p) for p in cat_path.iterdir()
                        if p.is_dir() and (p / "SKILL.md").exists()
                    )
        else:
            # 全量扫描，跳过 openclaw-imports（已清空）
            for cat_path in skills_root.iterdir():
                if cat_path.is_dir() and cat_path.name not in ("openclaw-imports", "skill-cache"):
                    skill_dirs.extend(
                        (cat_path.name, p) for p in cat_path.iterdir()
                        if p.is_dir() and (p / "SKILL.md").exists()
                    )

        for category, skill_path in skill_dirs:
            key = f"{category}/{skill_path.name}"
            try:
                result = self.scan_skill(skill_path)
                results[key] = result
                if verbose:
                    print(f"[{result.severity_label}] {key} (score={result.score})")
            except Exception as e:
                print(f"[ERROR] {key}: {e}", file=sys.stderr)

        return results

    def generate_report(self, results: dict[str, ScanResult], format: str = "md") -> str:
        """生成扫描报告"""
        if format == "json":
            import json
            data = {
                name: {
                    "score": r.score,
                    "severity": r.severity_label,
                    "categories": r.categories,
                    "rules": [
                        {"rule": rule.description, "severity": rule.severity, "samples": samples}
                        for rule, samples in r.rules_triggered
                    ],
                    "warnings": r.warnings
                }
                for name, r in results.items()
            }
            return json.dumps(data, indent=2, ensure_ascii=False)

        # Markdown 格式
        lines = [
            "# Skill Audit Report",
            "",
            f"**扫描时间:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**扫描范围:** {len(results)} skills",
            "",
            "---",
            "",
            "## 风险分级统计",
            ""
        ]

        stats = {"⛔ BLOCK": [], "🚨 DANGER": [], "⚠️ WARNING": [], "⚪ CLEAN": []}
        for name, r in sorted(results.items(), key=lambda x: -x[1].score):
            stats[r.severity_label].append(name)

        for label, items in stats.items():
            count = len(items)
            if count > 0:
                lines.append(f"### {label}: {count} skills")
                for item in items:
                    r = results[item]
                    lines.append(f"- `{item}` (score={r.score})")
                lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("## 详细扫描结果")
        lines.append("")

        for name, r in sorted(results.items(), key=lambda x: -x[1].score):
            if r.score == 0:
                continue
            lines.append(f"### `{name}` — {r.severity_label} (score={r.score})")
            if r.warnings:
                for w in r.warnings:
                    lines.append(f"- ⚠️ {w}")
            for rule, samples in r.rules_triggered:
                lines.append(f"- [{rule.severity}分] **{rule.description}** (`{rule.category}`)")
                for s in samples[:3]:
                    lines.append(f"  - `{s[:100]}`")
            lines.append("")

        return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# CLI 入口
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Skill Danger Scanner")
    parser.add_argument("command", choices=["scan", "batch", "report"],
                        help="scan=single skill, batch=full scan, report=generate from last scan")
    parser.add_argument("--skill", help="Skill name or path (for scan)")
    parser.add_argument("--skills-root", default="~/.hermes/skills",
                        help="Skills root directory")
    parser.add_argument("--categories", nargs="+",
                        help="Only scan specific categories")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--format", choices=["md", "json"], default="md")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    scanner = DangerScanner()

    if args.command == "scan":
        if not args.skill:
            print("Error: --skill required for scan command", file=sys.stderr)
            sys.exit(1)
        result = scanner.scan_skill(args.skill)
        print(f"Skill: {result.skill_name}")
        print(f"Score: {result.score}")
        print(f"Severity: {result.severity_label}")
        for rule, samples in result.rules_triggered:
            print(f"  [{rule.severity}P] {rule.description}")
            for s in samples[:3]:
                print(f"    → {s[:120]}")

    elif args.command == "batch":
        results = scanner.batch_scan(
            args.skills_root,
            categories=args.categories,
            verbose=args.verbose
        )
        report = scanner.generate_report(results, args.format)
        if args.output:
            Path(args.output).write_text(report, encoding="utf-8")
            print(f"Report saved to {args.output}")
        else:
            print(report)

    elif args.command == "report":
        print("Use 'batch' command to generate report from scan results")
