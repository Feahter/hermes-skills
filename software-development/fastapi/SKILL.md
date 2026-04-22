---
name: fastapi
description: "FastAPI - Python现代高性能Web框架"
triggers:
  - "fastapi"
  - "Python API"
  - "异步API"
  - "REST API"
source:
  url: https://github.com/fastapi/fastapi
  auto_generated: false
---

# FastAPI Skill

FastAPI 是Python现代高性能Web框架，支持异步API开发。

## 触发场景
- "创建API"
- "FastAPI教程"
- "Python异步"
- "REST API开发"
- "构建Web服务"

## 核心能力
1. **高性能** - 异步支持，与Node.js和Go相当
2. **自动文档** - Swagger UI自动生成
3. **类型提示** - Pydantic数据验证
4. **依赖注入** - 简洁的依赖系统
5. **WebSocket** - 实时通信支持

## 基础用法

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
async def create_item(item: Item):
    return item
```

## 常用功能
- 路径参数：`@app.get("/items/{item_id}")`
- 查询参数：`@app.get("/items/?skip=0")`
- 请求体：`@app.post("/items/")`
- 表单：`@app.post("/login/")`
- 文件上传：`@app.post("/uploadfile/")`

## 部署
```bash
# 安装
pip install fastapi uvicorn

# 运行
uvicorn main:app --reload
```

## 与其他Skills联动
- 配合 `pydantic` 做数据验证
- 配合 `database` 做数据库操作
- 配合 `swagger` 生成API文档
