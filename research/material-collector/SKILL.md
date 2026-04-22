---
name: material-collector
title: Material Collector - Multi-Source Asset Gathering
version: 1.0.0
description: 从多个来源（网页、社交媒体、本地文件）收集素材，支持分类存储、去重、标签管理和多平台集成
tags: ["素材收集", "content-collection", "asset-management", "web-scraping", "social-media", "deduplication", "tagging", "multi-platform", "素材管理"]
metadata:
  author_name: "OpenClaw System"
  author_role: "Content Workflow Automation"
  supported_platforms:
    - "Twitter/X"
    - "YouTube"
    - "Web Pages"
    - "Local Files"
    - "Feishu/Lark"
    - "Telegram"
  features:
    - "多源素材采集"
    - "智能分类存储"
    - "去重管理"
    - "标签系统"
    - "元数据提取"
---

# 素材收集系统 (Material Collector)

从多个来源高效收集、组织和管理数字素材，支持去重和智能标签。

## 适用场景

- **社交媒体素材收集**：从 Twitter/X、YouTube、Telegram 收集内容
- **网页素材采集**：抓取网页内容、图片、视频和文档
- **本地文件管理**：整理和索引本地素材库
- **项目素材归档**：为创作项目系统化收集参考资料
- **竞品分析素材**：批量收集行业相关内容

## 核心功能

### 1. 多源采集引擎

| 来源类型 | 采集能力 | 说明 |
|---------|---------|------|
| **Twitter/X** | 推文、图片、视频、线程 | 支持用户时间线、话题搜索、列表 |
| **YouTube** | 视频、字幕、缩略图、评论 | 支持频道、播放列表、视频搜索 |
| **网页** | 全文、图片、链接、元数据 | 智能解析多种页面结构 |
| **本地文件** | 图片、文档、视频、音频 | 支持批量索引和分类 |
| **Telegram** | 消息、媒体、频道内容 | 支持群组和频道素材收集 |
| **Feishu/Lark** | 文档、云空间、媒体库 | 企业素材库集成 |

### 2. 智能分类存储

```
素材库结构：
├── raw/                    # 原始素材
│   ├── images/
│   ├── videos/
│   ├── documents/
│   └── audio/
├── processed/              # 处理后素材
│   ├── optimized/
│   └── thumbnails/
├── metadata/               # 元数据索引
│   ├── material-index.json
│   └── tags/
└── archive/                # 归档素材
```

### 3. 去重系统

- **哈希去重**：基于文件内容的 MD5/SHA 指纹检测
- **相似度去重**：图片相似度检测（感知哈希算法）
- **内容去重**：文本相似度比较
- **自动标记**：重复素材自动标记而非删除

### 4. 标签管理系统

- **自动标签**：基于内容、来源、日期自动生成标签
- **手动标签**：支持用户自定义标签
- **标签层级**：支持父标签和子标签结构
- **标签统计**：标签使用频率分析

## 核心工具/命令

### 素材采集命令

```bash
# 采集 Twitter/X 素材
collect twitter --username=<user> --types=tweet,image,video --limit=100
collect twitter --search="关键词" --filter=images --max=50

# 采集 YouTube 素材  
collect youtube --channel=<channel_id> --include=video,thumbnail,subtitle
collect youtube --video_id=<id> --download=subtitles --format=srt

# 采集网页素材
collect webpage --url=<url> --types=text,images,links --extract_metadata
collect webpage --batch=urls.txt --recursive=true

# 采集本地素材
collect local --path=/path/to/materials --recursive=true --organize=true
collect local --scan --duplicates=true --tagging=true

# 采集 Telegram 素材
collect telegram --chat=<chat_id> --media_types=photo,video,document
collect telegram --channel=<channel_name> --export=true

# 采集 Feishu 素材
collect feishu --folder=<folder_id> --include=media,documents
```

### 素材管理命令

```bash
# 素材查询
query materials --tags=design,inspiration --type=image --sort=date_desc
query materials --source=twitter --date_range=2026-01-01_2026-02-01

# 标签管理
tag materials --add="2026-热门" --filter=likes>100
tag materials --remove=outdated --batch=true
tag materials --auto_tag --source=twitter --model=smart

# 去重操作
deduplicate --check=true --action=mark --strategy=hash
deduplicate --images --similarity_threshold=0.85 --action=review

# 素材导出
export materials --format=zip --include_metadata --dest=/backup/
export materials --to=feishu --folder=素材收集 --compress=true
```

### 素材处理命令

```bash
# 图片处理
process images --resize=1920x1080 --optimize --format=webp
process images --thumbnail --size=300x300 --watermark=true

# 视频处理
process videos --extract_frames --interval=10s --format=jpg
process videos --compress --quality=high --remove_audio=false

# 文本处理
process text --extract_text --summarize --language=zh
process text --translate --to=en --preserve_formatting=true
```

## 配置说明

### 配置文件位置

```
~/.openclaw/config/material-collector.yaml
```

### 基础配置

```yaml
# 基础设置
storage:
  base_path: ~/materials
  raw_folder: raw
  processed_folder: processed
  metadata_folder: metadata
  archive_folder: archive

# 去重设置
deduplication:
  enabled: true
  hash_algorithm: sha256
  image_similarity_threshold: 0.85
  text_similarity_threshold: 0.9
  action: mark  # mark, review, delete
  auto_clean_days: 30

# 标签设置
tagging:
  auto_tag_enabled: true
  auto_tag_sources:
    - content
    - filename
    - metadata
  max_auto_tags: 10
  custom_tag_rules:
    - pattern: "设计.*" → 设计
    - pattern: "inspiration" → 灵感
```

### 平台认证配置

```yaml
# Twitter/X API
twitter:
  api_key: ${TWITTER_API_KEY}
  api_secret: ${TWITTER_API_SECRET}
  access_token: ${TWITTER_ACCESS_TOKEN}
  access_secret: ${TWITTER_ACCESS_SECRET}

# YouTube Data API
youtube:
  api_key: ${YOUTUBE_API_KEY}
  oauth_token: ${YOUTUBE_OAUTH_TOKEN}

# Telegram Bot
telegram:
  bot_token: ${TELEGRAM_BOT_TOKEN}
  session_name: default

# Feishu/Lark
feishu:
  app_id: ${FEISHU_APP_ID}
  app_secret: ${FEISHU_APP_SECRET}
```

### 采集规则配置

```yaml
collection_rules:
  # 速率限制
  rate_limit:
    twitter:
      requests_per_hour: 300
      burst: 10
    youtube:
      requests_per_second: 1
    telegram:
      messages_per_second: 5

  # 内容过滤
  filters:
    min_image_width: 200
    min_image_height: 200
    max_file_size_mb: 100
    allowed_formats:
      - jpg
      - png
      - mp4
      - pdf
      - docx

  # 自动组织
  auto_organize:
    enabled: true
    folder_structure: source/type/YYYY-MM
    naming_pattern: "{source}_{type}_{date}_{hash}"
```

## 使用示例

### 示例 1：收集设计灵感素材

```bash
# 搜索并收集设计相关内容
collect twitter --search="设计 灵感 UI" --types=image --limit=50
collect webpage --url=https://dribbble.com --types=images --filter=shots

# 自动标签
tag materials --auto_tag --source=design

# 查看收集结果
query materials --tags=design,灵感 --type=image
```

### 示例 2：项目素材库初始化

```bash
# 创建项目素材库
collect local --path=./references --init=true --create_structure=true

# 收集竞品资料
collect webpage --url=https://competitor.com --recursive=true --types=text,images
collect twitter --username=competitor --include=media

# 设置标签规则
tag materials --add="竞品" --filter=source=competitor.com
```

### 示例 3：YouTube 视频素材提取

```bash
# 收集教程视频
collect youtube --channel=UCxxx --include=video,subtitle --quality=high

# 提取关键帧
process videos --extract_frames --interval=60s --from=raw/videos/

# 生成缩略图
process images --thumbnail --size=400x225 --source=processed/frames/
```

### 示例 4：素材去重和整理

```bash
# 检查重复
deduplicate --check=true --types=images,documents

# 相似图片审查
deduplicate --images --similarity_threshold=0.9 --action=review

# 批量标签
tag materials --add="待处理" --filter=duplicates=true
```

## 与其他 Skills 的配合

| 场景 | 使用 Skill |
|------|-----------|
| 收集素材 | `material-collector` |
| 素材创作 | `auto-content-creator` |
| 素材发布 | `x-post-automation` |
| 知识管理 | `para-second-brain` |
| 浏览器操作 | `browser-automation` |

## 注意事项

1. **尊重版权**：收集素材时请注意版权限制，仅用于学习参考
2. **遵守平台规则**：遵守各平台的 API 使用条款和速率限制
3. **数据备份**：定期备份素材库和索引
4. **隐私保护**：敏感素材请加密存储
5. **存储空间**：监控磁盘使用，避免过度收集

## 输出位置

所有素材保存在 `~/materials/` 目录：
- 原始素材：`raw/`
- 处理后素材：`processed/`
- 元数据：`metadata/material-index.json`
- 日志：`logs/collection.log`
