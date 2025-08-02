# AI智能研究助手 🤖

一个基于AI的智能研究助手，能够针对给定的研究任务或主题，通过联网搜索生成包含最新信息来源的研究报告。

## ✨ 功能特性

- 🔍 **智能搜索**: 基于给定主题进行深度网络搜索
- 📊 **信息整合**: 自动整合和整理搜索结果
- 📝 **报告生成**: 生成结构化的研究报告
- 🌐 **实时信息**: 获取最新的研究信息和数据
- 🎯 **精准定位**: 针对特定研究领域进行定向搜索
- 💬 **多轮对话**: 支持深度追问和连续对话
- 📈 **会话管理**: 完整的对话历史记录和统计
- 🗂️ **数据导出**: 支持对话历史导出为JSON格式
- 📄 **Word文档导出**: 支持将研究结果导出为.docx格式
- 🔒 **SSL安全配置**: 内置SSL配置，提高数据传输安全性
- 📚 **学术搜索**: 集成Arxiv学术论文搜索工具
- 💹 **财经数据**: 集成Yahoo Finance财经新闻工具
- 🇨🇳 **国产大模型**: 支持SiliconFlow平台，使用Qwen3-235B模型

## 🆕 版本说明

### 最新优化版本 (v2.0)
- **文件**: `app_gradio.py` + `conversation_manager.py` + `agent_core.py`
- **特点**: 
  - 更清晰的代码结构和注释
  - 改进的UI设计，使用Glass主题
  - 优化的会话管理和计时功能
  - 更好的错误处理和日志记录
  - 支持自定义数据目录导出
  - **新增Word文档导出功能** - 一键导出研究结果为.docx格式
  - **新增SSL安全配置** - 提高数据传输安全性
  - **新增多工具集成** - Yahoo Finance财经数据 + Arxiv学术搜索
  - **新增国产大模型支持** - SiliconFlow平台 + Qwen3-235B模型
  - **增强会话统计** - 详细的处理时间、错误统计等
  - **新增测试文件** - 完善的功能测试和验证

## 🛠️ 技术栈

- **后端框架**: FastAPI + Gradio
- **AI模型**: OpenAI GPT + SiliconFlow Qwen3-235B + LangChain
- **搜索引擎**: Tavily API + Yahoo Finance + Arxiv
- **文档处理**: pypandoc (Markdown转Word)
- **包管理**: uv (快速Python包管理器)
- **环境管理**: Conda
- **安全配置**: SSL/TLS支持

## 📋 系统要求

- Python 3.11+
- Conda 或 Miniconda
- 稳定的网络连接
- Pandoc (用于Word文档导出)

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/XploreXing/AI-Research-Assistant.git
cd AI-Research-Assistant/backend
```

### 2. 环境配置

```bash
# 创建虚拟环境
conda create -n ai-research python=3.11

# 激活虚拟环境
conda activate ai-research

# 安装uv包管理器
pip install uv
```

### 3. 安装依赖

```bash
# 使用uv安装依赖（推荐，速度更快）
uv pip install -r requirements.txt

# 或者使用传统pip
pip install -r requirements.txt
```

### 4. 安装Pandoc (用于Word文档导出)

#### 方法一：使用pypandoc_binary（推荐）
```bash
# 安装包含pandoc的完整包（推荐方式）
pip install pypandoc_binary
```

#### 方法二：手动安装pandoc
```bash
# macOS
brew install pandoc

# Ubuntu/Debian
sudo apt-get install pandoc

# Windows
# 从 https://pandoc.org/installing.html 下载安装包

# 然后安装pypandoc
pip install pypandoc
```

#### 方法三：仅安装pypandoc（需要手动安装pandoc）
```bash
# 如果你已经手动安装了pandoc，只需要安装pypandoc
pip install pypandoc
```

> 💡 **推荐使用方法一**：`pypandoc_binary` 包含了pandoc二进制文件，无需额外安装pandoc，是最简单的安装方式。

### 5. 配置环境变量

复制环境变量模板文件：
```bash
cp env.example .env
```

编辑 `.env` 文件，填入你的API密钥：
```env
OPENAI_API_KEY="your_openai_api_key_here"
TAVILY_API_KEY="your_tavily_api_key_here"
SILICONFLOW_API_KEY="your_siliconflow_api_key_here"
```

### 6. 启动应用

```bash
# 启动Gradio界面
python app_gradio.py
```

## 📖 使用方法

1. 启动应用后，在浏览器中打开显示的地址（通常是 `http://localhost:7860`）
2. 在输入框中输入你的研究主题或问题
3. 点击提交，等待AI助手生成研究报告
4. 查看生成的研究报告，包含最新的信息来源和详细分析
5. 使用追问功能进行深度对话
6. 查看对话历史和统计信息
7. **使用Word导出功能** - 点击"📄 导出为Docx"按钮将研究结果导出为Word文档

## 🔧 配置说明

### API密钥获取

本项目需要以下API密钥，请按需注册获取并填写到`.env`文件中：

- **OpenAI API**  
  用途：用于调用GPT等大模型，生成内容和对话。  
  获取方式：访问 [OpenAI Platform](https://platform.openai.com/) 注册并获取API密钥。

- **Tavily API**  
  用途：用于联网搜索，获取最新的网页和信息。  
  获取方式：访问 [Tavily](https://tavily.com/) 注册并获取API密钥。

- **SiliconFlow API（硅基流动）**  
  用途：调用多种国产大模型，体验丰富的AI能力。  
  获取方式：访问 [SiliconFlow](https://siliconflow.com/) 注册并获取API密钥。  
  推荐福利：  
  - 通过我的专属邀请注册链接 [https://cloud.siliconflow.cn/i/SV01waIi](https://cloud.siliconflow.cn/i/SV01waIi) 注册新用户，即可免费获得2000万 tokens！  
  - 你可以在硅基流动平台上体验多种大模型，足够充分体验和享受本AI研究助手的全部功能。

> ⚠️ 温馨提示：API密钥属于个人隐私信息，请妥善保管，避免泄露。

## 📁 项目结构

```
backend/
├── main.py                    # FastAPI主应用
├── app_gradio.py             # Gradio界面应用
├── agent_core.py             # AI助手核心逻辑
├── conversation_manager.py    # 对话管理器
├── ssl_config.py             # SSL配置
├── requirements.txt          # Python依赖
├── env.example               # 环境变量模板
├── data/                     # 对话导出数据目录
│   └── generated_reports/    # Word文档导出目录
└── README.md                # 项目说明文档
```

## 🆕 新功能详解

### 📄 Word文档导出
- 支持将研究结果和追问回答合并导出为.docx格式
- 自动生成带时间戳的文件名
- 保存在`data/generated_reports/`目录下

### 🔒 SSL安全配置
- 内置SSL配置模块，提高数据传输安全性
- 支持HTTPS连接，保护API密钥和用户数据

### 📚 多工具集成
- **Yahoo Finance**: 获取最新财经新闻和股票数据
- **Arxiv**: 搜索学术论文和研究报告
- **Tavily**: 通用网页搜索和信息获取

### 🇨🇳 国产大模型支持
- 集成SiliconFlow平台
- 使用Qwen3-235B大模型
- 提供更丰富的AI能力选择

### 📊 增强会话统计
- 详细的处理时间统计
- 错误轮次统计
- 会话活动时间记录
- 平均响应时间计算

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

1. Fork 这个项目
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

⭐ 如果这个项目对你有帮助，请给它一个星标！ 