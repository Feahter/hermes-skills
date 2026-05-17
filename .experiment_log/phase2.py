#!/usr/bin/env python3
"""
Phase 2 整合脚本
一键执行：失败案例 → 回归测试 → 验证闭环

用法:
    python3 phase2.py --generate-regression --skill coding-agent
    python3 phase2.py --run-regression --skill coding-agent
    python3 phase2.py --ab-test --skill-a coding-agent --skill-b claude-code
    python3 phase2.py --full-loop --skill coding-agent
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime

# 添加 experiment_log 到路径
LOG_ROOT = Path.home() / ".hermes" / "skills" / ".experiment_log"
sys.path.insert(0, str(LOG_ROOT))

from skill_logger import SkillLogger
from regression_generator import RegressionGenerator
from ab_tester import ABTester


def cmd_generate_regression(skill: str, min_occurrences: int = 1):
    """从失败案例生成回归测试"""
    logger = SkillLogger()
    gen = RegressionGenerator()
    
    # 获取失败案例
    failures = logger.query_failures(skill_name=skill, limit=100)
    print(f"找到 {len(failures)} 条失败案例")
    
    if not failures:
        print("没有失败案例，无法生成回归测试")
        print("提示：先积累一些失败案例，或者手动添加测试用例")
        return
    
    # 生成回归测试
    tests = gen.generate_regression_tests(skill, failures, min_occurrences)
    print(f"生成了 {len(tests)} 条回归测试")
    
    # 保存
    filepath = gen.save_regression_tests(skill, tests)
    print(f"保存到: {filepath}")
    
    # 显示摘要
    for t in tests[:5]:
        print(f"  [{t['confidence']}] {t['query'][:50]}... -> {t['failure_mode']}")


def cmd_run_regression(skill: str, version: str = "auto", dry_run: bool = True):
    """运行回归测试"""
    gen = RegressionGenerator()
    results = gen.run_regression_tests(skill, version, dry_run)
    
    if "error" in results:
        print(f"错误: {results['error']}")
        return
    
    print(f"\n=== 回归测试结果: {skill} @ {version} ===")
    print(f"运行: {results['tests_run']} | 通过: {results['tests_passed']} | 失败: {results['tests_failed']}")
    
    if results['details']:
        print("\n详情:")
        for d in results['details'][:10]:
            status_icon = "✓" if d['status'] == 'passed' else "✗" if d['status'] == 'failed' else "○"
            print(f"  {status_icon} {d.get('query', '?')} [{d.get('confidence', '?')}]")


def cmd_ab_test(skill_a: str, skill_b: str, queries: list = None):
    """运行 A/B 测试"""
    tester = ABTester()
    
    # 默认测试 queries
    if not queries:
        queries = [
            "帮我写一个快速排序",
            "分析这段代码的性能瓶颈",
            "帮我优化这个 SQL 查询",
            "翻译这段英文到中文",
            "总结这篇论文的主要内容",
        ]
    
    # 创建测试
    config = tester.create_test(
        test_name=f"{skill_a} vs {skill_b}",
        skill_a=skill_a,
        skill_b=skill_b,
        queries=queries,
    )
    
    print(f"创建 A/B 测试: {config.test_id}")
    print(f"  A: {skill_a}")
    print(f"  B: {skill_b}")
    print(f"  Queries: {len(queries)}")
    
    # 运行测试（使用 mock executor）
    def mock_executor(skill: str, query: str):
        import time, random
        time.sleep(0.05)
        return {
            "quality": random.uniform(0.6, 0.95),
            "latency_ms": random.randint(500, 2000),
            "tokens": random.randint(200, 800),
            "output": f"[{skill}] processed: {query[:20]}...",
        }
    
    results = tester.run_test(config.test_id, mock_executor, dry_run=True)
    summary = tester.get_test_summary(config.test_id)
    
    print(f"\n=== A/B 测试结果 ===")
    print(f"胜率: {skill_a} {summary['win_rate_a']:.1%} vs {skill_b} {summary['win_rate_b']:.1%}")
    print(f"平局: {summary['ties']}")
    print(f"推荐: {summary['recommendation'].upper()}")
    
    return summary


def cmd_full_loop(skill: str):
    """完整闭环：检查回归 → 生成测试 → 运行验证"""
    print(f"\n{'='*50}")
    print(f"Phase 2 完整闭环: {skill}")
    print(f"{'='*50}\n")
    
    # Step 1: 检查失败案例
    logger = SkillLogger()
    failures = logger.query_failures(skill_name=skill, limit=50)
    print(f"[1/4] 失败案例: {len(failures)} 条")
    
    # Step 2: 生成/更新回归测试
    gen = RegressionGenerator()
    if failures:
        tests = gen.generate_regression_tests(skill, failures)
        filepath = gen.save_regression_tests(skill, tests)
        print(f"[2/4] 回归测试: 生成了 {len(tests)} 条 -> {filepath.name}")
    else:
        print("[2/4] 回归测试: 无失败案例，跳过生成")
    
    # Step 3: 运行回归测试
    print(f"[3/4] 运行回归测试...")
    results = gen.run_regression_tests(skill, dry_run=True)
    passed = results.get('tests_passed', 0)
    failed = results.get('tests_failed', 0)
    print(f"         通过 {passed}, 失败 {failed}")
    
    # Step 4: 给出建议
    print(f"[4/4] 建议:")
    if failed > 0:
        print(f"         ⚠️  {failed} 条回归测试失败，建议运行 skill-evolution-manager")
    else:
        print(f"         ✅ 所有回归测试通过")
    
    # 检查是否有 skill-evolution-manager 经验
    evolution_file = Path.home() / ".hermes" / "skills" / skill / "evolution.json"
    if evolution_file.exists():
        with open(evolution_file) as f:
            evo = json.load(f)
            prefs = evo.get("preferences", [])
            fixes = evo.get("fixes", [])
            if prefs or fixes:
                print(f"\n         已积累 {len(prefs)} 条偏好, {len(fixes)} 条修复")


def cmd_status():
    """查看 Phase 2 整体状态"""
    logger = SkillLogger()
    stats = logger.get_stats()
    
    # 读取回归测试状态
    reg_gen = RegressionGenerator()
    
    # 获取所有有回归测试的 skills
    all_skills = set()
    for f in (LOG_ROOT / "regression_tests").glob("*__regression.jsonl"):
        skill = f.stem.split("__")[0]
        all_skills.add(skill)
    
    # 获取 A/B 测试
    ab_tester = ABTester()
    ab_tests = ab_tester.list_tests()
    
    print(json.dumps({
        "experiment_log": {
            "总调用记录": stats["total_invocations"],
            "失败案例文件": stats["fail_case_files"],
        },
        "regression": {
            "有回归测试的 Skills": sorted(all_skills),
            "回归测试文件": stats["regression_files"],
        },
        "ab_tests": {
            "测试数量": len(ab_tests),
            "最近测试": [t.get("test_id") for t in ab_tests[-3:]],
        },
    }, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Phase 2 - 回归测试 + A/B 测试")
    parser.add_argument("--generate-regression", action="store_true", help="从失败案例生成回归测试")
    parser.add_argument("--run-regression", action="store_true", help="运行回归测试")
    parser.add_argument("--ab-test", action="store_true", help="运行 A/B 测试")
    parser.add_argument("--full-loop", action="store_true", help="完整闭环检查")
    parser.add_argument("--status", action="store_true", help="查看状态")
    
    parser.add_argument("--skill", type=str, default=None, help="Skill 名称")
    parser.add_argument("--skill-a", type=str, default=None, help="Skill A (A/B 测试)")
    parser.add_argument("--skill-b", type=str, default=None, help="Skill B (A/B 测试)")
    parser.add_argument("--version", type=str, default="auto", help="版本号")
    parser.add_argument("--min-occurrences", type=int, default=1, help="最小失败次数")
    parser.add_argument("--dry-run", action="store_true", default=True, help="dry-run 模式")
    parser.add_argument("--queries", nargs="*", default=None, help="A/B 测试 queries")
    
    args = parser.parse_args()
    
    if args.status:
        cmd_status()
    elif args.generate_regression:
        if not args.skill:
            print("--skill 是必需的")
            return
        cmd_generate_regression(args.skill, args.min_occurrences)
    elif args.run_regression:
        if not args.skill:
            print("--skill 是必需的")
            return
        cmd_run_regression(args.skill, args.version, args.dry_run)
    elif args.ab_test:
        if not args.skill_a or not args.skill_b:
            print("--ab-test 需要 --skill-a 和 --skill-b")
            return
        cmd_ab_test(args.skill_a, args.skill_b, args.queries)
    elif args.full_loop:
        if not args.skill:
            print("--full-loop 需要 --skill")
            return
        cmd_full_loop(args.skill)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
