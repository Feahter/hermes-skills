#!/usr/bin/env python3
"""
A/B Tester - Phase 2
对比两个 Skill 或版本的性能

功能：
1. 同一 query 同时/轮流跑两个 Skill
2. 比较输出质量/效率
3. 记录结果，自动选出胜者
"""

import json
import argparse
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
import random

LOG_ROOT = Path.home() / ".hermes" / "skills" / ".experiment_log"
AB_DIR = LOG_ROOT / "ab_tests"


@dataclass
class ABTestConfig:
    """A/B 测试配置"""
    test_id: str
    test_name: str
    skill_a: str
    skill_b: str
    queries: List[str]
    version_a: str = "v1"
    version_b: str = "v2"
    metric: str = "quality"  # quality | latency | tokens
    mode: str = "parallel"  # parallel | sequential | random
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class ABTestResult:
    """A/B 测试单次结果"""
    test_id: str
    query: str
    query_hash: str
    skill_a_result: Optional[Dict]
    skill_b_result: Optional[Dict]
    winner: str  # "a" | "b" | "tie" | "error"
    winner_score: float
    loser_score: float
    score_diff: float
    run_at: str


class ABTester:
    """A/B 测试器"""
    
    def __init__(self):
        AB_DIR.mkdir(parents=True, exist_ok=True)
    
    def create_test(
        self,
        test_name: str,
        skill_a: str,
        skill_b: str,
        queries: List[str],
        version_a: str = "v1",
        version_b: str = "v2",
        metric: str = "quality",
        mode: str = "parallel",
    ) -> ABTestConfig:
        """创建 A/B 测试"""
        test_id = str(uuid.uuid4())[:8]
        
        config = ABTestConfig(
            test_id=test_id,
            test_name=test_name,
            skill_a=skill_a,
            skill_b=skill_b,
            version_a=version_a,
            version_b=version_b,
            queries=queries,
            metric=metric,
            mode=mode,
        )
        
        # 保存配置
        config_file = AB_DIR / f"{test_id}__config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(asdict(config), f, ensure_ascii=False, indent=2)
        
        return config
    
    def run_test(
        self,
        test_id: str,
        executor: Callable[[str, str], Dict],
        dry_run: bool = False,
    ) -> List[ABTestResult]:
        """
        运行 A/B 测试
        
        executor: 函数(skill_name, query) -> {"quality": float, "latency_ms": float, "tokens": int, "output": str}
        """
        config_file = AB_DIR / f"{test_id}__config.json"
        if not config_file.exists():
            raise FileNotFoundError(f"测试配置不存在: {test_id}")
        
        with open(config_file, encoding="utf-8") as f:
            config_dict = json.load(f)
        config = ABTestConfig(**config_dict)
        
        results = []
        
        for query in config.queries:
            query_hash = hashlib.md5(query.encode()).hexdigest()[:12]
            
            if dry_run:
                # 模拟结果
                result = ABTestResult(
                    test_id=test_id,
                    query=query[:50] + "...",
                    query_hash=query_hash,
                    skill_a_result={"quality": 0.8, "latency_ms": 1000},
                    skill_b_result={"quality": 0.7, "latency_ms": 800},
                    winner="a",
                    winner_score=0.8,
                    loser_score=0.7,
                    score_diff=0.1,
                    run_at=datetime.now().isoformat(),
                )
                results.append(result)
                continue
            
            # 实际执行
            try:
                a_result = executor(config.skill_a, query)
                b_result = executor(config.skill_b, query)
            except Exception as e:
                # 执行失败
                result = ABTestResult(
                    test_id=test_id,
                    query=query[:50] + "...",
                    query_hash=query_hash,
                    skill_a_result={"error": str(e)},
                    skill_b_result={"error": str(e)},
                    winner="error",
                    winner_score=0,
                    loser_score=0,
                    score_diff=0,
                    run_at=datetime.now().isoformat(),
                )
                results.append(result)
                continue
            
            # 计算分数
            if config.metric == "quality":
                a_score = a_result.get("quality", 0)
                b_score = b_result.get("quality", 0)
            elif config.metric == "latency":
                # latency 越小越好
                a_score = 1.0 / (a_result.get("latency_ms", 1) + 1)
                b_score = 1.0 / (b_result.get("latency_ms", 1) + 1)
            elif config.metric == "tokens":
                # tokens 越少越好
                a_score = 1.0 / (a_result.get("tokens", 1) + 1)
                b_score = 1.0 / (b_result.get("tokens", 1) + 1)
            else:
                a_score = a_result.get(config.metric, 0)
                b_score = b_result.get(config.metric, 0)
            
            # 判断胜者
            if abs(a_score - b_score) < 0.01:
                winner = "tie"
            elif a_score > b_score:
                winner = "a"
            else:
                winner = "b"
            
            result = ABTestResult(
                test_id=test_id,
                query=query,
                query_hash=query_hash,
                skill_a_result=a_result,
                skill_b_result=b_result,
                winner=winner,
                winner_score=max(a_score, b_score),
                loser_score=min(a_score, b_score),
                score_diff=abs(a_score - b_score),
                run_at=datetime.now().isoformat(),
            )
            results.append(result)
        
        # 保存结果
        results_file = AB_DIR / f"{test_id}__results.jsonl"
        with open(results_file, "w", encoding="utf-8") as f:
            for r in results:
                f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")
        
        return results
    
    def get_test_summary(self, test_id: str) -> Dict:
        """获取测试摘要"""
        config_file = AB_DIR / f"{test_id}__config.json"
        results_file = AB_DIR / f"{test_id}__results.jsonl"
        
        if not config_file.exists():
            return {"error": f"测试不存在: {test_id}"}
        
        with open(config_file, encoding="utf-8") as f:
            config = json.load(f)
        
        results = []
        if results_file.exists():
            with open(results_file, encoding="utf-8") as f:
                for line in f:
                    results.append(json.loads(line))
        
        # 统计
        wins_a = sum(1 for r in results if r["winner"] == "a")
        wins_b = sum(1 for r in results if r["winner"] == "b")
        ties = sum(1 for r in results if r["winner"] == "tie")
        
        avg_score_diff = sum(r["score_diff"] for r in results) / len(results) if results else 0
        
        return {
            "test_id": test_id,
            "test_name": config.get("test_name"),
            "skill_a": config.get("skill_a"),
            "skill_b": config.get("skill_b"),
            "total_queries": len(config.get("queries", [])),
            "results_count": len(results),
            "wins_a": wins_a,
            "wins_b": wins_b,
            "ties": ties,
            "win_rate_a": wins_a / len(results) if results else 0,
            "win_rate_b": wins_b / len(results) if results else 0,
            "avg_score_diff": avg_score_diff,
            "recommendation": "a" if wins_a > wins_b else ("b" if wins_b > wins_a else "tie"),
        }
    
    def list_tests(self) -> List[Dict]:
        """列出所有测试"""
        tests = []
        for config_file in sorted(AB_DIR.glob("*__config.json")):
            test_id = config_file.stem.replace("__config", "")
            summary = self.get_test_summary(test_id)
            tests.append(summary)
        return tests
    
    def delete_test(self, test_id: str):
        """删除测试"""
        for f in AB_DIR.glob(f"{test_id}__*"):
            f.unlink()


# 便捷函数

def quick_ab_test(
    skill_a: str,
    skill_b: str,
    queries: List[str],
    executor: Callable[[str, str], Dict],
) -> Dict:
    """快速 A/B 测试"""
    tester = ABTester()
    
    # 创建测试
    test_name = f"{skill_a} vs {skill_b}"
    config = tester.create_test(
        test_name=test_name,
        skill_a=skill_a,
        skill_b=skill_b,
        queries=queries,
    )
    
    # 运行测试
    results = tester.run_test(config.test_id, executor)
    
    # 返回摘要
    return tester.get_test_summary(config.test_id)


# CLI 命令

def cmd_create(args):
    """创建测试"""
    tester = ABTester()
    
    queries = []
    if args.queries_file:
        with open(args.queries_file, encoding="utf-8") as f:
            queries = [line.strip() for line in f if line.strip()]
    elif args.queries:
        queries = args.queries
    
    config = tester.create_test(
        test_name=args.name,
        skill_a=args.skill_a,
        skill_b=args.skill_b,
        queries=queries,
        version_a=args.version_a,
        version_b=args.version_b,
        metric=args.metric,
        mode=args.mode,
    )
    
    print(f"创建测试: {config.test_id}")
    print(f"保存配置: {AB_DIR / f'{config.test_id}__config.json'}")


def cmd_run(args):
    """运行测试"""
    tester = ABTester()
    
    def mock_executor(skill: str, query: str) -> Dict:
        """模拟执行器 - 实际使用时替换为真的"""
        import time, random
        time.sleep(0.1)
        return {
            "quality": random.uniform(0.5, 1.0),
            "latency_ms": random.randint(500, 2000),
            "tokens": random.randint(100, 1000),
            "output": f"[{skill}] {query[:30]}...",
        }
    
    results = tester.run_test(args.test_id, mock_executor, dry_run=args.dry_run)
    
    summary = tester.get_test_summary(args.test_id)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def cmd_list():
    """列出测试"""
    tester = ABTester()
    tests = tester.list_tests()
    print(json.dumps(tests, indent=2, ensure_ascii=False))


def cmd_summary(test_id: str):
    """查看测试摘要"""
    tester = ABTester()
    summary = tester.get_test_summary(test_id)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def cmd_delete(test_id: str):
    """删除测试"""
    tester = ABTester()
    tester.delete_test(test_id)
    print(f"已删除测试: {test_id}")


def main():
    parser = argparse.ArgumentParser(description="A/B Tester")
    parser.add_argument("--create", action="store_true", help="创建测试")
    parser.add_argument("--run", action="store_true", help="运行测试")
    parser.add_argument("--list", action="store_true", help="列出测试")
    parser.add_argument("--summary", type=str, help="查看测试摘要")
    parser.add_argument("--delete", type=str, help="删除测试")
    
    # 创建参数
    parser.add_argument("--name", type=str, default=None, help="测试名称")
    parser.add_argument("--skill-a", type=str, default=None, help="Skill A")
    parser.add_argument("--skill-b", type=str, default=None, help="Skill B")
    parser.add_argument("--version-a", type=str, default="v1", help="Version A")
    parser.add_argument("--version-b", type=str, default="v2", help="Version B")
    parser.add_argument("--queries", nargs="*", default=None, help="查询列表")
    parser.add_argument("--queries-file", type=str, default=None, help="查询文件")
    parser.add_argument("--metric", type=str, default="quality", choices=["quality", "latency", "tokens"])
    parser.add_argument("--mode", type=str, default="parallel", choices=["parallel", "sequential", "random"])
    
    # 运行参数
    parser.add_argument("--test-id", type=str, default=None, help="测试 ID")
    parser.add_argument("--dry-run", action="store_true", default=False, help="dry-run 模式")
    
    args = parser.parse_args()
    
    if args.create:
        if not args.name or not args.skill_a or not args.skill_b:
            print("--create 需要 --name, --skill-a, --skill-b")
            return
        cmd_create(args)
    elif args.run:
        if not args.test_id:
            print("--run 需要 --test-id")
            return
        cmd_run(args)
    elif args.list:
        cmd_list()
    elif args.summary:
        cmd_summary(args.summary)
    elif args.delete:
        cmd_delete(args.delete)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
