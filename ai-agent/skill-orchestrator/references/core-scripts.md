## 核心脚本

### auto-orchestrate.py

```python
#!/usr/bin/env python3
"""
自动技能编排脚本
用法: python auto-orchestrate.py "需求描述"
"""

import sys
import subprocess
import json
from pathlib import Path

class SkillOrchestrator:
    def __init__(self):
        self.skills_dir = Path("skills")
        self.model_priority = [
            "kimi-coding/k2p5",
            "kimi-k2p5",
            "claude-sonnet",
        ]
    
    def parse_requirement(self, description: str) -> list:
        """解析需求为子任务"""
        # 关键词匹配
        keywords = {
            "csv|excel|xlsx": "xlsx",
            "pdf": "pdf",
            "chart|graph|visual": "canvas-design",
            "image|photo": "canvas-design",
            "ppt|slide|presentation": "pptx",
            "doc|word|document": "docx",
            "test|spec": "test-driven-development",
            "optimize|performance": "performance-optimizer",
            "database|sql|db": "database",
            "github|git|pr": "github",
            "web|browser|scrape": "browser",
            "cron|schedule|timer": "cron-mastery",
        }
        
        tasks = []
        desc_lower = description.lower()
        
        for pattern, skill in keywords.items():
            if any(p in desc_lower for p in pattern.split("|")):
                tasks.append({
                    "skill": skill,
                    "action": "auto",
                })
        
        return tasks
    
    def check_skill_installed(self, skill_name: str) -> bool:
        """检查技能是否已安装"""
        return (self.skills_dir / skill_name).exists()
    
    def install_skill(self, skill_name: str) -> bool:
        """安装技能（使用 skillhub_install 工具）"""
        # 注意：实际实现应调用 skillhub_install 工具
        # 这里仅为示例，展示正确的调用方式
        try:
            # 正确方式：调用 skillhub_install 工具
            # result = skillhub_install(action="install_skill", skillName=skill_name)
            # return result.success
            return True
        except Exception as e:
            log_error(f"安装失败: {e}")
            return False
    
    def select_model(self, task_complexity: str = "medium") -> str:
        """选择执行模型"""
        # 检查当前模型状态
        for model in self.model_priority:
            if self.is_model_available(model):
                return model
        return self.model_priority[0]
    
    def is_model_available(self, model: str) -> bool:
        """检查模型是否可用"""
        # 通过轻量请求检测
        return True
    
    def execute_subtask(self, task: dict, model: str) -> str:
        """执行子任务"""
        # 调用 sessions_spawn 或其他方式
        return ""
    
    def orchestrate(self, description: str) -> dict:
        """主编排流程"""
        # 1. 解析需求
        tasks = self.parse_requirement(description)
        
        # 2. 确保技能安装
        for task in tasks:
            skill = task["skill"]
            if not self.check_skill_installed(skill):
                print(f"发现缺失技能: {skill}")
                # 使用 skillhub_install 工具自动安装
                # 工具会处理所有依赖和环境
                self.install_skill(skill)
        
        # 3. 选择模型
        model = self.select_model()
        
        # 4. 执行任务
        results = []
        for task in tasks:
            result = self.execute_subtask(task, model)
            results.append(result)
        
        # 5. 整合结果
        return {
            "tasks": tasks,
            "model_used": model,
            "results": results,
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python auto-orchestrate.py '需求描述'")
        sys.exit(1)
    
    description = sys.argv[1]
    orchestrator = SkillOrchestrator()
    result = orchestrator.orchestrate(description)
    print(json.dumps(result, indent=2))
```

