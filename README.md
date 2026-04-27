# hermes-skills

> AI Agent Skills Collection · **167 skills** across **21 categories** · 2026-04-27

## Overview

| Metric | Value |
|--------|-------|
| Total Skills | 167 |
| Categories | 21 |
| Updated | 2026-04-27 |

## Categories

| Category | Count |
|---------|-------|
| 🤖 `ai-agent` | 14 |
| 🍎 `apple` | 4 |
| 🧠 `autonomous-ai-agents` | 4 |
| 🎨 `creative` | 11 |
| 🔬 `data-science` | 6 |
| ⚙️ `devops` | 5 |
| 📧 `email` | 3 |
| 🎮 `gaming` | 1 |
| 🐙 `github` | 1 |
| 🔌 `mcp` | 1 |
| 🖼️ `media` | 8 |
| 🚀 `mlops` | 3 |
| 📝 `note-taking` | 4 |
| ⚡ `productivity` | 25 |
| 🔍 `research` | 13 |
| 🏠 `smart-home` | 1 |
| 📱 `social-media` | 1 |
| 💻 `software-development` | 24 |
| 🖥️ `system` | 14 |
| 🧩 `thinking` | 15 |
| ✍️ `writing` | 9 |

### 🤖 ai-agent

| Skill | Description | Triggers |
|-------|-------------|---------|
| `agent-commander` | Agent 会话管理能力。用于创建子会话、发送消息、查看状态、管理多代理协作。触发场景：(1) 需要隔离上下文时创建新会话 (2) 向其他会话发送消息 (3) 查看/监控会话状态 (4) 多代理协作编排 |  |
| `automation-workflows` | Design and implement automation workflows to save time and scale operations as a solopreneur. Use when identifying re... |  |
| `find-skills` | 帮助用户发现和安装 Agent 技能。当用户提出类似"我怎么做 X"、"找一个能做 X 的技能"、"有没有可以……的技能"等问题，或表达出扩展功能的需求时触发。当用户寻找的功能可能以可安装技能的形式存在时，应使用此技能。 |  |
| `free-claude-code` | | Claude Code 零成本路由代理 — 将 Claude Code 的 Anthropic API 调用路由到免费/低成本后端。 触发：安装/启动/配置 free-claude-code、Claude Code 零成本、API... | `free-claude-code`, `Claude`, `Code`, `零成本` |
| `lobster-evolution` | > 龙虾（OpenClaw）自动进化引擎——观察→判断→执行→验证闭环。 【单向架构】lobster-evolution 是唯一主控，读取其他组件的数据输出（单向数据流）： session-miner（观察数据）、skill-prop... | `keywords`, `自动进化`, `龙虾进化`, `session挖掘` |
| `prompt-engineering` | 提示词生成与优化技能。融合道法术器四层体系+2026年TOP10技术。当用户要求优化提示词、生成提示词、改进AI输出质量、设计Prompt框架时触发。 | `提示词`, `prompt`, `优化`, `工程化` |
| `sales-god` | 销售岗位等级评估、金牌策略规划、销售流派诊断、SPIN提问生成、组合技匹配。触发场景：销售咨询、客单价分析、销售策略制定、谈判准备、B2B销售诊断、竞品对比策略、销售培训问题。关键词：销售、客单价、B2B、SPIN、顾问型、挑战型、关... |  |
| `skill-audit` | AI Agent Skills 安全扫描器。扫描 SKILL.md 内容中的危险 pattern、权限过大、数据外传风险。三层递归扫描：批量自动扫描（5min/179skills）→ 重点精准分析 → 元认知自我演进。触发：安装新 s... |  |
| `skill-creator` | Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a... |  |
| `skill-evolution-manager` | 基于对话反馈持续改进 Skills 的核心工具。在对话结束时总结优化并迭代现有 Skills，将用户反馈和经验转化为结构化数据并持久化。 |  |
| `skill-from-github` | 通过学习高质量 GitHub 项目来创建 Skills。当用户想完成某任务时，搜索高质量项目，深入理解，然后基于这些知识创建 Skill。 |  |
| `skill-from-masters` | 基于专家方法论创建高质量 Skills。使用前先发现并整合领域专家的框架和最佳实践。触发场景："帮我创建一个 X 的 skill" 或 "我想做一个能 Y 的 skill"。这个 Skill 先进行方法论研究，然后指导创建最终 Skill。 |  |
| `skill-orchestrator` | 技能编排 — 分析需求调用最合适skill。触发：需要多skill协作时。 技能编排器 - 自动发现、安装并使用最适合的技能来完成任务。  **核心能力:** 1. **需求解析** - 分析用户描述，识别需要的技能组合 2. **自... |  |
| `skill-vetter` | Security-first skill vetting for AI agents. Use before installing any skill from ClawdHub, GitHub, or other sources. ... |  |

### 🍎 apple

| Skill | Description | Triggers |
|-------|-------------|---------|
| `apple-notes` | Manage Apple Notes via the memo CLI on macOS (create, view, search, edit). |  |
| `apple-reminders` | Manage Apple Reminders via remindctl CLI (list, add, complete, delete). |  |
| `findmy` | Track Apple devices and AirTags via FindMy.app on macOS using AppleScript and screen capture. |  |
| `imessage` | Send and receive iMessages/SMS via the imsg CLI on macOS. |  |

### 🧠 autonomous-ai-agents

| Skill | Description | Triggers |
|-------|-------------|---------|
| `claude-code` | Delegate coding tasks to Claude Code (Anthropic's CLI agent). Use for building features, refactoring, PR reviews, and... |  |
| `codex` | Delegate coding tasks to OpenAI Codex CLI agent. Use for building features, refactoring, PR reviews, and batch issue ... |  |
| `hermes-agent` | Complete guide to using and extending Hermes Agent — CLI usage, setup, configuration, spawning additional agents, gat... |  |
| `opencode` | Delegate coding tasks to OpenCode CLI agent for feature implementation, refactoring, PR review, and long-running auto... |  |

### 🎨 creative

| Skill | Description | Triggers |
|-------|-------------|---------|
| `architecture-diagram` | Generate dark-themed SVG diagrams of software systems and cloud infrastructure as standalone HTML files with inline S... |  |
| `ascii-art` | Generate ASCII art using pyfiglet (571 fonts), cowsay, boxes, toilet, image-to-ascii, remote APIs (asciified, ascii.c... |  |
| `baoyu-infographic` | Generate professional infographics with 21 layout types and 21 visual styles. Analyzes content, recommends layout×sty... |  |
| `ideation` | "Generate project ideas through creative constraints. Use when the user says 'I want to build something', 'give me a ... |  |
| `excalidraw` | Create hand-drawn style diagrams using Excalidraw JSON format. Generate .excalidraw files for architecture diagrams, ... |  |
| `fireworks-tech-graph` | >- Use when the user wants to create any technical diagram - architecture, data flow, flowchart, sequence, agent/memo... |  |
| `manim-video` | "Production pipeline for mathematical and technical animations using Manim Community Edition. Creates 3Blue1Brown-sty... |  |
| `p5js` | "Production pipeline for interactive and generative visual art using p5.js. Creates browser-based sketches, generativ... |  |
| `pixel-art` | Convert images into retro pixel art with hardware-accurate palettes (NES, Game Boy, PICO-8, C64, etc.), and animate t... |  |
| `popular-web-designs` | > 54 production-quality design systems extracted from real websites. Load a template to generate HTML/CSS that matche... | `build`, `page`, `that`, `looks` |
| `songwriting-and-ai-music` | > Songwriting craft, AI music generation prompts (Suno focus), parody/adaptation techniques, phonetic tricks, and les... | `writing`, `song`, `song`, `lyrics` |

### 🔬 data-science

| Skill | Description | Triggers |
|-------|-------------|---------|
| `builder-pulse` | > AI 独立开发者日报生成器。每天收集精选情报，生成结构化报告并推送飞书。 触发：今日资讯、builder-pulse、日报、AI情报、独立开发者、产品发布、趋势分析。 | `builder-pulse`, `日报`, `资讯`, `情报` |
| `explorer` | > 探索者 Agent，网络海洋的航海日志。每天出海发现有趣项目，打捞珍宝。 触发：探索、今日出海、发现新项目、打捞、explorer、航海日志、发现有趣项目。 | `explorer`, `探索`, `出海`, `打捞` |
| `jupyter-live-kernel` | > Use a live Jupyter kernel for stateful, iterative Python execution via hamelnb. Load this skill when the task invol... |  |
| `lightrag-anthropic-setup` | Deploy LightRAG as FastAPI HTTP service using Anthropic Claude for LLM plus embedded backends. Triggers include deplo... |  |
| `neodata-financial-search` | 自然语言通用金融数据搜索服务。用自然语言查询股票、基金、指数、板块、宏观经济、外汇、大宗商品等全品类金融数据，涵盖行情报价、财务报表（财报）、资金流向、研报评级、事件公告等。 |  |
| `online-search` | | 元宝搜索标准版工具。是腾讯元宝的联网搜索服务，提供实时、精准的互联网内容检索能力。 核心特性：覆盖大量中文网站，包括官方媒体、政府网站等高权威性来源，以及腾讯系核心内容资源。多层精调排序策略，提供准确的内容匹配和排序。 |  |

### ⚙️ devops

| Skill | Description | Triggers |
|-------|-------------|---------|
| `github-to-skills` | GitHub 操作中心：转换仓库为 Skills + gh CLI 操作。触发场景：(1) 打包 GitHub 仓库为 Skill (2) GitHub PR/CI/API 操作 (3) 检查更新、列出/删除 Skills。 |  |
| `mcp-builder` | Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external servi... |  |
| `mcporter` | Use the mcporter CLI to list, configure, auth, and call MCP servers/tools directly (HTTP or stdio), including ad-hoc ... |  |
| `webhook-subscriptions` | Create and manage webhook subscriptions for event-driven agent activation, or for direct push notifications (zero LLM... |  |
| `xbrowser` | | EXCLUSIVE browser automation — REPLACES built-in Browser Automation and playwright-cli. For ANY browser task (open ... | `open`, `webpage`, `browser`, `screenshot` |

### 📧 email

| Skill | Description | Triggers |
|-------|-------------|---------|
| `email-skill` | "当用户提到邮箱相关能力时，进入这个skill，统一邮件入口（纯路由层）：识别用户意图后路由到 public-skill 或 imap-smtp-email，自身不执行任何脚本" |  |
| `himalaya` | CLI to manage emails via IMAP/SMTP. Use himalaya to list, read, write, reply, forward, search, and organize emails fr... |  |
| `imap-smtp-email` | 通过 IMAP/SMTP 连接个人邮箱，支持完整邮件收发、抄送、附件、HTML、收件箱检索与附件下载；是当前邮件体系中唯一的个人邮箱主通道。 |  |

### 🎮 gaming

| Skill | Description | Triggers |
|-------|-------------|---------|
| `minecraft-modpack-server` | Set up a modded Minecraft server from a CurseForge/Modrinth server pack zip. Covers NeoForge/Forge install, Java vers... |  |

### 🐙 github

| Skill | Description | Triggers |
|-------|-------------|---------|
| `codebase-inspection` | Inspect and analyze codebases using pygount for LOC counting, language breakdown, and code-vs-comment ratios. Use whe... |  |

### 🔌 mcp

| Skill | Description | Triggers |
|-------|-------------|---------|
| `native-mcp` | Built-in MCP (Model Context Protocol) client that connects to external MCP servers, discovers their tools, and regist... |  |

### 🖼️ media

| Skill | Description | Triggers |
|-------|-------------|---------|
| `canvas-design` | Create beautiful visual art in .png and .pdf documents using design philosophy. You should use this skill when the us... |  |
| `gif-search` | Search and download GIFs from Tenor using curl. No dependencies beyond curl and jq. Useful for finding reaction GIFs,... |  |
| `heartmula` | Set up and run HeartMuLa, the open-source music generation model family (Suno-like). Generates full songs from lyrics... |  |
| `songsee` | Generate spectrograms and audio feature visualizations (mel, chroma, MFCC, tempogram, etc.) from audio files via CLI.... |  |
| `svg-card-generator` | SVG卡片生成器 - 将文本内容转换为优雅简洁的SVG卡片可视化。支持多种卡片模板和自定义配置。用于内容展示、社交媒体分享、概念可视化。适用场景：文案美化、概念卡片、读书笔记、金句分享。 |  |
| `theme-factory` | Toolkit for styling artifacts with a theme. These artifacts can be slides, docs, reportings, HTML landing pages, etc.... |  |
| `web-artifacts-builder` | Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologie... |  |
| `youtube-content` | > Fetch YouTube video transcripts and transform them into structured content (chapters, summaries, threads, blog post... |  |

### 🚀 mlops

| Skill | Description | Triggers |
|-------|-------------|---------|
| `huggingface-hub` | Hugging Face Hub CLI (hf) — search, download, and upload models and datasets, manage repos, query datasets with SQL, ... |  |
| `langflow` | "Langflow - 可视化AI工作流编排平台，零代码构建RAG和Agent应用" | `langflow`, `AI工作流`, `RAG可视化`, `无代码AI` |
| `minimax-multimodal` | MiniMax 多模态能力包（TTS语音合成、图像理解、图像生成）。触发场景：说话/读给我听/转语音/转成语音（语音合成）；看图/读图/分析截图/分析照片/分析图表/分析设计稿/分析柱状图/帮我看看/帮我分析/帮我理解（图像理解）；生... |  |

### 📝 note-taking

| Skill | Description | Triggers |
|-------|-------------|---------|
| `context-manager` | 上下文管理器 - 智能压缩、摘要和管理对话历史，优化长对话的token使用。用于长对话维护、信息提取、记忆管理。适用场景：长任务跟踪、多轮对话优化、历史会话检索。 |  |
| `memvid` | "Memory layer for AI Agents. Replace complex RAG pipelines with a serverless, single-file memory layer. Give your age... | `memvid`, `memvid`, `memvid`, `if` |
| `obsidian` | Read, search, and create notes in the Obsidian vault. |  |
| `tapestry` | "知识图谱构建技能，用于文档关联和知识网络管理" | `tapestry`, `tapestry` |

### ⚡ productivity

| Skill | Description | Triggers |
|-------|-------------|---------|
| `checklist-manager` | 清单管理 - 结构化清单生成与管理，将复杂任务拆解为可执行步骤。用于任务规划、流程管理、质量控制。适用场景：项目管理、流程标准化、质量检查、习惯养成。 |  |
| `cloud-upload-backup` | "Cloud file upload and backup tool. Upload local files to Tencent SMH cloud storage, viewable in QClaw Mini Program." |  |
| `docx` | "Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files). Triggers i... |  |
| `frontend-slides` | Create stunning, animation-rich HTML presentations from scratch or by converting PowerPoint files. Use when the user ... |  |
| `google-workspace` | Gmail, Calendar, Drive, Contacts, Sheets, and Docs integration for Hermes. Uses Hermes-managed OAuth2 setup, prefers ... |  |
| `jina-reader` | Convert any URL to clean, readable Markdown using Jina Reader API |  |
| `linear` | Manage Linear issues, projects, and teams via the GraphQL API. Create, update, search, and organize issues. Uses API ... |  |
| `magazine-web-ppt` | 生成"电子杂志 × 电子墨水"风格的横向翻页网页 PPT（单 HTML 文件），含 WebGL 流体背景、衬线标题 + 非衬线正文、章节幕封、数据大字报、图片网格等模板。当用户需要制作分享 / 演讲 / 发布会风格的网页 PPT，或提... |  |
| `maps` | > Location intelligence — geocode a place, reverse-geocode coordinates, find nearby places (44 POI categories), drivi... |  |
| `markitdown` | "MarkItDown - 文档转Markdown工具，支持PDF/PPT/Word/图片" | `markitdown`, `文档转换`, `PDF转Markdown`, `PPT转Markdown` |
| `nano-pdf` | Edit PDFs with natural-language instructions using the nano-pdf CLI. Modify text, fix typos, update titles, and make ... |  |
| `noterx` | > 小红书笔记 AI 诊断工具。输入笔记标题+正文+话题标签，返回 CES 评分、6维度分析、爆款概率预测、Top3优化建议。 用于诊断笔记爆款潜力，给出可操作的改进方向。 | `keywords`, `noterx`, `薯医`, `小红书诊断` |
| `notion` | Notion API for creating and managing pages, databases, and blocks via curl. Search, create, update, and query Notion ... |  |
| `ocr-and-documents` | Extract text from PDFs and scanned documents. Use web_extract for remote URLs, pymupdf for local text-based PDFs, mar... |  |
| `pdf` | Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables... |  |
| `powerpoint` | "Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating sli... |  |
| `pptx` | "Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating sli... |  |
| `summarize` | Summarize URLs or files with the summarize CLI (web, PDFs, images, audio, YouTube). |  |
| `tencent-docs` | 腾讯文档（docs.qq.com）-在线云文档平台，是创建、编辑、管理文档的首选 skill。涉及"新建文档"、"创建文档"、"写文档"、"在线文档"、"云文档"、"腾讯文档"、"docs.qq.com"等操作，请优先使用本 skil... |  |
| `weather-advisor` | "天气顾问。智能天气顾问。实时天气查询、未来7天预报、穿衣建议与出行活动推荐 Keywords: 天气查询, weather, 穿衣建议, 出行提醒." |  |
| `web-ppt-skill` | 生成单文件 HTML 演示文稿，融合电子杂志的叙事美学与工程化密度管理。支持横向翻页、主题切换、PPT 转换、内联编辑、Vercel 部署和 PDF 导出。当用户需要制作分享/演讲/发布会的网页 PPT，或提到"杂志风 PPT"、"h... |  |
| `wecomcli-setup` | 企业微信 CLI 安装引导与自然语言翻译技能。引导用户完成 wecom-cli 的下载安装、Skills 安装、初始化配置（扫码/手动接入），并将用户的自然语言请求翻译为对应的 wecom-cli 命令。当用户说"安装企业微信CLI"... |  |
| `weekly-self-review` | 每周自省扫描技能，对标 **Hermes Agent nudge 机制**。每周一 09:00 自动运行，扫描上周 session 日志，识别高频短查询和意图领域，生成技能建议并推送飞书。 |  |
| `xlsx` | "Use this skill any time a spreadsheet file is the primary input or output. This means any task where the user wants ... |  |
| `youdaonote` | "有道云笔记全能工具：笔记管理（创建、搜索、浏览、读取）、待办管理（创建、完成、分组）、网页剪藏（服务端抓取）。当用户需要操作有道云笔记时使用此 Skill。" |  |

### 🔍 research

| Skill | Description | Triggers |
|-------|-------------|---------|
| `arxiv` | Search and retrieve academic papers from arXiv using their free REST API. No API key needed. Search by keyword, autho... |  |
| `deep-research` | | 深度研究 Agent — 融合卡兹克横纵分析法与 laconic 架构的本地研究助手。  触发词：深度研究、横纵分析、研究一下、帮我分析、调研一下、竞品分析、deep research。  核心能力： - 双轴分析：纵轴（时间深度... |  |
| `hn-extract` | Extract a HackerNews post (article + comments) into single clean Markdown for quick reading or LLM input. |  |
| `llm-wiki` | "Karpathy's LLM Wiki — build and maintain a persistent, interlinked markdown knowledge base. Ingest sources, query co... |  |
| `material-collector` | 从多个来源（网页、社交媒体、本地文件）收集素材，支持分类存储、去重、标签管理和多平台集成 |  |
| `"multi-search-engine"` | 多搜索引擎聚合，集成 17 个引擎（8 个国内 + 9 个国际）。支持高级搜索语法、时间筛选、站内搜索、隐私引擎和 WolframAlpha 知识查询。无需 API 密钥。 |  |
| `news-summary` | This skill should be used when the user asks for news updates, daily briefings, or what's happening in the world. Fet... |  |
| `para-second-brain` | Organize your agent's knowledge using PARA (Projects, Areas, Resources, Archive) — then make it ALL searchable. The s... |  |
| `polymarket` | Query Polymarket prediction market data — search markets, get prices, orderbooks, and price history. Read-only via pu... |  |
| `research-paper-writing` | End-to-end pipeline for writing ML/AI research papers — from experiment design through analysis, drafting, revision, ... |  |
| `"tavily-search"` | | Tavily AI 搜索 API — 提供结构化搜索结果与引用来源标注的深度研究工具。   触发词：tavily、AI搜索、结构化搜索、cited answer、research-grade search、带来源的搜索   核心能... |  |
| `tech-news-digest` | "科技新闻多源聚合摘要。从100+信息源自动采集并评分科技新闻。Keywords: 科技新闻, tech news, RSS, industry trends." |  |
| `wiki-retriever` | | Wiki BM25 + wikilink 混合检索服务。LightRAG 的零依赖替代方案，基于 rank-bm25 实现， 无需 PyTorch，已在 ~/wiki 验证可用（75 页索引）。 | `wiki`, `检索`, `wiki`, `搜索` |

### 🏠 smart-home

| Skill | Description | Triggers |
|-------|-------------|---------|
| `openhue` | Control Philips Hue lights, rooms, and scenes via the OpenHue CLI. Turn lights on/off, adjust brightness, color, colo... |  |

### 📱 social-media

| Skill | Description | Triggers |
|-------|-------------|---------|
| `xurl` | Interact with X/Twitter via xurl, the official X API CLI. Use for posting, replying, quoting, searching, timelines, m... |  |

### 💻 software-development

| Skill | Description | Triggers |
|-------|-------------|---------|
| `local-agent-browser` | Fast headless browser automation CLI for AI agents (v0.26.0). Use when automating web interactions, scraping, filling... |  |
| `browser` | Automate web browser interactions using natural language via CLI commands. Use when the user asks to browse websites,... |  |
| `code-review-expert` | "Expert code review of current git changes with a senior engineer lens. Detects SOLID violations, security risks, and... |  |
| `codebase-to-course` | "Turn any codebase into a beautiful, interactive single-page HTML course that teaches how the code works to non-techn... |  |
| `coding-agent` | > Autonomous coding execution engine — use whenever someone asks to code, build, create, implement, refactor, debug, ... | `帮我写代码`, `写个`, `写一个`, `做一个小工具` |
| `commit` | 智能生成 git commit message，支持 Conventional Commits 格式。 |  |
| `db-query` | Query project databases with automatic SSH tunnel management. Use when you need to execute SQL queries against config... |  |
| `fast-edit` | 大文件编辑、批量修改、剪贴板/stdin粘贴、多文件写入、编辑验证/回滚。用于替代慢速的 Edit/Write 工具。（重构测试版） |  |
| `fastapi` | "FastAPI - Python现代高性能Web框架" | `fastapi`, `Python`, `API`, `异步API` |
| `frontend-design` | Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks ... |  |
| `git` | "Git workflow best practices and safety rules. Use when the user is working with git operations, committing code, res... | `git`, `git` |
| `karpathy-coding-principles` | Karpathy 编码四原则 — Think Before Coding / Simplicity First / Surgical Changes / Goal-Driven Execution。用于开发任务的质量守则，减少 LLM... |  |
| `kc-gui` | Use the bundled kc.exe Windows agent to perform GUI-based desktop automation tasks that cannot be handled through CLI... |  |
| `perf-profiler` | Profile and optimize application performance. Use when diagnosing slow code, measuring CPU/memory usage, generating f... |  |
| `plan` | Plan mode for Hermes — inspect context, write a markdown plan into the active workspace's `.hermes/plans/` directory,... |  |
| `playwright` | "Auto-generated skill from AQA" | `playwright` |
| `prettier` | "Prettier is an opinionated code formatter." | `prettier`, `prettier`, `prettier`, `if` |
| `requesting-code-review` | > Pre-commit verification pipeline — static security scan, baseline-aware quality gates, independent reviewer subagen... |  |
| `subagent-driven-development` | Use when executing implementation plans with independent tasks. Dispatches fresh delegate_task per task with two-stag... |  |
| `systematic-debugging` | Use when encountering any bug, test failure, or unexpected behavior. 4-phase root cause investigation — NO fixes with... |  |
| `test-driven-development` | Use when implementing any feature or bugfix, before writing implementation code. Enforces RED-GREEN-REFACTOR cycle wi... |  |
| `tmux` | Remote-control tmux sessions for interactive CLIs by sending keystrokes and scraping pane output. |  |
| `webapp-testing` | Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functio... |  |
| `writing-plans` | Use when you have a spec or requirements for a multi-step task. Creates comprehensive implementation plans with bite-... |  |

### 🖥️ system

| Skill | Description | Triggers |
|-------|-------------|---------|
| `bb-browser-sites` | Turn any website into a CLI command. 36 platforms, 103 commands — Twitter, Reddit, GitHub, YouTube, Zhihu, Bilibili, ... |  |
| `cron-mastery` | Master OpenClaw's timing systems. Use for scheduling reliable reminders, setting up periodic maintenance (janitor job... |  |
| `cron-scheduling` | Schedule and manage recurring tasks with cron and systemd timers. Use when setting up cron jobs, writing systemd time... |  |
| `文件整理` | '智能文件/桌面整理技能。当用户 prompt 中包含"桌面整理"、"文件整理"、"整理桌面"、"整理文件"、"整理文件夹"、"清理桌面"、"排列桌面"、"桌面排列"、"桌面排序"、"按类型排列"、"按项目类型排列"等字样时，优先使用... |  |
| `mac-use` | Control macOS GUI apps visually — take screenshots, click, scroll, type. Use when the user asks to interact with any ... |  |
| `migration-prep` | OpenClaw → Hermes 迁移风险评估工具。分析 `~/.openclaw/` 目录结构，识别迁移风险，生成检查清单。在你决定是否迁移 Hermes 前必读。 |  |
| `openclaw-agent-optimize` | Optimize an OpenClaw agent setup (model routing, context management, delegation, rules, memory). Use when asked about... | `optimize`, `agent`, `optimizing`, `agent` |
| `openclaw-control-cli` | | CLI tools for OpenClaw gateway management. Two implementations: - Python (config file): safe offline config editing... | `代理设置`, `gateway`, `status`, `openclaw` |
| `token-optimizer` | Reduce OpenClaw token usage and API costs through smart model routing, heartbeat optimization, budget tracking, and m... |  |
| `security-monitor` | Real-time security monitoring for Clawdbot. Detects intrusions, unusual API calls, credential usage patterns, and ale... |  |
| `session-insights` | | 根据 OpenClaw 历史 Session 生成复盘报告和洞察分析。  触发场景： - 用户问"insights"、"复盘"、"session 分析" - 用户想回顾过去一段时间的工作内容 - 用户问"今天做了什么"、"这周做了... |  |
| `session-logs` | Search and analyze your own session logs (older/parent conversations) using jq. |  |
| `skill-combinator` | Skills 组合涌现引擎 — 根据任务特征自动发现、排序、组合 skills。触发：多 skill 协作需求、复杂任务分解、技能选型决策。 |  |
| `system-health-reporter` | Generate system health reports with CPU, memory, disk, network diagnostics and recommendations. |  |

### 🧩 thinking

| Skill | Description | Triggers |
|-------|-------------|---------|
| `blade-of-logic` | 逻辑之刃 - 使用命题化、符号推理和逻辑分析庖丁解牛般拆解文本逻辑脉络。用于分析论证结构、识别逻辑谬误、构建严密推理、学术写作论证。适用场景：论文写作、辩论准备、决策分析、批判性思维训练。 |  |
| `brainstorming` | 头脑风暴技能 - 创意发散与思路拓展。触发：需要创意想法、解决方案发散、思路拓展、多方案对比。 |  |
| `complexity-sensor` | > 复杂性思维传感器 — 检测 skill 组合的复杂度、相变临界点、涌现信号。 用于：当技能组合产生意外结果时、故障排查时、系统行为异常时、技术架构评审时。 核心功能：监控 skill 组合的复杂度、检测相变临界点、识别涌现行为。 |  |
| `context-pollution-defender` | 防止长任务中上下文污染导致响应质量下降。触发：长任务(30min+/50+calls)、用户反馈跑偏、优先级固化。 |  |
| `debugging-reasoning-framework` | 高水平AI调试推理框架。触发：遇到bug/故障/系统异常时加载。替代简单的"已知问题→假设→验证"循环。 |  |
| `ladder-of-abstraction` | 抽象之梯 - 将文本在具象细节与抽象概括之间自如转换。用于写作、思考、沟通时，把含混不清的表达改写成细腻具象（如莫言般的感官描写）或凝练抽象（如哲学概念）的表达。适用场景：创意写作、学术写作、演讲稿优化、概念澄清。 |  |
| `meta-skill-skeleton` | Meta-skill 的骨架——整合所有高阶能力框架。触发：构建新skill时，或评估skill质量时使用。 |  |
| `metacognition-auditor` | > 元认知审计器 — 决策审计、预验尸、认知盲区检测。 用于：技术选型时、故障复盘时、做重大决策时、多次失败后框架冲突时。 核心功能：二阶思维执行、预验尸分析、认知盲区识别。 |  |
| `mirror-of-perspectives` | 视角之镜 - 找到独特的观察角度，使复杂问题变得异常简单易解。用于问题解决、创新思考、突破思维定势。适用场景：难题攻关、产品设计、战略决策、创意发想。 |  |
| `paradigm-detector` | > 范式跃迁检测器 — 识别架构瓶颈、检测范式转移信号、触发重构时机。 用于：系统成为枷锁时、专家用同样方法收益递减时、技术债累积时。 核心功能：范式识别、跃迁信号检测、重构时机判断。 |  |
| `reflect` | Self-improvement through conversation analysis. Extracts learnings from corrections and success patterns, permanently... |  |
| `response-strategy-decider` | 结论优先 vs 风险前置的边界判断框架。触发：用户提出问题后不确定先给结论还是先说风险。 |  |
| `self-improving` | 自我改进 Agent - 从对话分析中提取学习点，将修正永久编码到 agent 定义中。触发：自我反思、从错误中学习、提取经验、持续改进。 |  |
| `six-thinking-hats` | 六顶思考帽 - 爱德华·德博诺的平行思考方法。系统化地从六个维度分析问题：客观事实、情感直觉、风险谨慎、乐观价值、创意创新、控制流程。用于全面决策分析、团队讨论、问题解决。适用场景：重大决策、方案评估、创新发想、团队共识。 |  |
| `talent-mind` | 天才思维方法论 - 三层递归操作系统。用于深度思考、问题分析、认知升级。当遇到难题、思维瓶颈、需要创新解决方案时触发。 |  |

### ✍️ writing

| Skill | Description | Triggers |
|-------|-------------|---------|
| `academic-paper` | "Academic paper writing skill with 12-agent pipeline. v2.4: LaTeX output formatting hardening — mandatory apa7 class,... |  |
| `academic-paper-reviewer` | "Multi-perspective academic paper review with dynamic reviewer personas. Simulates 5 independent reviewers (EIC + 3 p... |  |
| `academic-pipeline` | "Orchestrator: research → write → integrity check → review → revise → re-review → re-revise → final integrity → final... |  |
| `auto-content-creator` | 基于素材自动生成内容，支持多种创作类型、模板风格管理、一键发布到多平台 |  |
| `content-editor` | 审稿润色系统，支持语言润色、逻辑检查、结构优化、风格统一、错别字修正，可联动内容生成系统 |  |
| `content-factory` | "多代理内容生产线。自动化从选题研究到内容创作的全流程。Keywords: 内容创作, 文案, content creation, copywriting." |  |
| `doc-coauthoring` | Guide users through a structured workflow for co-authoring documentation. Use when user wants to write documentation,... |  |
| `novel-quality-guardian` | 小说质量守护者 - 强制锚定 + 质量门 + 迭代机制。解决长篇小说创作中的人物走样、情节重复、前后矛盾等问题。核心原理：不是AI能力不行，而是锚定信息不够。触发场景：写新章节、质检、创作质量崩塌诊断。 | `小说质量`, `写作质量`, `章节检查`, `创作质量` |
| `novel-writing-sop` | 中文小说创作SOP——种子→萌芽→枝干→枝叶四层模型。触发：写小说/创作故事/章节写作/续写/长篇创作/继续上次/接着写/从第X章开始/批量生成章节/扩充章节字数/规划大纲/悬念钩子/开头技巧/去AI味。核心功能：13种悬念钩子设计、... |  |

---
*Generated by `scripts/generate_readme.py`*