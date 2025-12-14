# Design Document

## Overview

本文档描述了基于 LangChain 框架的 AI 对话 agent 系统的技术设计。该系统使用 PyQt6 构建桌面应用程序前端，后端以 LangChain 架构为核心，通过 OpenAPI 协议连接远程 AI 模型服务，支持模型配置管理、多轮对话、会话管理、文件操作和文本处理等功能。

### 技术栈

**核心框架：**
- Python 3.9+
- PyQt6（跨平台桌面 GUI 前端）
- LangChain（后端核心架构：Agent、Tool、Memory、Chain）
- LangChain-OpenAI（OpenAPI 模型集成）
- PyYAML（配置管理）
- Requests（HTTP 客户端）

**平台支持：**
- macOS 10.15+
- Windows 10/11
- Linux 主流发行版


## Architecture

系统采用前后端分离的桌面应用架构设计，前端使用 PyQt6 构建 GUI，后端以 LangChain 为核心架构：

```
┌─────────────────────────────────────────────────────────┐
│              Frontend Layer (PyQt6)                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │  QMainWindow (主窗口)                             │  │
│  │  ┌────────┬──────────────────┬────────────────┐  │  │
│  │  │Session │   Chat Widget    │  File Browser  │  │  │
│  │  │List    │   (QListWidget)  │  (QTreeView)   │  │  │
│  │  └────────┴──────────────────┴────────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓ (Qt Signals/Slots)
┌─────────────────────────────────────────────────────────┐
│              Application Controller                     │
│  (连接前端 GUI 和后端 LangChain 架构)                   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│         Backend Layer (LangChain 核心架构)              │
│  ┌──────────────────────────────────────────────────┐  │
│  │  LangChain Agent (ReAct/OpenAI Functions)        │  │
│  │    ├─ ChatOpenAI (OpenAPI Model 集成)            │  │
│  │    ├─ ConversationBufferMemory (会话记忆)        │  │
│  │    └─ AgentExecutor (工具调用执行器)             │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  LangChain Tools                                 │  │
│  │    ├─ ReadFileTool (文件读取)                    │  │
│  │    ├─ WriteFileTool (文件写入)                   │  │
│  │    ├─ ModifyFileTool (文件修改)                  │  │
│  │    └─ ListFilesTool (文件列表)                   │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Service Layer                                   │  │
│  │    ├─ ModelConfigManager (模型配置管理)          │  │
│  │    ├─ SessionManager (会话持久化)                │  │
│  │    └─ SystemContextProvider (系统上下文)         │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              External Services                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  OpenAPI Model Services (远程 AI 模型)           │  │
│  │    ├─ OpenAI API                                 │  │
│  │    ├─ Azure OpenAI                               │  │
│  │    ├─ 自定义 OpenAPI 兼容服务                     │  │
│  │    └─ 其他 OpenAPI 兼容模型                       │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 核心设计原则

1. **LangChain 为核心**: 后端完全基于 LangChain 架构，使用 Agent、Tool、Memory、Chain 等组件
2. **前后端分离**: GUI 和业务逻辑分离，使用 Qt 信号槽机制通信
3. **OpenAPI 集成**: 通过 LangChain-OpenAI 集成远程模型服务，支持多种 OpenAPI 兼容服务
4. **模块化**: 各功能模块独立，便于测试和维护
5. **多线程**: 使用 QThread 处理耗时操作，避免阻塞 UI
6. **可配置**: 支持配置多个 OpenAPI 模型，灵活切换


## Components and Interfaces

### 1. GUI Components (PyQt6)

#### 主要组件
- **MainWindow**: 主窗口，整合所有 UI 组件
- **ChatWidget**: 聊天界面，显示消息和输入框
- **SessionSidebar**: 会话列表侧边栏
- **FileBrowser**: 文件浏览器
- **ModelManagerDialog**: 模型管理对话框
- **SettingsDialog**: 设置对话框

### 2. Backend Layer Components (LangChain 核心)

#### LangChain Agent
- **AgentExecutor**: LangChain 的 Agent 执行器，负责工具调用和响应生成
- **ChatOpenAI**: LangChain 的 OpenAI 模型集成，支持 OpenAPI 协议
- **ConversationBufferMemory**: LangChain 的会话记忆组件，管理对话历史
- **SystemMessagePromptTemplate**: 系统提示模板，包含工作目录和系统信息

#### Service Layer
- **ApplicationController**: 应用程序控制器，连接前端 GUI 和后端 LangChain
- **ModelConfigManager**: 模型配置管理器，管理多个 OpenAPI 模型配置
- **SessionManager**: 会话管理器，负责会话的创建、保存、加载和删除
- **SystemContextProvider**: 系统上下文提供者，提供工作目录、操作系统等信息

### 3. LangChain Tools

#### 文件操作工具
- **ReadFileTool**: 读取文件内容
- **WriteFileTool**: 创建或覆盖文件
- **ModifyFileTool**: 修改文件内容
- **ListFilesTool**: 列出目录文件


## Data Models

### Python Data Models

系统使用数据类（dataclass）定义核心数据模型：

**Message（消息模型）**
- role: 消息角色（'user' 或 'assistant'）
- content: 消息内容文本
- timestamp: 消息时间戳
- sequence_number: 消息序号

**Session（会话模型）**
- session_id: 会话唯一标识符
- name: 会话名称
- messages: 消息列表
- created_at: 创建时间
- updated_at: 最后更新时间
- metadata: 元数据字典

**ModelConfig（模型配置模型）**
- id: 模型唯一标识符
- name: 模型显示名称
- api_base: API 端点 URL
- api_key: API 密钥
- model_name: 模型标识符（如 "gpt-4"）
- description: 模型描述（可选）

**SystemContext（系统上下文模型）**
- working_directory: 当前工作目录路径
- os_type: 操作系统类型（'Darwin', 'Linux', 'Windows'）
- os_version: 操作系统版本
- python_version: Python 版本

**Settings（设置模型）**
- active_model_id: 当前激活的模型 ID
- temperature: 温度参数
- max_tokens: 最大 token 数
- working_directory: 工作目录
- theme: 主题（'light' 或 'dark'）

### 配置文件格式 (config.yaml)

配置文件采用 YAML 格式，包含以下主要部分：

**模型配置**
- active_model_id: 当前激活的模型 ID
- models: 模型配置字典，支持多个 OpenAPI 模型（不限制数量）
  - 每个模型包含：name（显示名称）、api_base（API 端点）、api_key（密钥）、model_name（模型标识符）、description（描述）

**LangChain 配置**
- temperature: 温度参数（默认 0.7）
- max_tokens: 最大 token 数（默认 2048）
- streaming: 是否启用流式响应（默认 true）
- verbose: 是否显示详细日志（默认 false）

**工作目录配置**
- working_directory: 当前工作目录（默认 "."）

**会话配置**
- storage_path: 会话存储路径（默认 "./sessions"）
- auto_save: 是否自动保存（默认 true）
- max_history: 最多保留的历史消息数（默认 100）

**文件操作配置**
- allowed_formats: 允许的文件格式列表
- max_file_size: 最大文件大小（默认 10MB）

**日志配置**
- level: 日志级别（默认 "INFO"）
- file: 日志文件路径（默认 "./logs/agent.log"）

**UI 配置**
- theme: 主题（'light' 或 'dark'，默认 'light'）
- window_width: 窗口宽度（默认 1200）
- window_height: 窗口高度（默认 800）


## System Initialization and Default Settings

### 默认配置

#### 1. 默认配置值

首次启动时，系统会创建包含以下默认值的配置文件：
- active_model_id: null（需要用户配置）
- models: {}（空字典，需要用户添加）
- temperature: 0.7
- max_tokens: 2048
- streaming: true
- working_directory: "."（当前目录）
- auto_save: true
- max_history: 100
- max_file_size: 10MB
- log_level: "INFO"
- theme: "light"
- window_width: 1200
- window_height: 800

#### 2. 首次启动流程

**场景 1: 完全首次启动（无配置文件）**
```
1. 创建默认 config.yaml
2. 创建 ./sessions/ 和 ./logs/ 目录
3. 显示"欢迎使用"对话框
4. 引导用户添加第一个模型配置
   - 提供常见模型模板（OpenAI、Azure、自定义）
   - 用户填写 API 端点、密钥、模型名称
5. 保存模型配置到 config.yaml
6. 初始化 LangChain Agent
7. 显示主界面，提示"点击新建会话开始对话"
```

**场景 2: 有配置文件但无模型**
```
1. 加载 config.yaml
2. 检测到 models 为空
3. 显示"添加模型"对话框
4. 引导用户添加模型配置
5. 初始化 LangChain Agent
6. 显示主界面
```

**场景 3: 正常启动（有配置和模型）**
```
1. 加载 config.yaml
2. 加载 active_model_id 对应的模型
3. 初始化 LangChain Agent
4. 加载会话列表
5. 显示主界面
6. 如果有最近会话，自动加载
```

#### 3. 配置验证和修复

系统启动时会验证配置的合理性并自动修复无效值：

**温度参数验证**
- 检查范围：0.0 - 2.0
- 无效时重置为：0.7

**max_tokens 验证**
- 检查范围：512 - 4096
- 无效时重置为：2048

**工作目录验证**
- 检查目录是否存在
- 不存在时重置为："."（当前目录）

**主题验证**
- 检查值是否为 'light' 或 'dark'
- 无效时重置为：'light'

**active_model_id 验证**
- 检查模型 ID 是否存在于 models 字典中
- 不存在时重置为：null

#### 4. 错误恢复机制

**配置文件损坏**
- 备份损坏的配置文件为 config.yaml.backup
- 创建新的默认配置文件
- 提示用户配置文件已重置

**会话文件损坏**
- 在会话列表中标记为"损坏"
- 不影响其他会话的加载
- 提供"尝试修复"选项

**模型连接失败**
- 显示错误对话框，说明失败原因
- 提供"重试"和"选择其他模型"选项
- 不阻止应用启动，用户可以修改配置后重试

## Data Flow and Integration

### 完整的用户交互流程

#### 1. 应用启动流程（含初始化和默认设置）
```
用户启动应用
    ↓
main.py 初始化
    ↓
检查 config.yaml 是否存在
    ├─ 存在：加载配置
    └─ 不存在：创建默认配置文件
        ├─ 默认工作目录：当前目录 "."
        ├─ 默认主题：light
        ├─ 默认温度：0.7
        ├─ 默认 max_tokens：2048
        └─ 模型列表：空（需要用户添加）
    ↓
检查是否有已配置的模型
    ├─ 有模型：加载 active_model_id 对应的模型
    └─ 无模型：显示"首次使用引导"对话框
        └─ 引导用户添加第一个模型配置
    ↓
初始化 SystemContextProvider
    ├─ 获取当前工作目录（从配置或默认当前目录）
    ├─ 获取操作系统类型和版本
    └─ 获取 Python 版本信息
    ↓
创建必要的目录结构
    ├─ ./sessions/（如果不存在）
    └─ ./logs/（如果不存在）
    ↓
初始化日志系统
    ├─ 设置日志级别（从配置读取，默认 INFO）
    ├─ 配置日志文件路径和轮转策略
    └─ 设置日志格式（时间戳、模块名、级别、消息）
    ↓
创建 MainWindow（前端 GUI）
    ↓
创建 ApplicationController（连接前后端）
    ↓
初始化 LangChain Agent（如果有可用模型）
    ├─ 创建 ChatOpenAI 实例
    ├─ 创建 LangChain Tools（文件操作）
    ├─ 创建 ConversationBufferMemory
    └─ 创建 AgentExecutor
    ↓
加载会话列表
    ├─ 扫描 ./sessions/ 目录
    ├─ 按更新时间排序
    └─ 显示在 SessionSidebar
    ↓
显示主界面
    ├─ 如果有最近会话：加载最近会话
    └─ 如果无会话：显示欢迎消息和"新建会话"提示
```

#### 2. 发送消息流程（核心功能串联）
```
用户在 ChatWidget 输入消息并点击发送
    ↓
ChatWidget 发出信号 → ApplicationController.on_send_message()
    ↓
ApplicationController 创建 ChatWorker (QThread)
    ↓
ChatWorker 准备系统上下文（SystemContextProvider）
    ├─ 当前工作目录
    ├─ 操作系统类型和版本
    └─ Python 版本
    ↓
ChatWorker 调用 LangChain AgentExecutor.run()
    ├─ 加载当前会话的 ConversationBufferMemory
    ├─ 注入系统上下文到 SystemMessage
    ├─ 通过 ChatOpenAI 发送请求到 OpenAPI Model
    └─ 如果需要，Agent 自动调用 LangChain Tools
        ├─ ReadFileTool（读取文件）
        ├─ WriteFileTool（写入文件）
        ├─ ModifyFileTool（修改文件）
        └─ ListFilesTool（列出文件）
    ↓
ChatWorker 发出信号：
    ├─ tool_call_started（工具调用开始）
    ├─ message_chunk（流式响应文本块）
    ├─ tool_call_finished（工具调用完成）
    └─ message_complete（消息生成完成）
    ↓
ApplicationController 接收信号并更新 GUI
    ├─ ChatWidget 显示流式响应
    ├─ ChatWidget 显示工具调用过程
    └─ StatusBar 更新状态
    ↓
SessionManager 自动保存会话到 JSON 文件
```

#### 3. 模型切换流程（热切换，无需重启）
```
用户在 SettingsDialog 选择新模型
    ↓
SettingsDialog 发出信号 → ApplicationController.on_model_changed()
    ↓
ApplicationController 调用 ModelConfigManager.get_model_config()
    ↓
销毁旧的 ChatOpenAI 实例
    ↓
创建新的 ChatOpenAI 实例（使用新的 api_base、api_key、model_name）
    ↓
重新创建 LangChain AgentExecutor（保留现有 Tools 和 Memory）
    ↓
更新 config.yaml 中的 active_model_id
    ↓
发出 model_switched 信号
    ↓
StatusBar 显示新模型名称
    ↓
用户可以立即使用新模型继续对话（无需重启程序）
```

#### 4. 工作目录切换流程
```
用户在 FileBrowser 点击"选择目录"按钮
    ↓
FileBrowser 显示 QFileDialog
    ↓
用户选择新目录
    ↓
FileBrowser 发出信号 → ApplicationController.on_directory_changed()
    ↓
SystemContextProvider 更新工作目录
    ↓
更新 config.yaml 配置文件
    ↓
FileBrowser 更新显示的文件树
    ↓
发出 working_directory_changed 信号
    ↓
下次对话时，系统上下文会包含新的工作目录信息
```

#### 5. 会话管理流程

**5.1 创建新会话**
```
用户点击"新建会话"按钮
    ↓
SessionSidebar 显示 QInputDialog（输入会话名称）
    ↓
用户输入会话名称（默认："新会话 - 时间戳"）
    ↓
SessionSidebar 发出信号 → ApplicationController.on_create_session(name)
    ↓
SessionManager 创建新会话
    ├─ 生成唯一 session_id（UUID）
    ├─ 创建会话目录：./sessions/{session_id}/
    ├─ 创建 metadata.json（会话名称、创建时间等）
    └─ 创建空的 messages.json
    ↓
创建新的 ConversationBufferMemory（空历史）
    ↓
发出 session_created 信号
    ↓
SessionSidebar 更新会话列表（新会话显示在顶部）
    ↓
ChatWidget 清空显示，准备新对话
    ↓
StatusBar 显示"新会话已创建"
```

**5.2 切换会话**
```
用户在 SessionSidebar 点击某个会话项
    ↓
SessionSidebar 发出信号 → ApplicationController.on_load_session(session_id)
    ↓
保存当前会话（如果有）
    ├─ SessionManager.save_session(current_session_id)
    ├─ 保存当前 ConversationBufferMemory 到 messages.json
    └─ 更新 metadata.json 的 updated_at 时间戳
    ↓
加载目标会话
    ├─ SessionManager.load_session(session_id)
    ├─ 读取 ./sessions/{session_id}/metadata.json
    ├─ 读取 ./sessions/{session_id}/messages.json
    └─ 解析消息历史
    ↓
创建新的 ConversationBufferMemory
    └─ 加载历史消息到 Memory
    ↓
发出 session_loaded 信号（包含 Session 对象）
    ↓
ChatWidget 清空当前显示
    ↓
ChatWidget 加载并显示历史消息
    ├─ 遍历 messages 列表
    ├─ 为每条消息创建 MessageBubble
    └─ 添加到 QListWidget
    ↓
SessionSidebar 高亮选中的会话项
    ↓
StatusBar 显示"已加载会话：{会话名称}"
```

**5.3 自动保存会话**
```
用户发送消息或收到 AI 响应
    ↓
消息添加到 ConversationBufferMemory
    ↓
触发自动保存（如果配置启用）
    ↓
SessionManager 保存会话到 JSON 文件
    ├─ 保存消息历史
    └─ 更新元数据（时间戳、消息数量）
    ↓
SessionSidebar 更新会话预览
```

**5.4 删除会话**
```
用户右键点击会话项，选择"删除会话"
    ↓
显示确认对话框
    ↓
用户确认后，SessionManager 删除会话目录和文件
    ↓
如果删除的是当前会话，清空界面并提示用户
    ↓
更新会话列表
```

**5.5 会话重命名**
```
用户右键点击会话项，选择"重命名"
    ↓
显示输入对话框（预填充当前名称）
    ↓
用户输入新名称后，SessionManager 更新元数据
    ↓
更新会话列表显示
```

#### 6. 文件操作流程（LangChain Tools）
```
用户请求："帮我读取 README.md 文件"
    ↓
消息发送到 LangChain Agent
    ↓
Agent 决定调用 ReadFileTool
    ↓
发出 tool_call_started 信号
    ↓
ReadFileTool 执行：
    ├─ 验证文件路径（在工作目录内）
    ├─ 检查文件大小（<10MB）
    ├─ 检查文件格式（在允许列表中）
    └─ 读取文件内容
    ↓
发出 tool_call_finished 信号
    ↓
ChatWidget 显示工具调用结果（特殊样式）
    ↓
Agent 将文件内容整合到响应中
    ↓
返回最终响应给用户
```

## Signal/Slot Communication

### Qt 信号槽机制

应用程序使用 Qt 的信号槽机制进行前后端通信。ApplicationController 作为中央控制器，定义以下信号：

**消息相关信号**
- message_chunk: 流式响应的文本块
- message_complete: 消息生成完成
- tool_call_started: 工具调用开始（携带工具名和参数）
- tool_call_finished: 工具调用完成（携带工具名和结果）

**模型相关信号**
- model_switched: 模型切换成功（携带模型名称）
- model_connection_failed: 模型连接失败（携带错误信息）

**会话相关信号**
- session_created: 会话创建（携带会话 ID）
- session_loaded: 会话加载（携带会话对象）
- session_saved: 会话保存（携带会话 ID）

**系统上下文相关信号**
- working_directory_changed: 工作目录变更（携带新路径）

**错误相关信号**
- error_occurred: 错误发生（携带错误信息）

### 信号槽连接方式

ApplicationController 在初始化时建立双向信号槽连接：

**GUI → Controller（用户操作）**
- 消息发送、会话创建/加载、目录变更、模型切换等用户操作信号连接到 Controller 的对应处理方法

**Controller → GUI（状态更新）**
- 消息流式响应、工具调用、模型切换、会话加载、错误提示等状态信号连接到 GUI 组件的更新方法


## Logging and Documentation Standards

### 日志规范

#### 1. 日志级别使用规范

系统使用 Python 标准 logging 模块，按以下级别记录日志：

**DEBUG 级别**
- 用途：详细的调试信息，用于开发和问题排查
- 示例：加载模型配置、系统上下文信息、详细的参数值

**INFO 级别**
- 用途：重要的业务流程信息
- 示例：应用启动成功、模型切换、会话创建/加载、消息发送

**WARNING 级别**
- 用途：警告信息，不影响正常运行但需要注意
- 示例：配置文件不存在、会话文件损坏、模型响应超时

**ERROR 级别**
- 用途：错误信息，影响功能但不导致崩溃
- 示例：模型连接失败、会话保存失败、文件操作失败（包含异常堆栈）

**CRITICAL 级别**
- 用途：严重错误，可能导致应用崩溃
- 示例：应用初始化失败、数据库损坏（包含异常堆栈）

#### 2. 关键操作日志记录

系统对所有关键操作进行详细日志记录，便于问题定位：

**应用生命周期**
- 启动和初始化过程（Python 版本、平台信息、配置加载）
- 模型切换操作（切换前后的模型、配置详情）
- 应用关闭和资源清理

**会话管理**
- 会话创建、加载、保存、删除操作
- 记录会话 ID、名称、消息数量、文件路径
- 操作成功或失败状态

**消息处理**
- 用户消息接收和 AI 响应生成
- 系统上下文注入
- 工具调用过程（工具名称、参数、结果）
- 消息处理耗时统计

**文件操作**
- 文件读取、写入、修改操作
- 文件路径、大小、格式验证
- 操作成功或失败（包含异常堆栈）

**错误处理**
- 异常发生位置和错误信息（包含堆栈）
- 重试操作记录
- 最终失败状态

#### 3. 日志格式配置

**日志格式**
- 时间戳：记录日志产生的时间
- 模块名：记录产生日志的模块
- 日志级别：DEBUG/INFO/WARNING/ERROR/CRITICAL
- 文件名和行号：记录日志产生的代码位置
- 消息内容：实际的日志信息

**日志输出**
- 文件输出：使用 RotatingFileHandler，单个文件最大 10MB，保留 5 个备份文件
- 控制台输出：同时输出到控制台，方便开发调试
- 编码：使用 UTF-8 编码，支持中文

**日志初始化**
- 在应用启动时配置日志系统
- 自动创建日志目录（如果不存在）
- 根据配置文件设置日志级别（默认 INFO）
- 记录日志系统初始化成功信息

### 代码注释规范

#### 1. 模块级注释

每个 Python 模块文件顶部应包含模块级文档字符串，说明：
- 模块名称和功能描述
- 主要类和功能列表
- 依赖的外部库
- 作者和日期信息

#### 2. 类级注释

每个类应包含类级文档字符串，说明：
- 类的职责和功能
- 主要属性及其类型和含义
- 使用示例
- 注意事项

#### 3. 方法级注释

每个公共方法应包含详细的文档字符串，说明：
- 方法的功能描述
- 参数列表（名称、类型、含义）
- 返回值（类型、含义）
- 可能抛出的异常
- 使用示例
- 特殊注意事项

#### 4. 复杂逻辑注释

对于复杂的业务逻辑，应添加行内注释说明：
- 每个主要步骤的目的
- 为什么这样实现
- 关键变量的含义
- 特殊处理的原因

示例：处理用户消息的方法应注释说明
- 步骤 1：准备系统上下文（包含工作目录、操作系统信息）
- 步骤 2：构建完整的 prompt（注入系统上下文）
- 步骤 3：调用 LangChain Agent（自动决定是否调用工具）
- 步骤 4：保存到会话历史（ConversationBufferMemory）
- 步骤 5：触发自动保存（持久化到磁盘）

#### 5. TODO 和 FIXME 注释

使用标准标记注释待办事项和问题：
- TODO：需要实现的功能
- FIXME：需要修复的问题
- NOTE：重要说明
- HACK：临时解决方案
- WARNING：警告信息

## Error Handling

### 错误分类

系统定义以下错误类型，所有错误都继承自基础错误类：

**AgentError（基础错误类）**
- 所有 Agent 相关错误的基类
- 包含错误消息和可选的原始异常
- 自动记录错误日志

**ModelError（模型相关错误）**
- 模型连接失败
- API 调用失败
- 响应解析失败
- 模型配置无效

**SessionError（会话相关错误）**
- 会话创建失败
- 会话加载失败
- 会话保存失败
- 会话文件损坏

**FileError（文件相关错误）**
- 文件读取失败
- 文件写入失败
- 文件权限错误
- 文件格式不支持


## UI/UX Design

### 布局设计

```
┌─────────────────────────────────────────────────────────────┐
│  Toolbar: [新建会话] [设置] [模型管理] [主题切换]            │
├──────────┬──────────────────────────────────┬───────────────┤
│ Session  │        Chat View                 │  File Browser │
│ Sidebar  │                                  │  [选择目录]   │
│          │  ┌────────────────────────────┐  │  ┌──────────┐ │
│ [+新建]  │  │ User: 你好                 │  │  │ 📁 src   │ │
│          │  │ ┌──────────────────────┐   │  │  │ 📁 docs  │ │
│ 📝会话1  │  │ │ AI: 你好！有什么可以  │   │  │  │ 📄 README│ │
│ 📝会话2  │  │ │ 帮助你的吗？          │   │  │  └──────────┘ │
│ 📝会话3  │  │ └──────────────────────┘   │  │               │
│          │  └────────────────────────────┘  │               │
│          │  ┌────────────────────────────┐  │               │
│          │  │ [输入消息...]        [发送]│  │               │
│          │  └────────────────────────────┘  │               │
├──────────┴──────────────────────────────────┴───────────────┤
│  Status Bar: 模型: OpenAI GPT-4 | 工作目录: /path/to/dir | 状态: 就绪 │
└─────────────────────────────────────────────────────────────┘
```

### 用户体验优化

系统从多个维度优化用户体验，确保流畅、友好的交互：

**响应式反馈**
- 用户操作后立即显示视觉反馈
- AI 响应流式显示，避免长时间等待
- 工具调用时显示进度提示
- 状态栏实时更新系统状态

**错误处理和恢复**
- 友好的错误提示对话框，说明原因和解决方案
- 网络错误时提供重试选项
- 模型连接失败时引导切换其他模型
- 应用崩溃后自动恢复会话状态

**操作便捷性**
- 键盘快捷键支持（Ctrl+N、Ctrl+S、Ctrl+Enter）
- 拖拽文件到对话区域
- 右键菜单快捷操作
- 完整的会话历史记录

**性能优化**
- 所有耗时操作异步处理，不阻塞 UI
- 智能缓存模型配置和会话列表
- 会话消息懒加载
- 输入框防抖处理

**视觉设计**
- 清晰的功能区域层次
- 统一的组件样式
- 明暗主题切换
- 工具调用过程可视化

**引导和帮助**
- 首次启动引导配置模型
- 空状态友好提示
- 鼠标悬停工具提示
- 日志查看功能


## Deployment

### 完整的项目目录结构

```
qwen-chat-agent/
├── src/                            # 源代码目录
│   ├── main.py                     # 应用程序入口，初始化 QApplication 和 MainWindow
│   │
│   ├── gui/                        # 前端 GUI 组件（PyQt6）
│   │   ├── __init__.py
│   │   ├── main_window.py          # 主窗口，整合所有 UI 组件
│   │   ├── chat_widget.py          # 聊天界面，显示消息和输入框
│   │   ├── message_bubble.py       # 消息气泡组件，区分用户和 AI 消息
│   │   ├── session_sidebar.py      # 会话列表侧边栏
│   │   ├── session_item.py         # 会话列表项组件
│   │   ├── file_browser.py         # 文件浏览器，显示文件树
│   │   ├── settings_dialog.py      # 设置对话框
│   │   ├── model_config_dialog.py  # 模型配置对话框（添加/编辑模型）
│   │   └── text_diff_viewer.py     # 文本对比视图
│   │
│   ├── backend/                    # 后端 LangChain 架构
│   │   ├── __init__.py
│   │   ├── agent/                  # LangChain Agent
│   │   │   ├── __init__.py
│   │   │   ├── agent_executor.py   # Agent 执行器，管理工具调用
│   │   │   └── prompts.py          # Prompt 模板，包含系统上下文
│   │   │
│   │   ├── tools/                  # LangChain Tools
│   │   │   ├── __init__.py
│   │   │   ├── file_tools.py       # 文件操作工具（读取、写入、修改、列表）
│   │   │   └── base_tool.py        # 工具基类
│   │   │
│   │   └── memory/                 # LangChain Memory
│   │       ├── __init__.py
│   │       └── conversation_memory.py  # 会话记忆管理
│   │
│   ├── services/                   # 业务服务层
│   │   ├── __init__.py
│   │   ├── application_controller.py   # 应用控制器，连接前后端
│   │   ├── model_config_manager.py     # 模型配置管理器
│   │   ├── session_manager.py          # 会话管理器
│   │   └── system_context.py           # 系统上下文提供者
│   │
│   ├── workers/                    # QThread 工作线程
│   │   ├── __init__.py
│   │   └── chat_worker.py          # 聊天工作线程，处理 AI 响应
│   │
│   ├── utils/                      # 工具函数
│   │   ├── __init__.py
│   │   ├── config.py               # 配置文件读写
│   │   ├── logger.py               # 日志工具
│   │   └── validators.py           # 输入验证工具
│   │
│   └── resources/                  # 资源文件
│       ├── icons/                  # 图标文件
│       │   ├── app.png
│       │   ├── new_session.png
│       │   ├── settings.png
│       │   └── send.png
│       └── styles/                 # QSS 样式表
│           ├── light_theme.qss     # 明亮主题
│           └── dark_theme.qss      # 暗黑主题
│
├── docs/                           # 文档目录
│   ├── USER_GUIDE.md               # 用户使用指南
│   ├── DEVELOPER_GUIDE.md          # 开发者文档
│   └── API.md                      # API 文档
│
├── scripts/                        # 脚本目录
│   ├── install.sh                  # 安装脚本（macOS/Linux）
│   ├── install.bat                 # 安装脚本（Windows）
│   ├── run.sh                      # 运行脚本（macOS/Linux）
│   └── run.bat                     # 运行脚本（Windows）
│
├── sessions/                       # 会话存储目录
│   ├── session_001/                # 单个会话目录
│   │   ├── metadata.json           # 会话元数据（名称、创建时间等）
│   │   └── messages.json           # 会话消息历史
│   ├── session_002/
│   └── ...
│
├── logs/                           # 日志目录
│   └── agent.log                   # 应用日志文件
│
├── tests/                          # 测试目录
│   ├── __init__.py
│   ├── test_tools.py               # 测试 LangChain Tools
│   ├── test_session_manager.py     # 测试会话管理
│   └── test_model_config.py        # 测试模型配置
│
├── config.yaml                     # 配置文件（模型配置、系统设置等）
├── requirements.txt                # Python 依赖包列表
├── README.md                       # 项目说明文档
├── .gitignore                      # Git 忽略文件
└── LICENSE                         # 许可证文件
```

### 目录说明

**src/ - 源代码目录**
- 包含应用程序入口、前端 GUI 组件、后端 LangChain 组件、业务服务层、工作线程、工具函数和资源文件

**docs/ - 文档目录**
- USER_GUIDE.md: 用户使用指南（功能介绍、操作说明、常见问题）
- DEVELOPER_GUIDE.md: 开发者文档（架构说明、开发指南、贡献指南）
- API.md: API 文档（主要类和方法的说明）

**scripts/ - 脚本目录**
- install.sh/install.bat: 跨平台安装脚本
- run.sh/run.bat: 跨平台运行脚本

**sessions/ - 会话存储目录**
- 每个会话独立目录，JSON 格式存储，易于备份和迁移

**logs/ - 日志目录**
- 存储应用运行日志，支持日志轮转

**tests/ - 测试目录**
- 单元测试和集成测试，覆盖核心功能模块

### 环境安装

**主要依赖包**
- PyQt6 (>=6.5.0): 桌面 GUI 框架
- LangChain (>=0.1.0): Agent 和 Tool 框架
- LangChain-OpenAI (>=0.0.5): OpenAPI 模型集成
- PyYAML (>=6.0): 配置文件管理
- Requests (>=2.31.0): HTTP 客户端

**安装脚本**

系统提供跨平台的安装脚本，自动完成环境配置：

**macOS/Linux (scripts/install.sh)**
- 检查 Python 版本（需要 3.9+）
- 创建虚拟环境
- 安装所有依赖包
- 创建必要的目录结构
- 生成默认配置文件
- 验证安装是否成功

**Windows (scripts/install.bat)**
- 检查 Python 版本（需要 3.9+）
- 创建虚拟环境
- 安装所有依赖包
- 创建必要的目录结构
- 生成默认配置文件
- 验证安装是否成功

**运行脚本**

**macOS/Linux (scripts/run.sh)**
- 激活虚拟环境
- 检查配置文件
- 启动应用程序

**Windows (scripts/run.bat)**
- 激活虚拟环境
- 检查配置文件
- 启动应用程序


## Security Considerations

### 1. 文件访问控制
- 验证文件路径是否在允许的目录内
- 限制文件大小（10MB）
- 检查文件格式

### 2. 输入验证
- 验证消息内容长度
- 验证会话名称合法性
- 检查非法字符

### 3. 数据隐私
- 所有会话数据存储在本地
- API 密钥存储在本地配置文件中
- 仅在用户发起对话时才向 OpenAPI 模型服务发送请求
- 不会主动上传用户数据到其他第三方服务


## Performance Optimization

### 1. LangChain 优化
- 使用流式响应（streaming=True）提升用户体验
- 使用 ConversationBufferMemory 管理对话历史，避免重复加载
- 合理设置 max_tokens 控制响应长度

### 2. 网络优化
- 实现请求超时和重试机制
- 使用异步请求避免阻塞
- 缓存模型配置减少配置文件读取

### 3. GUI 优化
- 使用 QTimer 实现防抖
- 优化长列表显示
- 批量更新 GUI 减少重绘
- 使用 QThread 处理网络请求


## Testing Strategy

### 1. 单元测试
- 测试 LangChain Tools（文件读取、写入、修改、列表）
- 测试模型配置管理功能
- 测试会话管理功能
- 测试系统上下文提供

### 2. GUI 测试
- 测试消息输入和发送
- 测试会话创建和切换
- 测试文件浏览器操作
- 测试模型配置界面

### 3. 集成测试
- 测试完整的聊天流程（用户输入 → LangChain Agent → OpenAPI Model → 响应显示）
- 测试工具调用流程（用户请求 → Agent 调用工具 → 工具执行 → 结果返回）
- 测试模型切换功能
- 测试会话持久化和恢复


## Implementation Notes

### 关键技术决策

1. **LangChain 核心架构**
   - 后端完全基于 LangChain 框架构建
   - 使用 AgentExecutor 管理工具调用和响应生成
   - 使用 ConversationBufferMemory 管理对话历史
   - 使用 SystemMessagePromptTemplate 注入系统上下文

2. **OpenAPI 模型集成**
   - 通过 LangChain-OpenAI 的 ChatOpenAI 集成远程模型
   - 支持任意 OpenAPI 兼容服务（OpenAI、Azure、自定义等）
   - 支持配置多个模型，灵活切换
   - 无需本地模型，降低硬件要求

3. **前后端分离**
   - 前端使用 PyQt6 构建 GUI
   - 后端使用 LangChain 处理业务逻辑
   - 使用 Qt 信号槽机制进行通信
   - 使用 QThread 处理耗时操作

4. **会话存储方式**
   - 采用 JSON 文件，每个会话独立目录
   - 简单，易于备份和迁移
   - 兼容 LangChain 的 Memory 机制

5. **热切换设计（无需重启）**
   - **模型切换**: 动态创建新的 ChatOpenAI 实例，保留会话历史
   - **工作目录切换**: 更新 SystemContextProvider，下次对话生效
   - **配置更新**: 实时保存到 config.yaml，立即生效
   - **主题切换**: 动态加载新的 QSS 样式表，无需重启
   - **会话切换**: 切换 ConversationBufferMemory，加载不同会话历史
   - 所有配置变更都通过信号槽机制通知相关组件，实现热更新

### 开发优先级

系统采用三阶段开发策略：

**Phase 1: 核心功能（MVP）**
- OpenAPI 模型配置管理、LangChain Agent 和 Tools 集成、基础聊天界面、会话管理、系统上下文提供

**Phase 2: 增强功能**
- 文件浏览器和工作目录选择、文本处理快捷操作、会话回滚、工具调用可视化、设置面板

**Phase 3: 高级功能**
- 文本对比视图、拖拽操作、主题切换、键盘快捷键、错误处理优化
