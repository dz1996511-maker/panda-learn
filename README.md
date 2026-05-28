# 🐼 Panda Learn — 震惊！这个AI学习助手把RAG+间隔重复玩明白了

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek%20|%20Claude%20|%20GPT-4F5A8B?logo=openai&logoColor=white)](https://github.com/dz1996511-maker/panda-learn)

**🏆 上传PDF → AI自动提取知识点 → 间隔重复复习 → 掌握度追踪 — 考研/考证/自学神器**

[English](#english) · [中文](#中文) · [快速开始](#-快速开始) · [功能列表](#-核心功能)

</div>

<a name="中文"></a>

## 📖 这是啥？

别人刷题背单词，你直接上传 PDF 让 AI 帮你学。

**熊猫学习**是一个基于 **RAG（检索增强生成）** + **SM-2 间隔重复算法**的开源 AI 学习助手。上传你的 PDF/教材/笔记，AI 自动提取知识点、出题、安排复习计划。支持 DeepSeek / Claude / GPT 自由切换。

> 💡 适合：考研党、留学生、程序员学新技术、考证党

### ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 📄 **智能知识库** | 上传 PDF / TXT / Markdown / HTML，自动分块、向量化、索引 |
| 💬 **RAG 问答** | 基于知识库语义检索 + LLM 生成，引用原文出处 |
| 🧠 **知识点提取** | AI 自动提取文档核心概念和知识点 |
| 🔄 **间隔重复** | 基于 SM-2 算法的科学复习计划 |
| 📝 **自动出题** | AI 生成选择题、判断题、填空题 |
| 📊 **掌握度追踪** | 多信号综合评估（时间 + 练习 + 稳定性） |
| 🎯 **学习报告** | 薄弱点识别、学习进度可视化 |
| 🔌 **多 LLM 支持** | DeepSeek（默认）/ Claude / OpenAI 自由切换 |
| 🐼 **熊猫主题 UI** | 深色玻璃态设计，像素熊猫伴学吉祥物 |

### 🏗️ 技术架构

```
┌─────────────────────────────────────────────┐
│             浏览器 (Jinja2 + HTMX)            │
├─────────────────────────────────────────────┤
│              FastAPI 应用层                    │
├──────────┬──────────┬──────────┬────────────┤
│ 知识库    │ 学习引擎 │ 练习系统 │ 分析模块    │
│ RAG检索   │ SM-2算法 │ 自动出题 │ 掌握度报告  │
│ ChromaDB │ 复习计划 │ 答题评估 │ 概念关系    │
├──────────┴──────────┴──────────┴────────────┤
│          LLM 提供层 (DeepSeek/Claude/OpenAI) │
├─────────────────────────────────────────────┤
│          SQLite + ChromaDB 持久化            │
└─────────────────────────────────────────────┘
```

### 🚀 快速开始

#### 方式一：Docker（推荐）

```bash
git clone https://github.com/dz1996511-maker/panda-learn.git
cd panda-learn

# 编辑 .env 填入至少一个 LLM API Key
echo "DEEPSEEK_API_KEY=your_key_here" > .env

# 一键启动
docker compose up -d

# 打开 http://localhost:5000
```

#### 方式二：手动运行

```bash
# 需要 Python 3.11+
git clone https://github.com/dz1996511-maker/panda-learn.git
cd panda-learn

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置 API Key
echo "DEEPSEEK_API_KEY=your_key_here" > .env

# 启动
python -m app

# 打开 http://localhost:5000
```

### 🖥️ 界面预览

| 页面 | 特点 |
|------|------|
| 📊 **仪表盘** | 学习统计概览（文档数、知识点、待复习） |
| 📚 **知识库** | 文档卡片展示，拖拽排序，暗色玻璃态设计 |
| 💬 **聊天** | 基于知识库的 RAG 对话，流式输出 |
| 🧠 **学习** | 知识点 AI 解释 + 自我评估 + SM-2 复习 |
| 📝 **练习** | AI 自动出题（选择/判断/填空） |
| 📈 **分析** | 文档摘要、概念提取、掌握度报告 |
| ⚙️ **设置** | LLM 提供者切换（DeepSeek / Claude / OpenAI） |

### 🔧 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | - |
| `DEEPSEEK_MODEL` | DeepSeek 模型名 | `deepseek-chat` |
| `CLAUDE_API_KEY` | Claude API 密钥 | - |
| `CLAUDE_MODEL` | Claude 模型名 | `claude-sonnet-4-20250514` |
| `OPENAI_API_KEY` | OpenAI API 密钥 | - |
| `OPENAI_MODEL` | OpenAI 模型名 | `gpt-4o` |
| `PORT` | 运行端口 | `5000` |

### 🧪 运行测试

```bash
pytest tests/ -v
```

### 🤝 贡献

欢迎 Issue 和 PR！请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

### 📄 许可证

[MIT License](LICENSE)

---

<a name="english"></a>

## 📖 English — RAG + SM-2 AI Learning Assistant

**Panda Learn** is an open-source AI-powered learning assistant built on RAG (Retrieval-Augmented Generation) and the SM-2 spaced repetition algorithm. Upload PDFs/docs, AI auto-extracts knowledge points, generates quizzes, and schedules reviews. Supports DeepSeek / Claude / GPT.

### ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **Smart Knowledge Base** | Upload PDF/TXT/MD/HTML — auto-chunk, embed, and index |
| 💬 **RAG Q&A** | Semantic search + LLM generation with source citations |
| 🧠 **Knowledge Extraction** | AI automatically extracts key concepts from documents |
| 🔄 **Spaced Repetition** | SM-2 algorithm-based optimal review scheduling |
| 📝 **Quiz Generation** | AI generates multiple-choice, true/false, fill-in-blank questions |
| 📊 **Mastery Tracking** | Multi-signal assessment (time + practice + stability) |
| 🎯 **Learning Reports** | Weak point identification and progress visualization |
| 🔌 **Multi-LLM** | DeepSeek (default) / Claude / OpenAI — switch freely |
| 🐼 **Panda UI** | Dark glassmorphism design with pixel panda mascot |

### 🚀 Quick Start

#### Docker (recommended)

```bash
git clone https://github.com/dz1996511-maker/panda-learn.git
cd panda-learn
echo "DEEPSEEK_API_KEY=your_key_here" > .env
docker compose up -d
# Open http://localhost:5000
```

#### Manual

```bash
git clone https://github.com/dz1996511-maker/panda-learn.git
cd panda-learn
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
echo "DEEPSEEK_API_KEY=your_key_here" > .env
python -m app
# Open http://localhost:5000
```

### 🧪 Run Tests

```bash
pytest tests/ -v
```

### 📄 License

[MIT](LICENSE)

---

<div align="center">
Made with ❤️ and 🐼
</div>
