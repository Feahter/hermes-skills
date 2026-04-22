# DSPy 3.0 提示编译流程

## 何时需要 DSPy

- 提示词已经过人工优化，效果仍不稳定
- 需要在多个任务变体上保持一致性
- 有足够的训练样本（10-20个）
- 想自动化 few-shot 示例选择

## 标准编译流程

### Step 1: 定义任务签名

```python
import dspy

class Extract(dspy.Signature):
    """从文本中提取实体"""
    text = dspy.InputField(desc="原始文本")
    entities = dspy.OutputField(desc="list of (name, type) tuples")
```

### Step 2: 准备训练集

```python
trainset = [
    {"text": "Apple发布了iPhone 15...", "entities": [("Apple", "ORG"), ("iPhone 15", "PRODUCT")]},
    {"text": "张三在北京工作...", "entities": [("张三", "PERSON"), ("北京", "LOCATION")]},
    # ... 10-20个样本
]
```

### Step 3: 选择优化器

```python
# MIPROv2: 自动搜索最优提示 + few-shot组合
from dspy.predict import MIPRO

optimizer = MIPRO(
    metric=lambda pred, example: pred.entities == example.entities,
    num_trials=50,
    max_bootstrapped_demos=4,
    temperature=0.3
)
```

### Step 4: 编译

```python
optimized = optimizer.compile(
    Extract,
    trainset=trainset,
    max_errors=10
)
```

### Step 5: 验证泛化

```python
testset = [...]  # 留出测试集
dspy.evaluate.HOTPOTQA(optimized, devset=testset)
```

## 与手工优化的关系

DSPy 是手工优化的**补充**，不是替代：

| 场景 | 用手工 | 用DSPy |
|------|--------|--------|
| 0→1 快速验证 | ✅ | ❌ |
| 单一样本调优 | ✅ | ❌ |
| 10+ 样本稳定化 | ❌ | ✅ |
| 多任务统一 | ❌ | ✅ |

## 局限性

- 训练样本需要人工标注高质量答案
- 编译成本高（50+ trials）
- 结果可解释性差（不知道为什么提示词变好了）
- 对极端案例仍需手工干预
