#!/usr/bin/env python3
"""
Skill Experiment Logger - Phase 1
记录 Skill 调用的输入/输出/质量信号

用法:
    from skill_logger import SkillLogger
    logger = SkillLogger()
    logger.log_invocation_start(skill_name, query, context)
    # ... 执行 skill ...
    logger.log_invocation_end(invocation_id, success=True, quality_signals={})
"""

import json
import re
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# 存储根目录
LOG_ROOT = Path.home() / ".hermes" / "skills" / ".experiment_log"
INVOCATION_DIR = LOG_ROOT / "invocations"
FAIL_DIR = LOG_ROOT / "fail_cases"
REGRESSION_DIR = LOG_ROOT / "regression_tests"
AB_DIR = LOG_ROOT / "ab_tests"

# 确保目录存在
INVOCATION_DIR.mkdir(parents=True, exist_ok=True)
FAIL_DIR.mkdir(parents=True, exist_ok=True)
REGRESSION_DIR.mkdir(parents=True, exist_ok=True)
AB_DIR.mkdir(parents=True, exist_ok=True)


class SkillLogger:
    """Skill 调用日志记录器"""
    
    def __init__(self):
        self.current_invocation: Optional[Dict] = None
    
    @staticmethod
    def _hash_query(query: str) -> str:
        """对 query 去重哈希"""
        return hashlib.md5(query.encode()).hexdigest()[:12]
    
    @staticmethod
    def _now() -> str:
        return datetime.now().isoformat()
    
    def log_invocation_start(
        self,
        skill_name: str,
        query: str,
        context_snapshot: Optional[str] = None,
        user_id: Optional[str] = None,
        channel: Optional[str] = None,
        # Plan A 新增：selection context（skill-combinator 注入）
        skill_combinator_candidates: Optional[list[dict]] = None,
        skill_combinator_top_score: Optional[float] = None,
    ) -> str:
        """
        记录一次 Skill 调用的开始
        
        Args:
            skill_combinator_candidates: discover 阶段返回的候选列表
                [{"name": "skill-a", "score": 8.5}, {"name": "skill-b", "score": 6.2}]
            skill_combinator_top_score: 选中 skill 的 combinator 得分
        """
        invocation_id = str(uuid.uuid4())
        
        record = {
            "invocation_id": invocation_id,
            "timestamp": self._now(),
            "query_hash": self._hash_query(query),
            "user_id": user_id,
            "channel": channel,
            "skill_selected": skill_name,
            "input": {
                "query": query,
                "context_snapshot": context_snapshot[:500] if context_snapshot else None,
            },
            "output": None,
            "quality": {
                "explicit_rating": None,
                "implicit_signal": None,
                "followup_same_skill": None,
                "followup_refined": None,
            },
            # Plan A 新增：selection context
            "skill_combinator": {
                "candidates": skill_combinator_candidates,
                "top_score": skill_combinator_top_score,
                "was_correct": None,        # 事后由 skill_combinator 回填
                "selection_error": None,    # "wrong_skill" | "timeout" | None
            },
            "error": None,
        }
        
        self.current_invocation = record
        self._write_invocation(record)
        return invocation_id
    
    def log_invocation_end(
        self,
        invocation_id: str,
        success: bool = True,
        output: Optional[Dict] = None,
        error: Optional[str] = None,
        quality_signals: Optional[Dict] = None,
        skill_version: Optional[str] = None,
    ):
        """
        记录一次 Skill 调用的结束
        
        Args:
            invocation_id: log_invocation_start 返回的 ID
            success: 是否成功完成
            output: 输出信息 (result, tool_calls, latency_ms, tokens_used)
            error: 错误信息
            quality_signals: 质量信号 (followup_same_skill, followup_refined 等)
            skill_version: Skill 版本
        """
        if self.current_invocation is None:
            # 如果没有 start 记录，创建一个基本的
            record = {
                "invocation_id": invocation_id,
                "timestamp": self._now(),
                "query_hash": invocation_id,
                "output": {},
                "error": error,
            }
            self._write_invocation(record)
            return
        
        record = self.current_invocation
        record["timestamp_end"] = self._now()
        
        if output:
            record["output"] = {
                "result": output.get("result", "")[:1000] if output.get("result") else None,
                "tool_calls": output.get("tool_calls", []),
                "latency_ms": output.get("latency_ms"),
                "tokens_used": output.get("tokens_used"),
            }
        
        if error:
            record["error"] = error
            record["quality"]["implicit_signal"] = "error"
        elif success:
            record["quality"]["implicit_signal"] = "success"
        else:
            record["quality"]["implicit_signal"] = "unknown"
        
        if quality_signals:
            record["quality"].update(quality_signals)
        
        if skill_version:
            record["skill_version"] = skill_version
        
        # 覆写完整记录
        self._write_invocation(record, append=False)
        
        # 如果是失败案例，写入 fail_cases
        if error or not success:
            self._write_fail_case(record)
        
        self.current_invocation = None
    
    def log_invocation_update(
        self,
        invocation_id: str,
        implicit_signal: Optional[str] = None,
        followup_same_skill: Optional[bool] = None,
        followup_refined: Optional[bool] = None,
    ):
        """后续更新质量信号（用户反馈后调用）"""
        # 读取最新记录，追加 quality 信息
        log_file = INVOCATION_DIR / f"{invocation_id[:8]}.jsonl"
        # 简化处理：写入一条带 timestamp 的 quality 更新
        update_record = {
            "type": "quality_update",
            "invocation_id": invocation_id,
            "timestamp": self._now(),
            "quality": {
                "implicit_signal": implicit_signal,
                "followup_same_skill": followup_same_skill,
                "followup_refined": followup_refined,
            }
        }
        self._write_invocation(update_record, append=True)
    
    def _write_invocation(self, record: Dict, append: bool = True):
        """写入调用记录"""
        # 用 invocation_id 前8字符命名文件，便于查找
        file_id = record.get("invocation_id", "unknown")[:8]
        log_file = INVOCATION_DIR / f"{file_id}.jsonl"
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    def _write_fail_case(self, record: Dict):
        """写入失败案例"""
        skill = record.get("skill_selected", "unknown")
        date = datetime.now().strftime("%Y-%m-%d")
        fail_file = FAIL_DIR / f"{skill}__{date}.jsonl"
        
        # 提取关键信息
        fail_record = {
            "case_id": record.get("invocation_id"),
            "timestamp": record.get("timestamp"),
            "original_query": record.get("input", {}).get("query"),
            "failed_skill": skill,
            "failure_reason": record.get("error") or "unknown",
            "skill_version": record.get("skill_version"),
        }
        
        with open(fail_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(fail_record, ensure_ascii=False) + "\n")
    
    def log_regression_test(
        self,
        skill_name: str,
        skill_version: str,
        test_cases: list,
    ):
        """写入回归测试"""
        reg_file = REGRESSION_DIR / f"{skill_name}__{skill_version}__regression.jsonl"
        
        with open(reg_file, "w", encoding="utf-8") as f:
            for case in test_cases:
                f.write(json.dumps(case, ensure_ascii=False) + "\n")
    
    def log_ab_test(
        self,
        test_id: str,
        query: str,
        skill_a: str,
        skill_b: str,
        result_a: Dict,
        result_b: Dict,
    ):
        """记录 A/B 测试"""
        ab_record = {
            "test_id": test_id,
            "timestamp": self._now(),
            "query": query,
            "skill_a": {"name": skill_a, **result_a},
            "skill_b": {"name": skill_b, **result_b},
            "winner": result_a.get("score", 0) > result_b.get("score", 0) and "a" or "b",
        }
        
        ab_file = AB_DIR / f"{test_id[:8]}.jsonl"
        with open(ab_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(ab_record, ensure_ascii=False) + "\n")
    
    def query_invocations(
        self,
        skill_name: Optional[str] = None,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list:
        """查询调用记录"""
        results = []
        for log_file in sorted(INVOCATION_DIR.glob("*.jsonl"), reverse=True):
            with open(log_file, encoding="utf-8") as f:
                for line in f:
                    record = json.loads(line)
                    if skill_name and record.get("skill_selected") != skill_name:
                        continue
                    results.append(record)
                    if len(results) >= limit:
                        return results
        return results
    
    def query_failures(self, skill_name: Optional[str] = None, limit: int = 20) -> list:
        """查询失败案例"""
        results = []
        for fail_file in sorted(FAIL_DIR.glob("*.jsonl"), reverse=True):
            with open(fail_file, encoding="utf-8") as f:
                for line in f:
                    record = json.loads(line)
                    if skill_name and record.get("failed_skill") != skill_name:
                        continue
                    results.append(record)
                    if len(results) >= limit:
                        return results
        return results
    
    def get_real_invocation_stats(self, min_samples: int = 1) -> dict:
        """
        Plan A: 消费真实调用数据，生成 per-skill 统计
        skill-combinator 的 stage1_search_index() 在 scoring 后调用此方法，
        用真实成功率对候选做加权调整。

        Returns:
            {
                "skill_name": {
                    "total": N, "success": N, "partial": N, "fail": N,
                    "success_rate": 0.0-1.0,
                    "avg_latency_ms": float,
                    "query_keywords": {"kw1": count, ...},
                    "was_correct_avg": 0.0-1.0,  # 回填后才有意义
                }
            }
        """
        from collections import defaultdict
        import statistics

        stats: dict = defaultdict(lambda: {
            "total": 0, "success": 0, "partial": 0, "fail": 0,
            "latencies": [], "query_keywords": defaultdict(int),
            "was_correct_count": 0, "was_correct_total": 0,
        })

        for log_file in INVOCATION_DIR.glob("*.jsonl"):
            with open(log_file, encoding="utf-8") as f:
                for line in f:
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    # 跳过 quality_update 类型的追加记录
                    if record.get("type") == "quality_update":
                        continue
                    skill = record.get("skill_selected")
                    if not skill:
                        continue
                    s = stats[skill]
                    s["total"] += 1

                    implicit = record.get("quality", {}).get("implicit_signal")
                    if implicit == "success":
                        s["success"] += 1
                    elif implicit == "partial":
                        s["partial"] += 1
                    elif implicit in ("error", "fail"):
                        s["fail"] += 1

                    latency = (record.get("output") or {}).get("latency_ms")
                    if latency:
                        s["latencies"].append(latency)

                    # 记录 query 关键词（用于匹配增强）
                    query_words = re.findall(r'[\w]+', (record.get("input") or {}).get("query", "").lower())
                    for w in query_words:
                        if len(w) > 2:
                            s["query_keywords"][w] += 1

                    # 回填的 was_correct
                    sc = (record.get("skill_combinator") or {})
                    if sc.get("was_correct") is not None:
                        s["was_correct_total"] += 1
                        if sc["was_correct"]:
                            s["was_correct_count"] += 1

        # 汇总
        result = {}
        for skill, s in stats.items():
            if s["total"] < min_samples:
                continue
            result[skill] = {
                "total": s["total"],
                "success": s["success"],
                "partial": s["partial"],
                "fail": s["fail"],
                "success_rate": s["success"] / s["total"] if s["total"] else 0,
                "avg_latency_ms": statistics.mean(s["latencies"]) if s["latencies"] else None,
                "top_query_keywords": dict(sorted(s["query_keywords"].items(), key=lambda x: -x[1])[:20]),
                "was_correct_rate": s["was_correct_count"] / s["was_correct_total"] if s["was_correct_total"] else None,
            }
        return result

    def get_skill_cooccurrence(self) -> dict:
        """
        返回 {skill_name: [co_occurring_skill_names]}
        基于真实调用的 query_hash 聚类，同一 query 的连续调用视为协作链。
        """
        from collections import defaultdict
        hash_skills: dict = defaultdict(list)
        for log_file in INVOCATION_DIR.glob("*.jsonl"):
            with open(log_file, encoding="utf-8") as f:
                for line in f:
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if record.get("type") == "quality_update":
                        continue
                    qhash = record.get("query_hash")
                    skill = record.get("skill_selected")
                    if qhash and skill:
                        hash_skills[qhash].append(skill)

        cooccur: dict = defaultdict(set)
        for skills in hash_skills.values():
            if len(skills) > 1:
                for s in skills:
                    for t in skills:
                        if s != t:
                            cooccur[s].add(t)
        return {k: list(v) for k, v in cooccur.items()}

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        inv_count = len(list(INVOCATION_DIR.glob("*.jsonl")))
        fail_count = len(list(FAIL_DIR.glob("*.jsonl")))
        reg_count = len(list(REGRESSION_DIR.glob("*.jsonl")))
        
        # 计算总记录数（每行一条）
        total_invocations = 0
        for f in INVOCATION_DIR.glob("*.jsonl"):
            with open(f) as fp:
                total_invocations += sum(1 for _ in fp)
        
        return {
            "invocation_files": inv_count,
            "total_invocations": total_invocations,
            "fail_case_files": fail_count,
            "regression_files": reg_count,
            "log_root": str(LOG_ROOT),
        }


# 便捷函数
_logger: Optional[SkillLogger] = None

def get_logger() -> SkillLogger:
    global _logger
    if _logger is None:
        _logger = SkillLogger()
    return _logger


if __name__ == "__main__":
    # 演示用法
    logger = SkillLogger()
    
    # 记录一次调用
    inv_id = logger.log_invocation_start(
        skill_name="coding-agent",
        query="帮我写一个快速排序",
        user_id="test-user",
    )
    
    # 模拟执行
    import time
    time.sleep(0.1)
    
    # 记录结束
    logger.log_invocation_end(
        invocation_id=inv_id,
        success=True,
        output={"latency_ms": 100, "tokens_used": 500},
        quality_signals={"followup_same_skill": False},
    )
    
    # 打印统计
    print(json.dumps(logger.get_stats(), indent=2, ensure_ascii=False))
