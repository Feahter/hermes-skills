#!/usr/bin/env python3
"""
Regression Test Generator - Phase 2
从失败案例自动生成回归测试

功能：
1. 扫描 fail_cases/ 目录
2. 按 Skill 聚合失败案例
3. 生成回归测试 JSONL
4. 定期运行回归测试，验证修复
"""

import json
import argparse
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

LOG_ROOT = Path.home() / ".hermes" / "skills" / ".experiment_log"
FAIL_DIR = LOG_ROOT / "fail_cases"
REGRESSION_DIR = LOG_ROOT / "regression_tests"
INVOCATION_DIR = LOG_ROOT / "invocations"


class RegressionGenerator:
    """回归测试生成器"""
    
    def __init__(self):
        REGRESSION_DIR.mkdir(parents=True, exist_ok=True)
    
    def scan_failures(self, skill_name: Optional[str] = None) -> List[Dict]:
        """扫描失败案例"""
        failures = []
        
        for fail_file in sorted(FAIL_DIR.glob("*.jsonl")):
            # 按 Skill 过滤
            file_skill = fail_file.stem.split("__")[0]
            if skill_name and file_skill != skill_name:
                continue
            
            with open(fail_file, encoding="utf-8") as f:
                for line in f:
                    record = json.loads(line)
                    if skill_name is None or record.get("failed_skill") == skill_name:
                        failures.append(record)
        
        return failures
    
    def extract_patterns(self, failures: List[Dict]) -> Dict[str, List[Dict]]:
        """从失败案例中提取模式"""
        patterns = defaultdict(list)
        
        for f in failures:
            query = f.get("original_query", "")
            reason = f.get("failure_reason", "unknown")
            
            # 提取简单模式：关键词 + 失败原因
            pattern_key = self._extract_pattern_key(query, reason)
            patterns[pattern_key].append(f)
        
        return dict(patterns)
    
    def _extract_pattern_key(self, query: str, reason: str) -> str:
        """提取模式 key"""
        # 简化：用 reason + query 长度桶作为 key
        query_bucket = len(query) // 100 * 100
        return f"{reason}:{query_bucket}"
    
    def generate_regression_tests(
        self,
        skill_name: str,
        failures: List[Dict],
        min_occurrences: int = 2,
    ) -> List[Dict]:
        """
        生成回归测试用例
        
        去重 + 优先级排序：
        1. 高频失败模式优先
        2. 保留原始 query 供人工验证
        """
        # 按失败原因聚合
        by_reason = defaultdict(list)
        for f in failures:
            reason = f.get("failure_reason", "unknown")
            by_reason[reason].append(f)
        
        tests = []
        for reason, cases in by_reason.items():
            if len(cases) < min_occurrences and reason != "unknown":
                # 单次失败也保留，但标记为 low confidence
                for c in cases:
                    tests.append({
                        "type": "regression",
                        "skill": skill_name,
                        "query": c.get("original_query"),
                        "expected_behavior": "should_handle_gracefully",
                        "failure_mode": reason,
                        "confidence": "low",
                        "source_case_id": c.get("case_id"),
                        "generated_at": datetime.now().isoformat(),
                    })
            else:
                # 高频失败，取最有代表性的 case
                # 优先选择：中等长度 query、有具体错误信息的
                best = min(cases, key=lambda x: (
                    abs(len(x.get("original_query", "")) - 200),  # 接近 200 字
                    x.get("failure_reason", "") != "unknown"  # 有具体原因优先
                ))
                tests.append({
                    "type": "regression",
                    "skill": skill_name,
                    "query": best.get("original_query"),
                    "expected_behavior": "should_handle_gracefully",
                    "failure_mode": reason,
                    "confidence": "high" if len(cases) >= min_occurrences else "medium",
                    "occurrences": len(cases),
                    "sample_cases": [c.get("case_id") for c in cases[:3]],
                    "generated_at": datetime.now().isoformat(),
                })
        
        # 按 confidence 排序
        tests.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["confidence"]])
        return tests
    
    def save_regression_tests(
        self,
        skill_name: str,
        tests: List[Dict],
        version: str = "auto",
    ):
        """保存回归测试到文件"""
        filename = f"{skill_name}__{version}__regression.jsonl"
        filepath = REGRESSION_DIR / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            for test in tests:
                f.write(json.dumps(test, ensure_ascii=False) + "\n")
        
        return filepath
    
    def run_regression_tests(
        self,
        skill_name: str,
        version: str = "auto",
        dry_run: bool = False,
    ) -> Dict:
        """
        运行回归测试
        
        对于每个测试用例：
        1. 调用 Skill
        2. 检查是否仍然失败
        3. 记录结果
        
        注意：实际执行需要调用 LLM，这里只是框架
        """
        filepath = REGRESSION_DIR / f"{skill_name}__{version}__regression.jsonl"
        if not filepath.exists():
            return {"error": f"回归测试文件不存在: {filepath}"}
        
        results = {
            "skill": skill_name,
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "details": [],
        }
        
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                test = json.loads(line)
                results["tests_run"] += 1
                
                if dry_run:
                    results["details"].append({
                        "query": test["query"][:50] + "...",
                        "status": "skipped (dry-run)",
                        "confidence": test["confidence"],
                    })
                    continue
                
                # TODO: 实际调用 Skill 执行测试
                # 目前只是框架占位
                results["details"].append({
                    "query": test["query"][:50] + "...",
                    "status": "not_implemented",
                    "confidence": test["confidence"],
                })
        
        results["tests_passed"] = sum(
            1 for d in results["details"] if d["status"] == "passed"
        )
        results["tests_failed"] = results["tests_run"] - results["tests_passed"]
        
        return results
    
    def get_regression_status(self, skill_name: str) -> Dict:
        """获取某 Skill 的回归测试状态"""
        files = list(REGRESSION_DIR.glob(f"{skill_name}__*__regression.jsonl"))
        
        status = {
            "skill": skill_name,
            "regression_files": [],
            "total_tests": 0,
            "by_version": {},
        }
        
        for f in files:
            version = f.stem.split("__")[1]
            tests = []
            with open(f, encoding="utf-8") as fp:
                for line in fp:
                    tests.append(json.loads(line))
            
            confidence_counts = defaultdict(int)
            for t in tests:
                confidence_counts[t.get("confidence", "unknown")] += 1
            
            status["regression_files"].append({
                "file": f.name,
                "version": version,
                "test_count": len(tests),
                "by_confidence": dict(confidence_counts),
            })
            status["total_tests"] += len(tests)
            status["by_version"][version] = len(tests)
        
        return status


def cmd_generate(skill: str, min_occurrences: int = 1):
    """生成回归测试"""
    gen = RegressionGenerator()
    
    failures = gen.scan_failures(skill_name=skill)
    print(f"找到 {len(failures)} 条失败案例")
    
    if not failures:
        print("没有失败案例，跳过")
        return
    
    tests = gen.generate_regression_tests(skill, failures, min_occurrences)
    print(f"生成了 {len(tests)} 条回归测试")
    
    filepath = gen.save_regression_tests(skill, tests)
    print(f"保存到: {filepath}")


def cmd_run(skill: str, version: str = "auto", dry_run: bool = True):
    """运行回归测试"""
    gen = RegressionGenerator()
    results = gen.run_regression_tests(skill, version, dry_run)
    
    print(json.dumps(results, indent=2, ensure_ascii=False))


def cmd_status(skill: str = None):
    """查看回归测试状态"""
    gen = RegressionGenerator()
    
    if skill:
        status = gen.get_regression_status(skill)
        print(json.dumps(status, indent=2, ensure_ascii=False))
    else:
        # 全局状态
        all_skills = set()
        for f in REGRESSION_DIR.glob("*__regression.jsonl"):
            skill_name = f.stem.split("__")[0]
            all_skills.add(skill_name)
        
        print(json.dumps({
            "total_skills_with_regression": len(all_skills),
            "skills": sorted(all_skills),
            "regression_dir": str(REGRESSION_DIR),
        }, indent=2, ensure_ascii=False))


def cmd_list(skill: str):
    """列出某 Skill 的所有回归测试"""
    gen = RegressionGenerator()
    status = gen.get_regression_status(skill)
    print(json.dumps(status, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Regression Test Generator")
    parser.add_argument("--generate", action="store_true", help="生成回归测试")
    parser.add_argument("--run", action="store_true", help="运行回归测试")
    parser.add_argument("--status", action="store_true", help="查看状态")
    parser.add_argument("--list", dest="list_tests", action="store_true", help="列出测试")
    parser.add_argument("--skill", type=str, default=None, help="Skill 名称")
    parser.add_argument("--version", type=str, default="auto", help="版本号")
    parser.add_argument("--min-occurrences", type=int, default=1, help="最小失败次数")
    parser.add_argument("--dry-run", action="store_true", default=True, help="dry-run 模式")
    
    args = parser.parse_args()
    
    if args.generate:
        if not args.skill:
            print("--skill 是必需的")
            return
        cmd_generate(args.skill, args.min_occurrences)
    elif args.run:
        if not args.skill:
            print("--skill 是必需的")
            return
        cmd_run(args.skill, args.version, args.dry_run)
    elif args.status:
        cmd_status(args.skill)
    elif args.list_tests:
        if not args.skill:
            print("--skill 是必需的")
            return
        cmd_list(args.skill)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
