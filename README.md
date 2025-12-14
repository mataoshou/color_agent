# Qwen Chat Agent

<div align="center">

**基于 LangChain 框架的智能 AI 对话助手**

一个功能强大的桌面应用程序，提供流畅的 AI 对话体验，支持文件操作、会话管理和多模型切换

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.5+-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-orange.svg)](https://python.langchain.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📖 项目简介

Qwen Chat Agent 是一个基于 LangChain 框架构建的现代化 AI 对话系统，采用 PyQt6 打造友好的桌面图形界面。系统通过 OpenAPI 协议连接远程 AI 模型服务，支持多轮对话、智能文件操作、会话持久化等功能，为用户提供类似专业 IDE 的 AI 助手体验。

### 核心特点

- **🎯 零配置启动**：首次运行自动引导配置，快速上手
- **🔌 多模型支持**：兼容 OpenAI、Azure OpenAI 及任何 OpenAPI 兼容服务
- **🔄 热切换**：模型、主题、工作目录无需重启即可切换
- **💾 智能会话管理**：自动保存对话历史，支持多会话并行
- **📁 文件操作集成**：AI 可自主读取、修改和管理文件
- **🎨 现代化界面**：流畅的流式响应、明暗主题、工具调用可视化

---

## ✨ 功能特性

### 🤖 智能对话系统

- **流式响应显示**：实时展示 AI 生成内容，无需等待完整响应
- **多轮对话记忆**：基于 LangChain Memory 的上下文管理
- **工具调用可视化**：清晰展示 AI 调用工具的过程和结果
- **系统上下文注入**：自动提供工作目录、操作系统等环境信息

### 🔧 模型配置管理

- **多模型配置**：支持添加和管理多个 OpenAPI 模型
- **灵活切换**：运行时动态切换模型，保留会话历史
- **参数调节**：可调节温度（0.0-2.0）和最大 token 数（512-4096）
- **连接状态监控**：实时显示模型连接状态和错误提示

### 💬 会话管理

- **多会话支持**：创建和管理多个独立对话会话
- **自动保存**：对话内容实时持久化到本地
- **会话预览**：侧边栏显示会话名称、时间和最新消息
- **会话回滚**：支持回滚到历史消息，重新生成响应
- **会话导出**：JSON 格式存储，易于备份和迁移

### 📁 文件操作工具

- **可视化文件浏览器**：树形结构展示工作目录文件
- **AI 文件操作**：AI 可自主调用工具读取、写入和修改文件
- **拖拽支持**：拖拽文件到对话区域快速处理
- **右键菜单**：快捷操作"让 AI 阅读"和"让 AI 修改"
- **安全控制**：文件大小限制、格式检查、路径验证

### 📝 文本处理辅助

- **快捷操作**：润色、扩写、缩写、翻译等一键处理
- **浮动工具栏**：选中文本时自动显示操作按钮
- **文本对比视图**：分屏展示修改前后的差异
- **模板填充**：预设提示模板快速应用

### 🎨 用户界面

- **三栏布局**：会话列表、聊天区域、文件浏览器
- **明暗主题**：支持 Light 和 Dark 两种主题风格
- **响应式设计**：可调整面板大小，适应不同屏幕
- **键盘快捷键**：Ctrl+N 新建会话、Ctrl+S 保存、Ctrl+Enter 发送
- **状态栏**：实时显示当前模型、工作目录和系统状态

### 🛡️ 错误处理与日志

- **友好错误提示**：清晰的错误对话框和解决建议
- **自动重试机制**：网络错误时提供重试选项
- **详细日志记录**：所有关键操作记录到日志文件
- **日志查看器**：内置日志查看窗口，方便问题排查
- **系统通知**：非阻塞式通知消息，不干扰工作流程

---

## 🚀 快速开始

### 系统要求

- **Python**：3.9 或更高版本
- **操作系统**：macOS 10.15+、Windows 10/11、Linux 主流发行版
- **网络**：需要访问 OpenAPI 模型服务（如 OpenAI API）

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/yourusername/qwen-chat-agent.git
cd qwen-chat-agent
```

#### 2. 运行安装脚本

**macOS / Linux**

```bash
bash scripts/install.sh
```

**Windows**

```cmd
scripts\install.bat
```

安装脚本会自动完成以下操作：
- ✅ 检查 Python 版本
- ✅ 创建虚拟环境
- ✅ 安装所有依赖包
- ✅ 创建必要的目录结构
- ✅ 生成默认配置文件

### 启动应用

**macOS / Linux**

```bash
bash scripts/run.sh
```

**Windows**

```cmd
scripts\run.bat
```

### 首次配置

首次启动时，应用会引导您完成初始配置：

1. **添加模型配置**
   - 选择模型类型（OpenAI、Azure OpenAI 或自定义）
   - 填写 API 端点 URL
   - 输入 API 密钥
   - 指定模型标识符（如 `gpt-4`、`gpt-3.5-turbo`）

2. **设置工作目录**
   - 选择您希望 AI 访问的工作目录
   - 可以随时在文件浏览器中更改

3. **开始对话**
   - 点击"新建会话"创建第一个对话
   - 在输入框中输入消息并发送

---

## 📸 截图和演示

### 主界面

```
┌─────────────────────────────────────────────────────────────┐
│  [新建会话] [设置] [模型管理] [主题切换]                      │
├──────────┬──────────────────────────────────┬───────────────┤
│ 会话列表  │        聊天区域                   │  文件浏览器    │
│          │                                  │               │
│ 📝 项目讨论│  User: 帮我分析这个文件          │  📁 src       │
│ 📝 代码审查│  ┌──────────────────────────┐   │  📁 docs      │
│ 📝 文档编写│  │ AI: 我来帮你分析...       │   │  📄 README.md │
│          │  │ [工具调用: ReadFileTool]  │   │  📄 main.py   │
│          │  └──────────────────────────┘   │               │
│          │  [输入消息...]          [发送]   │               │
├──────────┴──────────────────────────────────┴───────────────┤
│  模型: GPT-4 | 工作目录: /project | 状态: 就绪               │
└─────────────────────────────────────────────────────────────┘
```

### 核心功能演示

**1. 流式响应**
- AI 回复实时逐字显示，提供流畅的对话体验
- 显示"正在输入"动画，清晰的状态反馈

**2. 工具调用可视化**
- 特殊样式展示 AI 调用的工具（读取文件、修改文件等）
- 显示工具名称、参数和执行结果

**3. 文件操作**
- 右键点击文件选择"让 AI 阅读"或"让 AI 修改"
- 拖拽文件到对话区域快速处理
- AI 自动调用文件工具完成操作

**4. 会话管理**
- 侧边栏展示所有会话，显示名称和预览
- 点击切换会话，历史消息自动加载
- 右键菜单支持重命名和删除

**5. 模型切换**
- 在设置中选择不同的模型配置
- 无需重启，立即生效
- 保留当前会话历史

---

## 📁 项目结构

```
qwen-chat-agent/
├── src/                            # 源代码目录
│   ├── main.py                     # 应用程序入口
│   ├── gui/                        # PyQt6 GUI 组件
│   │   ├── main_window.py          # 主窗口
│   │   ├── chat_widget.py          # 聊天界面
│   │   ├── message_bubble.py       # 消息气泡
│   │   ├── session_sidebar.py      # 会话侧边栏
│   │   ├── file_browser.py         # 文件浏览器
│   │   ├── settings_dialog.py      # 设置对话框
│   │   └── ...                     # 其他 GUI 组件
│   ├── backend/                    # LangChain 后端
│   │   ├── agent/                  # Agent 执行器
│   │   ├── tools/                  # 文件操作工具
│   │   └── memory/                 # 会话记忆
│   ├── services/                   # 业务服务层
│   │   ├── application_controller.py   # 应用控制器
│   │   ├── model_config_manager.py     # 模型配置管理
│   │   ├── session_manager.py          # 会话管理
│   │   └── system_context.py           # 系统上下文
│   ├── workers/                    # QThread 工作线程
│   │   └── chat_worker.py          # 聊天工作线程
│   ├── utils/                      # 工具函数
│   │   ├── config.py               # 配置管理
│   │   ├── logger.py               # 日志工具
│   │   └── errors.py               # 错误定义
│   └── resources/                  # 资源文件
│       └── styles/                 # QSS 样式表
├── docs/                           # 文档目录
│   ├── USER_GUIDE.md               # 用户使用指南
│   ├── DEVELOPER_GUIDE.md          # 开发者文档
│   └── API.md                      # API 文档
├── scripts/                        # 脚本目录
│   ├── install.sh                  # 安装脚本（macOS/Linux）
│   ├── install.bat                 # 安装脚本（Windows）
│   ├── run.sh                      # 运行脚本（macOS/Linux）
│   └── run.bat                     # 运行脚本（Windows）
├── sessions/                       # 会话存储目录
├── logs/                           # 日志目录
├── tests/                          # 测试目录
├── config.yaml                     # 配置文件
├── requirements.txt                # Python 依赖
└── README.md                       # 项目说明
```

---

## 🔧 配置说明

### 配置文件（config.yaml）

应用的所有配置存储在 `config.yaml` 文件中，首次启动时自动生成。

**主要配置项：**

```yaml
# 模型配置
active_model_id: "model_001"
models:
  model_001:
    name: "OpenAI GPT-4"
    api_base: "https://api.openai.com/v1"
    api_key: "your-api-key-here"
    model_name: "gpt-4"
    description: "OpenAI GPT-4 模型"

# LangChain 配置
temperature: 0.7          # 温度参数（0.0-2.0）
max_tokens: 2048          # 最大 token 数
streaming: true           # 启用流式响应

# 工作目录
working_directory: "."    # 当前工作目录

# 会话配置
session:
  storage_path: "./sessions"
  auto_save: true
  max_history: 100

# UI 配置
ui:
  theme: "light"          # 主题：light 或 dark
  window_width: 1200
  window_height: 800

# 日志配置
logging:
  level: "INFO"
  file: "./logs/agent.log"
```

### 添加新模型

1. 打开设置对话框（工具栏 → 设置）
2. 点击"添加模型"按钮
3. 填写模型信息：
   - **模型名称**：显示名称（如 "GPT-4"）
   - **API 端点**：API 基础 URL（如 `https://api.openai.com/v1`）
   - **API 密钥**：您的 API 密钥
   - **模型标识符**：模型 ID（如 `gpt-4`、`gpt-3.5-turbo`）
4. 点击"保存"完成添加

### 支持的模型服务

- **OpenAI**：`https://api.openai.com/v1`
- **Azure OpenAI**：`https://your-resource.openai.azure.com/`
- **自定义服务**：任何兼容 OpenAPI 协议的服务

---

## 📚 文档

- **[用户使用指南](docs/USER_GUIDE.md)**：详细的功能说明和操作指南
- **[开发者文档](docs/DEVELOPER_GUIDE.md)**：架构设计和开发指南
- **[API 文档](docs/API.md)**：主要类和方法的 API 说明

---

## 🧪 测试

运行测试套件：

```bash
# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_tools.py
python -m pytest tests/test_session_manager.py
```

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 开发环境搭建

1. Fork 本项目
2. 克隆您的 Fork：`git clone https://github.com/your-username/qwen-chat-agent.git`
3. 创建特性分支：`git checkout -b feature/your-feature`
4. 运行安装脚本：`bash scripts/install.sh`
5. 进行开发和测试
6. 提交更改：`git commit -am 'Add some feature'`
7. 推送到分支：`git push origin feature/your-feature`
8. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 代码风格
- 使用类型提示（Type Hints）
- 编写清晰的文档字符串
- 为新功能添加测试
- 保持函数和方法的单一职责

---

## 🐛 问题反馈

如果您遇到问题或有建议，请通过以下方式反馈：

- **GitHub Issues**：[提交 Issue](https://github.com/yourusername/qwen-chat-agent/issues)
- **讨论区**：[GitHub Discussions](https://github.com/yourusername/qwen-chat-agent/discussions)

提交 Issue 时，请包含：
- 问题描述
- 复现步骤
- 系统环境（操作系统、Python 版本）
- 错误日志（位于 `logs/agent.log`）

---

## 📋 常见问题

### Q: 如何获取 OpenAI API 密钥？

A: 访问 [OpenAI Platform](https://platform.openai.com/) 注册账号并创建 API 密钥。

### Q: 支持本地模型吗？

A: 目前仅支持通过 OpenAPI 协议访问的远程模型。如果您的本地模型提供 OpenAPI 兼容接口（如 Ollama、LocalAI），可以配置使用。

### Q: 会话数据存储在哪里？

A: 所有会话数据以 JSON 格式存储在 `sessions/` 目录下，每个会话有独立的子目录。

### Q: 如何备份会话？

A: 直接复制 `sessions/` 目录即可备份所有会话数据。

### Q: 模型切换会丢失对话历史吗？

A: 不会。切换模型时会保留当前会话的所有历史消息，您可以继续对话。

### Q: 文件操作有什么限制？

A: 为了安全，系统限制：
- 文件大小不超过 10MB
- 仅允许访问工作目录内的文件
- 支持常见文本格式（.txt、.py、.md 等）

---

## 🗺️ 路线图

### 已完成 ✅

- [x] 基础架构和项目初始化
- [x] OpenAPI 模型配置管理
- [x] LangChain Agent 和 Tools 集成
- [x] 会话管理功能
- [x] 聊天界面和流式响应
- [x] 文件浏览器和操作
- [x] 设置对话框和主题切换
- [x] 错误处理和通知系统
- [x] 完整文档和安装脚本

### 计划中 🚧

- [ ] 插件系统支持
- [ ] 更多 LangChain Tools（网络搜索、代码执行等）
- [ ] 会话导出为 Markdown
- [ ] 语音输入支持
- [ ] 多语言界面
- [ ] 云端会话同步

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

```
MIT License

Copyright (c) 2024 Qwen Chat Agent Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 致谢

本项目基于以下优秀的开源项目构建：

- [LangChain](https://python.langchain.com/) - LLM 应用开发框架
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - Python Qt 绑定
- [OpenAI](https://openai.com/) - AI 模型服务

感谢所有贡献者的支持！

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个 Star！**

[报告问题](https://github.com/yourusername/qwen-chat-agent/issues) · [功能建议](https://github.com/yourusername/qwen-chat-agent/discussions) · [贡献代码](https://github.com/yourusername/qwen-chat-agent/pulls)

</div>
