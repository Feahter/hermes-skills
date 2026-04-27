#!/usr/bin/env python3
"""
generate_readme.py — Generate README.md for hermes-skills repository.
Usage: python3 generate_readme.py [--dry-run]
"""

import argparse, os, re, sys
from datetime import datetime
from pathlib import Path

SKILLS_ROOT = Path(__file__).parent.parent.resolve()


def extract_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter — handles block scalars (|) safely."""
    match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        return {}
    raw = match.group(1)
    fm = {}
    # Split on lines that start a top-level key
    # Top-level keys start at column 0 with word characters
    lines = raw.split("\n")
    buf_key = None
    buf_val = []

    for line in lines:
        # New top-level key
        top_key = re.match(r"^(\w[\w-]*)\s*:\s*(.*)$", line)
        if top_key:
            # Save previous
            if buf_key:
                val_str = " ".join(buf_val).strip()
                # Strip trailing | if it's a block marker
                val_str = re.sub(r"\s*\|$", "", val_str).strip()
                fm[buf_key] = val_str[:200]
            buf_key = top_key.group(1)
            buf_val = [top_key.group(2).strip()]
        elif buf_key and (
            line.startswith("  ") or line.startswith("\t") or line.startswith("  -")
        ):
            # Continuation of previous key (indented or YAML list item)
            buf_val.append(line.strip())
        elif buf_key and not line.strip():
            buf_val.append(" ")
        else:
            # Outside any key — save what we have
            if buf_key:
                val_str = " ".join(buf_val).strip()
                val_str = re.sub(r"\s*\|$", "", val_str).strip()
                fm[buf_key] = val_str[:200]
                buf_key = None
                buf_val = []

    if buf_key:
        val_str = " ".join(buf_val).strip()
        val_str = re.sub(r"\s*\|$", "", val_str).strip()
        fm[buf_key] = val_str[:200]

    return fm


def first_paragraph(content: str) -> str:
    """Get first non-header paragraph as description fallback."""
    stripped = re.sub(r"^---\n.*?\n---\n", "", content, flags=re.DOTALL, count=1)
    chars = []
    for line in stripped.split("\n"):
        line = line.strip()
        if not line:
            if chars:
                break
            continue
        if line.startswith("#"):
            continue
        chars.append(line)
        if len(chars) >= 2:
            break
    return " ".join(chars)[:180]


def scan_skills():
    """Scan all category/skill/SKILL.md files."""
    categories = {}
    total = 0

    for cat_dir in sorted(SKILLS_ROOT.iterdir()):
        if not cat_dir.is_dir() or cat_dir.name.startswith("."):
            continue
        skills = []
        for skill_dir in sorted(cat_dir.iterdir()):
            md = skill_dir / "SKILL.md"
            if not md.exists():
                continue
            try:
                content = md.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            fm = extract_frontmatter(content)
            name = fm.get("name", skill_dir.name)
            desc = fm.get("description", "") or first_paragraph(content)
            # Clean description
            desc = desc.replace("\n", " ").strip()
            if len(desc) > 120:
                desc = desc[:117] + "..."
            kw_raw = fm.get("triggers", "") or fm.get("keywords", "")
            keywords = re.findall(r"[\w\-\u4e00-\u9fff]{2,}", kw_raw)[:8]
            skills.append({
                "name": name,
                "description": desc,
                "keywords": keywords,
                "path": f"{cat_dir.name}/{skill_dir.name}",
            })
            total += 1
        if skills:
            categories[cat_dir.name] = {"skills": skills, "count": len(skills)}
    return categories, total


EMOJI = {
    "ai-agent": "🤖", "autonomous-ai-agents": "🧠", "apple": "🍎",
    "creative": "🎨", "data-science": "🔬", "devops": "⚙️",
    "diagramming": "📊", "dogfood": "🐶", "email": "📧",
    "gaming": "🎮", "github": "🐙", "mcp": "🔌",
    "media": "🖼️", "mlops": "🚀", "note-taking": "📝",
    "productivity": "⚡", "research": "🔍", "smart-home": "🏠",
    "social-media": "📱", "software-development": "💻", "system": "🖥️",
    "thinking": "🧩", "writing": "✍️",
}


def build_readme(categories: dict, total: int) -> str:
    date = datetime.now().strftime("%Y-%m-%d")
    parts = [
        "# hermes-skills",
        "",
        f"> AI Agent Skills Collection · **{total} skills** across **{len(categories)} categories** · {date}",
        "",
        "## Overview",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Skills | {total} |",
        f"| Categories | {len(categories)} |",
        f"| Updated | {date} |",
        "",
        "## Categories",
        "",
        "| Category | Count |",
        "|---------|-------|",
    ]
    for cat in sorted(categories):
        emoji =EMOJI.get(cat, "📦")
        count = categories[cat]["count"]
        parts.append(f"| {emoji} `{cat}` | {count} |")

    for cat in sorted(categories):
        skills = categories[cat]["skills"]
        emoji =EMOJI.get(cat, "📦")
        parts += ["", f"### {emoji} {cat}", "", "| Skill | Description | Triggers |", "|-------|-------------|---------|"]
        for s in skills:
            kw = ", ".join(f"`{k}`" for k in s["keywords"][:4])
            parts.append(f"| `{s['name']}` | {s['description']} | {kw} |")

    parts += ["", "---", "*Generated by `scripts/generate_readme.py`*"]
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    categories, total = scan_skills()
    if args.json:
        import json
        print(json.dumps({"total": total, "categories": {k: {"count": v["count"], "skills": v["skills"]} for k, v in categories.items()}}, indent=2, ensure_ascii=False))
        return
    readme = build_readme(categories, total)
    if args.dry_run:
        print(readme)
    else:
        out = SKILLS_ROOT / "README.md"
        out.write_text(readme, encoding="utf-8")
        print(f"Written: {out} ({total} skills, {len(categories)} categories)")


if __name__ == "__main__":
    main()
