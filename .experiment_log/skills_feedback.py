#!/usr/bin/env python3
"""
Skills Feedback Loop CLI - 三阶段合一
Phase 1: 调用日志
Phase 2: 回归测试 + A/B 测试
Phase 3: Boundary Detector

用法:
    python3 skills_feedback.py --stats
    python3 skills_feedback.py --scan coding-agent
    python3 skills_feedback.py --probe coding-agent
    python3 skills_feedback.py --check coding-agent "很长的query..."
    python3 skills_feedback.py --full-loop coding-agent
"""

import argparse
import sys
import json
from pathlib import Path

LOG_ROOT = Path.home() / ".hermes" / "skills" / ".experiment_log"

# 添加到路径
sys.path.insert(0, str(LOG_ROOT))


def cmd_stats():
    """全局统计"""
    from skill_logger import SkillLogger
    
    logger = SkillLogger()
    stats = logger.get_stats()
    
    # 回归测试
    reg_files = list((LOG_ROOT / "regression_tests").glob("*__regression.jsonl"))
    
    # 边界
    boundary_files = list((LOG_ROOT / "boundaries").glob("*.boundary.json"))
    
    # A/B 测试
    ab_configs = list((LOG_ROOT / "ab_tests").glob("*__config.json"))
    
    print(json.dumps({
        "invocations": {
            "总调用记录": stats["total_invocations"],
            "调用文件数": stats["invocation_files"],
        },
        "fail_cases": {
            "失败案例文件": stats["fail_case_files"],
        },
        "regression": {
            "回归测试文件": stats["regression_files"],
            "Skills": [f.stem.split("__")[0] for f in reg_files],
        },
        "boundaries": {
            "边界签名文件": len(boundary_files),
            "Skills": [f.stem.replace(".boundary", "") for f in boundary_files],
        },
        "ab_tests": {
            "测试配置": len(ab_configs),
        },
        "log_root": str(LOG_ROOT),
    }, indent=2, ensure_ascii=False))


def cmd_scan(skill: str):
    """Phase 3: 被动扫描边界"""
    from boundary_detector import BoundaryDetector
    
    detector = BoundaryDetector()
    result = detector.passive_scan(skill)
    
    if "error" in result:
        print(f"错误: {result['error']}")
        return
    
    filepath = detector.save_boundary(skill, result)
    print(f"扫描完成: {filepath}")
    print(f"\n{detector.get_boundary_summary(skill)}")


def cmd_probe(skill: str, dry_run: bool = True):
    """Phase 3: 主动探测"""
    from boundary_detector import BoundaryDetector
    
    detector = BoundaryDetector()
    
    def mock_executor(skill: str, query: str):
        import time, random
        time.sleep(0.05)
        if len(query) > 5000:
            return {"success": False, "error": "too long"}
        if not query:
            return {"success": False, "error": "empty"}
        return {"success": random.random() > 0.3, "output": "ok"}
    
    results = detector.run_adversarial_probe(skill, mock_executor, dry_run)
    
    print(json.dumps({
        "探测完成": f"{results['passed']}/{results['total_cases']} 通过",
        "skipped": results['total_cases'] if dry_run else 0,
    }, indent=2))


def cmd_check(skill: str, query: str):
    """Phase 3: 风险检查"""
    from boundary_detector import BoundaryDetector
    
    detector = BoundaryDetector()
    result = detector.check_risk(skill, query)
    
    print(f"风险等级: {result['risk_level'].upper()}")
    
    if result.get("risk_reasons"):
        print("\n风险原因:")
        for r in result["risk_reasons"]:
            print(f"  - {r}")
    
    if result.get("suggestions"):
        print("\n建议:")
        for s in result["suggestions"]:
            print(f"  - {s}")
    
    if result.get("alternative_skill"):
        print(f"\n替代方案: {result['alternative_skill']}")


def cmd_full_loop(skill: str):
    """完整闭环检查"""
    print(f"\n{'='*50}")
    print(f"Skills Feedback Loop 完整闭环: {skill}")
    print(f"{'='*50}\n")
    
    from skill_logger import SkillLogger
    from regression_generator import RegressionGenerator
    from boundary_detector import BoundaryDetector
    
    # Step 1: 调用统计
    logger = SkillLogger()
    stats = logger.get_stats()
    print(f"[1/5] 调用统计: {stats['total_invocations']} 条记录")
    
    # Step 2: 失败案例
    failures = logger.query_failures(skill_name=skill, limit=50)
    print(f"[2/5] 失败案例: {len(failures)} 条")
    
    # Step 3: 回归测试
    gen = RegressionGenerator()
    if failures:
        tests = gen.generate_regression_tests(skill, failures)
        filepath = gen.save_regression_tests(skill, tests)
        print(f"[3/5] 回归测试: {len(tests)} 条 -> {filepath.name}")
    else:
        print(f"[3/5] 回归测试: 无失败案例，跳过")
    
    # Step 4: 边界扫描
    detector = BoundaryDetector()
    boundary = detector.passive_scan(skill)
    if "error" not in boundary:
        detector.save_boundary(skill, boundary)
        print(f"[4/5] 边界签名: 已更新 (失败率 {boundary.get('failure_rate', 0):.1%})")
    else:
        print(f"[4/5] 边界签名: {boundary.get('error')}")
    
    # Step 5: 风险检查
    boundary_data = detector.load_boundary(skill)
    if boundary_data:
        print(f"[5/5] 风险检查:")
        sample_queries = [
            "帮我写代码",
            "分析这段很长的代码，解释每一行的作用，并指出可能的性能问题和改进方案，总字数超过一万字",
        ]
        for q in sample_queries[:1]:
            result = detector.check_risk(skill, q)
            print(f"    query长度={len(q)}: {result['risk_level'].upper()}")
    else:
        print(f"[5/5] 风险检查: 无边界数据")


def main():
    parser = argparse.ArgumentParser(
        description="Skills Feedback Loop CLI - 三阶段合一",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --stats                        # 全局统计
  %(prog)s --scan coding-agent            # Phase 3: 扫描边界
  %(prog)s --probe coding-agent           # Phase 3: 主动探测
  %(prog)s --check coding-agent "query"   # Phase 3: 风险检查
  %(prog)s --full-loop coding-agent       # 完整闭环
        """
    )
    
    parser.add_argument("--stats", action="store_true", help="全局统计")
    parser.add_argument("--scan", type=str, default=None, help="扫描 Skill 边界 (Phase 3)")
    parser.add_argument("--probe", type=str, default=None, help="主动探测边界 (Phase 3)")
    parser.add_argument("--check", type=str, default=None, help="检查风险 (需要 --query)")
    parser.add_argument("--full-loop", type=str, default=None, help="完整闭环")
    parser.add_argument("--query", type=str, default=None, help="查询内容 (用于 --check)")
    parser.add_argument("--dry-run", action="store_true", default=True)
    
    args = parser.parse_args()
    
    if args.stats:
        cmd_stats()
    elif args.scan:
        cmd_scan(args.scan)
    elif args.probe:
        cmd_probe(args.probe, args.dry_run)
    elif args.check:
        if not args.query:
            print("--check 需要 --query")
            return
        cmd_check(args.check, args.query)
    elif args.full_loop:
        cmd_full_loop(args.full_loop)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
