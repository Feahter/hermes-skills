#!/usr/bin/env python3
"""
AI热点搜索 - aihot.today 实时热榜抓取工具
"""

import argparse
import json
import re
import sys
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("请先安装依赖: pip install requests beautifulsoup4")
    sys.exit(1)

BASE_URL = "https://aihot.today"


def fetch_page(url: str, delay: float = 1.0) -> str:
    """抓取页面内容"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    import time
    time.sleep(delay)
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_aihot(html: str) -> dict:
    """解析 aihot.today HTML 页面"""
    soup = BeautifulSoup(html, "html.parser")
    results = {}

    # 找所有新闻卡片
    cards = soup.find_all("div", class_=lambda x: x and "bg-card" in x and "max-w" in x)

    for card in cards:
        # 提取来源名称 (从 logo alt)
        source_img = card.find("img", alt=True)
        source_name = source_img.get("alt", "") if source_img else ""
        # 清理: "TechCrunch logo" -> "TechCrunch"
        source_name = source_name.replace(" logo", "").strip()

        if not source_name:
            continue

        # 提取时间
        time_elem = card.find("span", class_=lambda x: x and "text-blue-600" in str(x))
        time_text = time_elem.get_text(strip=True) if time_elem else ""

        # 找所有外链新闻 (techcrunch.com/202, 36kr.com, github.com 等)
        all_links = card.find_all("a", href=True)
        news_links = [
            l for l in all_links
            if any(domain in l["href"] for domain in [
                "techcrunch.com/202", "36kr.com/", "github.com/", "news.mit.edu",
                "a16z.com", "openai.com", "anthropic.com", "huggingface.co",
                "arxiv.org", "producthunt.com", "news.ycombinator.com"
            ])
        ]

        if source_name not in results:
            results[source_name] = {"time": time_text, "items": []}

        for link in news_links:
            href = link["href"]

            # 提取标题
            title_div = link.find("div", class_=lambda x: x and "font-[500]" in str(x))
            if not title_div:
                continue

            title = title_div.get_text(strip=True)
            # 清理序号: "1. 标题" 或 "1<!-- -->. <!-- -->标题"
            title = re.sub(r"^\d+\.?\s*", "", title).strip()

            if not title or len(title) < 5:
                continue

            # 提取作者
            author_div = link.find("div", class_=lambda x: x and "text-[14px]" in str(x))
            author = author_div.get_text(strip=True) if author_div else ""

            # 避免重复
            if not any(item["title"] == title for item in results[source_name]["items"]):
                results[source_name]["items"].append({
                    "title": title,
                    "author": author,
                    "url": href,
                })

    return results


def format_output(data: dict, source: str = "all", limit: int = 20) -> str:
    """格式化输出"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    output = [f"# 🔥 AI今日热榜 - {now}\n"]

    # 来源名称模糊匹配
    def matches(src_name, target):
        if target == "all":
            return True
        sl = src_name.lower()
        tl = target.lower()
        return sl == tl or tl in sl or sl in tl

    filtered = {k: v for k, v in data.items() if matches(k, source)}

    if not filtered:
        output.append(f"\n未找到来源: {source}\n可用: {', '.join(data.keys())}\n")
        return "".join(output)

    for src_name, src_data in filtered.items():
        src_time = src_data.get("time", "")
        output.append(f"\n## {src_name} ({src_time})\n")
        items = src_data.get("items", [])[:limit]

        if not items:
            output.append("_暂无数据_\n")
            continue

        for i, item in enumerate(items, 1):
            title = item.get("title", "")
            author = item.get("author", "")
            if author and len(author) > 2:
                output.append(f"{i}. {title} — {author}\n")
            else:
                output.append(f"{i}. {title}\n")

    return "".join(output)


def main():
    parser = argparse.ArgumentParser(description="AI热点搜索 - aihot.today")
    parser.add_argument("--source", "-s", default="all")
    parser.add_argument("--limit", "-l", type=int, default=20)
    parser.add_argument("--keyword", "-k", default=None)
    parser.add_argument("--delay", "-d", type=float, default=1.0)
    parser.add_argument("--json", "-j", action="store_true")
    parser.add_argument("--url", default=BASE_URL)

    args = parser.parse_args()

    try:
        print(f"正在抓取 aihot.today ...", file=sys.stderr)
        html = fetch_page(args.url, args.delay)
        data = parse_aihot(html)

        if not data:
            print("未能解析到数据", file=sys.stderr)
            sys.exit(1)

        if args.keyword:
            for src in data:
                data[src]["items"] = [
                    i for i in data[src]["items"]
                    if args.keyword.lower() in i.get("title", "").lower()
                ]

        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(format_output(data, args.source, args.limit))

    except requests.RequestException as e:
        print(f"网络请求失败: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"解析失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
