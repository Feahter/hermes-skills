# 三阶段渐进实现模式

这是一个通用模式，适用于构建任何需要"基础设施 → 质量闭环 → 智能路由"的系统。

## 模式结构

```
Phase 1: 止血（可用的最小闭环）
    └─ 建立数据采集基础设施
    └─ 不追求完美，先能记录

Phase 2: 闭环（让数据产生价值）
    └─ 从数据中提炼可执行的质量信号
    └─ 建立回归测试和 A/B 测试

Phase 3: 智能（用数据做路由决策）
    └─ 从历史数据学习边界
    └─ 主动探测未知边界
    └─ 路由时做风险检查
```

## 判断标准

| 问题 | Phase 1 解决 | Phase 2 解决 | Phase 3 解决 |
|------|-------------|-------------|-------------|
| 不知道发生了什么 | ✅ 日志 | | |
| 不知道谁在失败 | ✅ fail_cases | | |
| 不知道失败原因 | | ✅ 失败模式分析 | |
| 不知道下次会不会失败 | | ✅ 回归测试 | |
| 不知道边界在哪 | | | ✅ 边界签名 |
| 不想被动等失败 | | | ✅ 主动探测 |

## 本次实现案例

对应项目：Skills 可观测性系统

```
用户问 HL 理论 → 分析借鉴 → 设计三阶段补全计划
    ↓
Phase 1: skill_logger.py + CLI + 嵌入 skill-orchestrator
    ↓
Phase 2: regression_generator + ab_tester + phase2.py + 联动 evolution-manager
    ↓
Phase 3: boundary_detector + skills_feedback.py 统一入口
```

## 通用启动命令

```bash
# Phase 1 完成后
echo "基础数据采集就绪"

# Phase 2 完成后  
python3 ~/.hermes/skills/.experiment_log/phase2.py --full-loop {skill_name}

# Phase 3 完成后
python3 ~/.hermes/skills/.experiment_log/skills_feedback.py --stats
```

## 警示

**Phase 2 的回归测试生成依赖 Phase 1 的失败案例积累**。如果失败案例太少（< 3 条），生成的回归测试置信度低，需要先积累数据或手动补充测试用例。
