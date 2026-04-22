---
name: langflow
description: "Langflow - 可视化AI工作流编排平台，零代码构建RAG和Agent应用"
triggers:
  - "langflow"
  - "AI工作流"
  - "RAG可视化"
  - "无代码AI"
source:
  url: https://github.com/langflow-ai/langflow
  auto_generated: false
---

# Langflow Skill

Langflow 是一个可视化的AI工作流编排平台，可零代码构建RAG（检索增强生成）和Agent应用。

## 触发场景
- "搭建RAG流程"
- "可视化AI工作流"
- "langflow使用"
- "无代码构建AI应用"
- "知识库问答系统"

## 核心能力
1. **可视化编排** - 拖拽式构建AI工作流
2. **RAG支持** - 内置文档加载器、向量存储、检索器
3. **Agent模板** - 预置ReAct、LangChain等Agent模板
4. **多模型支持** - OpenAI、Anthropic、Google等LLM集成
5. **API导出** - 一键导出为REST API

## 本地部署

```bash
# 安装
pip install langflow

# 启动
langflow
# 访问 http://127.0.0.1:7860
```

## 典型工作流

### 简单RAG流程
1. PDF/File Loader → 加载文档
2. Text Splitter → 分块
3. Chroma → 向量存储
4. Retrieval QA Chain → 问答

### Agent工作流
1. Chat Input → 用户输入
2. Agent → ReAct Agent
3. Tool → 搜索/计算工具
4. Chat Output → 输出

## 与现有Skills联动
- 可配合 `ai-rag-pipeline` 做深度RAG
- 配合 `chromadb` 做向量存储
- 配合 `pdf` 做文档处理

## 注意事项
- 依赖LangChain
- 需要LLM API Key
- 生产环境需配置数据库
