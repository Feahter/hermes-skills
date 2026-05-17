#!/usr/bin/env python3
"""
Skill Logger CLI - 查询和管理实验日志
"""

import sys
import json
import argparse
from pathlib import Path

LOG_ROOT = Path.home() / ".hermes" / "skills" / ".experiment_log"
INVOCATION_DIR = LOG_ROOT / "invocations"
FAIL_DIR = LOG_ROOT / "fail_cases"
REGRESSION_DIR = LOG_ROOT / "regression_tests"
AB_DIR = LOG_ROOT / "ab_tests"


def cmd_stats():
    """统计信息"""
    inv_files = list(INVOCATION_DIR.glob("*.jsonl"))
    fail_files = list(FAIL_DIR.glob("*.jsonl"))
    reg_files = list(REGRESSION_DIR.glob("*.jsonl"))
    ab_files = list(AB_DIR.glob("*.jsonl"))
    
    total_invocations = 0
    for f in inv_files:
        with open(f) as fp:
            total_invocations += sum(1 for _ in fp)
    
    # 按 skill 统计
    skill_counts = {}
    for f in inv_files:
        with open(f) as fp:
            for line in fp:
                record = json.loads(line)
                skill = record.get("skill_selected", "unknown")
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    # 失败统计
    fail_by_skill = {}
    for f in fail_files:
        skill = f.stem.split("__")[0]
        with open(f) as fp:
            count = sum(1 for _ in fp)
            fail_by_skill[skill] = fail_by_skill.get(skill, 0) + count
    
    print(json.dumps({
        "总调用文件数": len(inv_files),
        "总调用记录数": total_invocations,
        "失败案例文件数": len(fail_files),
        "回归测试文件数": len(reg_files),
        "A/B测试文件数": len(ab_files),
        "按Skill调用统计": skill_counts,
        "按Skill失败统计": fail_by_skill,
        "日志根目录": str(LOG_ROOT),
    }, indent=2, ensure_ascii=False))


def cmd_query(limit: int = 10, skill: str = None):
    """查询最近调用"""
    results = []
    for log_file in sorted(INVOCATION_DIR.glob("*.jsonl"), reverse=True):
        with open(log_file, encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                # 跳过 quality_update 类型的记录
                if record.get("type") == "quality_update":
                    continue
                if skill and record.get("skill_selected") != skill:
                    continue
                results.append(record)
                if len(results) >= limit:
                    break
        if len(results) >= limit:
            break
    
    for r in results:
        ts = r.get("timestamp", "")[:19]
        skill = r.get("skill_selected", "?")
        signal = r.get("quality", {}).get("implicit_signal", "?")
        qhash = r.get("query_hash", "?")
        inv_id = r.get("invocation_id", "?")[:8]
        print(f"[{ts}] {skill} | {signal} | {qhash} | {inv_id}")
        print(f"  query: {r.get('input', {}).get('query', '')[:80]}...")
        if r.get("error"):
            print(f"  ERROR: {r['error'][:100]}")
        print()


def cmd_failures(limit: int = 20, skill: str = None):
    """查询失败案例"""
    results = []
    for fail_file in sorted(FAIL_DIR.glob("*.jsonl"), reverse=True):
        fname = fail_file.stem
        f_skill = fname.split("__")[0]
        if skill and f_skill != skill:
            continue
        with open(fail_file, encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                results.append(record)
                if len(results) >= limit:
                    break
        if len(results) >= limit:
            break
    
    print(f"找到 {len(results)} 条失败案例：\n")
    for r in results:
        ts = r.get("timestamp", "")[:19]
        skill = r.get("failed_skill", "?")
        reason = r.get("failure_reason", "?")[:60]
        print(f"[{ts}] {skill}")
        print(f"  query: {r.get('original_query', '')[:80]}...")
        print(f"  reason: {reason}")
        print()


def cmd_regression(skill: str = None):
    """查看回归测试"""
    if skill:
        files = list(REGRESSION_DIR.glob(f"{skill}__*__regression.jsonl"))
    else:
        files = list(REGRESSION_DIR.glob("*__regression.jsonl"))
    
    for f in sorted(files)[:10]:
        print(f"\n=== {f.name} ===")
        with open(f) as fp:
            for i, line in enumerate(fp):
                if i >= 5:
                    print(f"  ... (还有更多)")
                    break
                record = json.loads(line)
                print(f"  query: {record.get('query', '')[:60]}...")
                print(f"  expected: {record.get('expected_skill', '?')}")


def cmd_start(skill: str, query: str, channel: str = None):
    """记录调用开始"""
    sys.path.insert(0, str(LOG_ROOT))
    from skill_logger import get_logger
    logger = get_logger()
    
    inv_id = logger.log_invocation_start(
        skill_name=skill,
        query=query,
        channel=channel,
    )
    print(inv_id)


def cmd_end(inv_id: str, success: bool, output: str = None, error: str = None):
    """记录调用结束"""
    sys.path.insert(0, str(LOG_ROOT))
    from skill_logger import get_logger
    logger = get_logger()
    
    out_dict = None
    if output:
        try:
            out_dict = json.loads(output)
        except:
            out_dict = {"result": output}
    
    err = None
    if error:
        err = error
    
    logger.log_invocation_end(
        invocation_id=inv_id,
        success=success,
        output=out_dict,
        error=err,
    )
    print("OK")


def main():
    parser = argparse.ArgumentParser(description="Skill Logger CLI")
    parser.add_argument("--stats", action="store_true", help="统计信息")
    parser.add_argument("--query", action="store_true", help="查询最近调用")
    parser.add_argument("--failures", action="store_true", help="查询失败案例")
    parser.add_argument("--regression", action="store_true", help="查看回归测试")
    parser.add_argument("--limit", type=int, default=10, help="限制数量")
    parser.add_argument("--skill", type=str, default=None, help="按Skill过滤")
    
    # 日志记录
    parser.add_argument("--start", action="store_true", help="记录调用开始")
    parser.add_argument("--end", action="store_true", help="记录调用结束")
    parser.add_argument("--inv-id", type=str, default=None, help="调用ID")
    parser.add_argument("--success", action="store_true", default=False, help="是否成功")
    parser.add_argument("--output", type=str, default=None, help="输出摘要(JSON)")
    parser.add_argument("--error", type=str, default=None, help="错误信息")
    parser.add_argument("--channel", type=str, default=None, help="来源渠道")
    parser.add_argument("--query-text", type=str, default=None, help="查询内容(用于--start)")
    
    args = parser.parse_args()
    
    if args.start:
        if not args.skill or not args.query_text:
            print("--start 需要 --skill 和 --query-text")
            sys.exit(1)
        cmd_start(skill=args.skill, query=args.query_text, channel=args.channel)
    elif args.end:
        if not args.inv_id:
            print("--end 需要 --inv-id")
            sys.exit(1)
        cmd_end(inv_id=args.inv_id, success=args.success, output=args.output, error=args.error)
    elif args.stats:
        cmd_stats()
    elif args.query:
        cmd_query(limit=args.limit, skill=args.skill)
    elif args.failures:
        cmd_failures(limit=args.limit, skill=args.skill)
    elif args.regression:
        cmd_regression(skill=args.skill)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
