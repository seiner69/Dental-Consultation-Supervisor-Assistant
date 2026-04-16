# 🦷 智齿·口腔咨询管家 (DCSA)

> **AI 驱动的口腔门诊咨询质检系统 — 让每一次沟通都可量化、可追溯、可优化**

[![架构](https://img.shields.io/badge/架构-六边形-blue)]()
[![状态](https://img.shields.io/badge/状态-生产就绪-green)]()

---

## 📖 项目简介

智齿·口腔咨询管家是一款垂直领域的 AI 质检系统，专为口腔门诊设计。系统通过 **ASR 语音识别**（阿里云 SenseVoice）和 **LLM 大模型**（通义千问 Qwen-Plus）将咨询录音转化为结构化的业务洞察，聚焦**合规性检查**、**客户痛点挖掘**和**销售转化分析**。

### 核心价值

| 角色 | 痛点 | 我们的解决方案 |
|------|------|----------------|
| 门诊主管 | 难以批量检查咨询师质量 | AI 全量质检，每通录音都有评分报告 |
| 咨询师 | 不知道自己哪里说错了 | 具体到话术级别的改进建议 |
| 老板 | 咨询转化率低但找不到原因 | 成交率与评分的关联分析 |

---

## ✨ 核心功能

- **🧠 AI 智能分析** — 基于医学销售金牌标准，对咨询录音进行 0-100 分评分
- **🎯 痛点精准识别** — 自动发现客户最关心的问题（怕痛、嫌贵、不信任等）
- **💡 话术改进建议** — 指出咨询师的失误点，给出具体可落地的话术优化方案
- **📊 监管看板** — 主管可查看所有咨询记录、成交率、评分分布，筛选高危预警单
- **🔒 数据安全** — 所有数据本地存储，录音上传 OSS 需签名 URL，防泄露
- **🛠️ 模拟测试模式** — 无需消耗 API 额度即可完整体验所有功能

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                      UI 层 (Streamlit)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │  咨询师工作台  │  │   主管监管端   │  │     数据展示      │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                    业务逻辑层 (src/core)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │  ASR 语音识别  │  │  LLM 分析引擎  │  │   数据模型验证    │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                    数据层 (src/database)                  │
│              ConsultationRepository (CSV)                 │
├─────────────────────────────────────────────────────────┤
│                    外部服务                              │
│     阿里云 OSS (录音存储)  ·  通义千问 (LLM + ASR)        │
└─────────────────────────────────────────────────────────┘
```

### 技术栈

| 类别 | 技术 |
|------|------|
| 前端 | Streamlit |
| LLM | LangChain + DashScope (Qwen-Plus) |
| ASR | 阿里云 SenseVoice (paraformer-v1) |
| 存储 | 阿里云 OSS + CSV 本地文件 |
| 数据验证 | Pydantic v2 |
| 数据分析 | Pandas |

---

## 🚀 快速开始

### 1. 环境要求

- Python 3.10+
- 阿里云账号（开通 DashScope 和 OSS 服务）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件：

```env
# 阿里云 DashScope (LLM + ASR)
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx

# 阿里云 OSS
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OSS_ENDPOINT=http://oss-cn-shenzhen.aliyuncs.com
OSS_BUCKET_NAME=your_bucket_name
```

### 4. 启动应用

```bash
streamlit run src/ui/dashboard.py
```

启动后访问 `http://localhost:8501`

### 5. 使用模拟模式（免配置）

默认开启**模拟数据模式**，无需配置 API 密钥即可体验完整功能：

- 自动生成测试对话文本
- AI 分析返回预设的评分报告
- 所有数据保存在本地 CSV

---

## 📁 项目结构

```
Dental Consultation Supervisor Assistant/
├── config/
│   └── settings.py          # 配置管理（从 .env 加载）
├── src/
│   ├── core/
│   │   ├── asr_client.py     # ASR 语音识别客户端
│   │   ├── llm_engine.py     # LLM 分析引擎
│   │   └── models.py         # Pydantic 数据模型
│   ├── database/
│   │   └── repository.py     # 数据持久化（CSV）
│   └── ui/
│       └── dashboard.py      # Streamlit 主界面
├── data/
│   ├── db/
│   │   └── dental_consultation_db.csv  # 咨询记录数据库
│   └── raw_audio/            # 原始录音文件
├── tests/
│   ├── test_core.py          # 核心模块单元测试
│   └── sanity_check.py       # 系统自检脚本
├── .env                       # 环境变量（勿提交到 Git）
├── .gitignore
├── requirements.txt
└── run_test.py               # 测试入口
```

---

## 🔧 扩展开发

### 添加新的分析维度

1. 在 `src/core/models.py` 中的 `ConsultationReport` 添加新字段
2. 修改 `src/core/llm_engine.py` 中的 system_prompt，指示 LLM 输出新字段
3. 更新 `src/database/repository.py` 中的表头定义

### 更换 ASR 服务

修改 `src/core/asr_client.py` 中的 `transcribe()` 方法，替换为其他 ASR 服务商的 SDK

---

## ⚠️ 注意事项

- `.env` 文件包含敏感密钥，**请勿提交到 Git 仓库**
- 录音文件建议使用 m4a 或 wav 格式
- CSV 数据库文件会随使用不断增大，可定期归档

---

## 📄 开源协议

MIT License

---

## 👤 作者

GitHub: [seiner69](https://github.com/seiner69)
