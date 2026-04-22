#!/usr/bin/env python3
"""
source_tracker.py — 来源追溯与信任评分
"""

import json
import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class SourceInfo:
    source: str           # ClawHub / GitHub / skill-cache / local / unknown
    author: str
    repo: Optional[str]
    stars: Optional[int]
    downloads: Optional[int]
    last_updated: Optional[str]
    license: Optional[str]
    verified: bool       # 是否成功验证来源
    raw_url: Optional[str]

    @property
    def trust_score(self) -> int:
        """信任评分 1-5"""
        score = 1.0
        if self.stars and self.stars >= 1000:
            score += 1.5
        elif self.stars and self.stars >= 100:
            score += 0.75
        if self.downloads and self.downloads >= 10000:
            score += 1.5
        elif self.downloads and self.downloads >= 1000:
            score += 0.75
        if self.license and self.license != "NOASSERTION":
            score += 0.5
        if self.verified:
            score += 0.5
        return min(5, int(score))

    @property
    def trust_label(self) -> str:
        labels = {1: "❌ Untrusted", 2: "⚠️ Low", 3: "🟡 Medium", 4: "🟢 High", 5: "✅ Trusted"}
        return labels.get(self.trust_score, "unknown")


class SourceTracker:
    """追溯 skill 来源，获取公开指标"""

    def __init__(self, cache_dir: str = "~/.hermes/.skill-audit-cache"):
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory: dict[str, SourceInfo] = {}

    def trace(self, skill_name: str, skill_path: str | Path = "") -> SourceInfo:
        """
        追溯来源，优先级：
        1. 查内存缓存
        2. 解析 SKILL.md frontmatter
        3. 查询 GitHub API（如果有 repo URL）
        4. fallback: local / unknown
        """
        cache_key = skill_name
        if cache_key in self._memory:
            return self._memory[cache_key]

        # 读取 SKILL.md 内容
        content = ""
        if skill_path:
            p = Path(skill_path)
            if p.is_dir():
                p = p / "SKILL.md"
            if p.exists():
                content = p.read_text(errors="ignore")

        # 提取 frontmatter
        fm = self._parse_frontmatter(content)

        # 提取 URL
        url = fm.get("url") or ""
        project = fm.get("project", "")

        # 判断来源
        if "clawhub.ai" in url:
            info = self._fetch_clawhub(skill_name)
        elif "github.com" in url:
            m = re.search(r"github\.com/([^/]+)/([^/\s#?]+)", url)
            if m:
                info = self._fetch_github(m.group(1), m.group(2))
                info.author = m.group(1)
            else:
                info = SourceInfo(
                    source="GitHub", author=project or "unknown",
                    repo=None, stars=None, downloads=None,
                    last_updated=None, license=None, verified=False, raw_url=url
                )
        elif "gitlab.com" in url:
            info = SourceInfo(
                source="GitLab", author=project or "unknown",
                repo=None, stars=None, downloads=None,
                last_updated=None, license=None, verified=False, raw_url=url
            )
        elif not url or not content:
            # 纯本地 skill
            info = SourceInfo(
                source="local", author=project or "unknown",
                repo=None, stars=None, downloads=None,
                last_updated=None, license=None, verified=False, raw_url=None
            )
        else:
            info = SourceInfo(
                source="unknown", author=project or "unknown",
                repo=None, stars=None, downloads=None,
                last_updated=None, license=None, verified=False, raw_url=url
            )

        self._memory[cache_key] = info
        return info

    def _parse_frontmatter(self, content: str) -> dict:
        """解析 YAML frontmatter"""
        fm = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not fm:
            return {}
        result = {}
        for line in fm.group(1).split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                result[key.strip()] = val.strip().strip('"').strip("'")
        return result

    def _fetch_github(self, owner: str, repo: str) -> SourceInfo:
        """从 GitHub REST API 获取元数据（无需 auth，60 req/hour）"""
        cache_file = self.cache_dir / f"github_{owner}_{repo}.json"
        if cache_file.exists():
            import time
            mtime = cache_file.stat().st_mtime
            if time.time() - mtime < 3600:  # 1小时缓存
                data = json.loads(cache_file.read_text())
                return SourceInfo(
                    source="GitHub", author=owner, repo=f"{owner}/{repo}",
                    stars=data.get("stargazers_count"),
                    downloads=None,
                    last_updated=data.get("updated_at", "")[:10] if data.get("updated_at") else None,
                    license=data.get("license", {}).get("spdx_id") if isinstance(data.get("license"), dict) else (data.get("license") or None),
                    verified=True,
                    raw_url=f"https://github.com/{owner}/{repo}"
                )

        try:
            url = f"https://api.github.com/repos/{owner}/{repo}"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "skill-audit/1.0", "Accept": "application/vnd.github.v3+json"}
            )
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read())
                cache_file.write_text(json.dumps(data))
                return SourceInfo(
                    source="GitHub", author=owner, repo=f"{owner}/{repo}",
                    stars=data.get("stargazers_count"),
                    downloads=None,
                    last_updated=data.get("updated_at", "")[:10] if data.get("updated_at") else None,
                    license=data.get("license", {}).get("spdx_id") if isinstance(data.get("license"), dict) else (data.get("license") or None),
                    verified=True,
                    raw_url=f"https://github.com/{owner}/{repo}"
                )
        except Exception as e:
            return SourceInfo(
                source="GitHub", author=owner, repo=f"{owner}/{repo}",
                stars=None, downloads=None,
                last_updated=None, license=None, verified=False, raw_url=f"https://github.com/{owner}/{repo}"
            )

    def _fetch_clawhub(self, skill_slug: str) -> SourceInfo:
        """从 ClawHub 获取指标（实验性，API 不稳定）"""
        try:
            # ClawHub 使用 Convex，需要找对 API 端点
            url = f"https://clawhub.ai/api/v1/skills/{skill_slug}"
            req = urllib.request.Request(url, headers={"User-Agent": "skill-audit/1.0"})
            with urllib.request.urlopen(req, timeout=5) as r:
                data = json.loads(r.read())
                return SourceInfo(
                    source="ClawHub", author=data.get("author", "unknown"),
                    repo=None,
                    stars=data.get("stars"),
                    downloads=data.get("downloads"),
                    last_updated=data.get("updatedAt", "")[:10] if data.get("updatedAt") else None,
                    license=data.get("license"),
                    verified=True, raw_url=f"https://clawhub.ai/{skill_slug}"
                )
        except Exception:
            return SourceInfo(
                source="ClawHub", author="unknown",
                repo=None, stars=None, downloads=None,
                last_updated=None, license=None, verified=False, raw_url=None
            )
