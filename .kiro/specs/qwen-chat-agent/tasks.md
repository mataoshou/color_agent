# Implementation Plan

## 任务概述

本实现计划将 AI Chat Agent 系统分解为可执行的开发任务。系统前端采用 PyQt6 构建桌面应用程序，后端以 LangChain 架构为核心，通过 OpenAPI 协议连接远程 AI 模型服务。

## 任务列表

- [x] 1. 项目初始化和基础架构
- [x] 1.1 创建项目目录结构
  - 创建 src/、sessions/、logs/、tests/ 等目录
  - 创建 gui/、backend/、services/、workers/、utils/ 子目录
  - 创建必要的 __init__.py 文件
  - _Requirements: 所有需求_

- [x] 1.2 创建配置文件管理模块
  - 实现 config.yaml 读取和写入功能
  - 创建 Settings、ModelConfig 等数据类
  - 实现配置验证和修复功能
  - 实现默认配置生成功能
  - _Requirements: 1.3, 1.7, 1.8_

- [x] 1.3 创建日志系统
  - 实现日志配置和初始化
  - 配置 RotatingFileHandler（10MB，5个备份）
  - 实现日志格式化（时间戳、模块名、级别、消息）
  - 添加控制台和文件双输出
  - _Requirements: 8.5_

- [x] 1.4 创建系统上下文提供者
  - 实现 SystemContextProvider 类
  - 获取工作目录、操作系统类型和版本、Python 版本
  - 实现工作目录切换功能
  - _Requirements: 4.2, 4.3, 5.6, 5.7_

- [x] 2. OpenAPI 模型配置管理
- [x] 2.1 实现 ModelConfigManager 类
  - 实现模型配置的添加、编辑、删除功能
  - 实现模型配置的加载和保存
  - 实现模型配置验证（API 端点、密钥、模型名称）
  - 实现当前激活模型的切换
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.9_

- [x] 2.2 实现模型配置对话框 UI
  - 创建 ModelConfigDialog (QDialog)
  - 实现模型名称、API 端点、密钥、模型标识符输入框
  - 实现模型配置的添加和编辑功能
  - 实现输入验证和错误提示
  - _Requirements: 1.2, 1.3, 1.5_

- [x] 2.3 实现模型列表管理 UI
  - 在 SettingsDialog 中实现模型列表展示（QListWidget）
  - 实现"添加模型"、"编辑"、"删除"按钮
  - 实现模型连接状态指示器
  - 实现当前使用模型的下拉选择菜单
  - _Requirements: 1.1, 1.4, 1.5, 1.6, 1.9_

- [-] 3. LangChain Agent 和 Tools 集成
- [x] 3.1 实现 LangChain 文件操作工具
  - 创建 ReadFileTool 类（读取文件内容）
  - 创建 WriteFileTool 类（创建或覆盖文件）
  - 创建 ModifyFileTool 类（修改文件内容）
  - 创建 ListFilesTool 类（列出目录文件）
  - 实现文件路径验证、大小检查、格式检查
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 3.2 实现 Prompt 模板
  - 创建 SystemMessagePromptTemplate
  - 实现系统上下文注入（工作目录、操作系统信息）
  - 实现工具使用说明的 Prompt
  - _Requirements: 5.6, 5.7_

- [x] 3.3 实现 LangChain Agent 执行器
  - 创建 AgentExecutor 初始化逻辑
  - 集成 ChatOpenAI（OpenAPI 模型）
  - 注册 LangChain Tools
  - 集成 ConversationBufferMemory
  - 实现流式响应生成
  - _Requirements: 2.3, 2.4, 5.2, 5.3_

- [x] 3.4 实现聊天工作线程
  - 创建 ChatWorker (QThread)
  - 实现消息处理和 Agent 调用
  - 实现流式响应信号发送（message_chunk）
  - 实现工具调用信号发送（tool_call_started/finished）
  - 实现错误处理和重试机制
  - _Requirements: 2.3, 2.4, 5.5_

- [x] 4. 会话管理功能
- [x] 4.1 实现 SessionManager 类
  - 实现会话创建和 UUID 生成
  - 实现会话保存到独立目录（JSON 格式）
  - 实现会话加载和列表查询
  - 实现会话删除和重命名
  - 实现自动保存功能
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4.2 实现会话侧边栏 UI
  - 创建 SessionSidebar (QWidget)
  - 实现会话列表展示（QListWidget）
  - 实现新建会话对话框（QInputDialog）
  - 实现会话切换功能
  - 实现会话右键菜单（删除、重命名）
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4.3 实现会话项自定义组件
  - 创建 SessionItemWidget (QWidget)
  - 显示会话名称、时间戳和最新消息预览
  - 实现选中状态样式
  - _Requirements: 3.2_

- [x] 5. 聊天界面
- [x] 5.1 实现 ChatWidget 组件
  - 创建消息列表展示（QListWidget）
  - 实现消息输入框（QTextEdit）
  - 实现发送按钮（QPushButton）
  - 实现消息发送信号
  - _Requirements: 2.1, 2.2_

- [x] 5.2 实现消息气泡自定义组件
  - 创建 MessageBubble (QWidget)
  - 实现用户和 AI 消息不同样式（QSS）
  - 实现消息对齐方式（用户右对齐，AI 左对齐）
  - _Requirements: 2.2, 2.5_

- [x] 5.3 实现流式响应显示
  - 使用 QTimer 批量更新 GUI
  - 实现逐字显示效果
  - 实现"正在输入"动画指示器（QLabel with QMovie）
  - _Requirements: 2.3, 2.4_

- [x] 5.4 实现工具调用可视化
  - 创建工具调用消息项（特殊样式）
  - 显示工具名称、参数和结果
  - 实现工具调用过程的动画效果
  - _Requirements: 5.5_

- [x] 5.5 实现文本处理快捷操作
  - 创建文本处理下拉菜单（QComboBox）
  - 实现润色、扩写、缩写、翻译功能
  - 实现文本选中检测和浮动工具栏（QToolBar）
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 6. 文件浏览器
- [x] 6.1 实现文件浏览器 UI
  - 创建 FileBrowser (QWidget)
  - 实现文件树展示（QTreeView with QFileSystemModel）
  - 实现工作目录选择按钮和对话框（QFileDialog）
  - 实现文件双击查看（QDialog with QTextEdit）
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 6.2 实现文件操作功能
  - 实现右键上下文菜单（QMenu）
  - 实现"让 AI 阅读"和"让 AI 修改"功能
  - 实现拖拽文件到对话区域（dragEnterEvent/dropEvent）
  - _Requirements: 4.5, 4.6, 4.7_

- [x] 7. 设置对话框
- [x] 7.1 实现 SettingsDialog UI
  - 创建设置对话框（QDialog）
  - 实现模型选择下拉菜单（QComboBox）
  - 实现温度参数滑块（QSlider，0.0-2.0）
  - 实现最大长度输入框（QSpinBox，512-4096）
  - _Requirements: 1.7, 1.8_

- [x] 7.2 实现主题切换功能
  - 实现明暗主题切换选项（QRadioButton）
  - 实现设置保存功能
  - 实现主题动态加载（QSS 样式表）
  - _Requirements: 7.5_

- [x] 8. 主窗口和应用控制器
- [x] 8.1 实现 MainWindow 主窗口
  - 创建主窗口（QMainWindow）
  - 实现三栏布局（QSplitter）
  - 实现工具栏（QToolBar）
  - 实现状态栏（QStatusBar）
  - 整合所有 UI 组件
  - _Requirements: 7.1, 7.2, 7.4_

- [x] 8.2 实现 ApplicationController
  - 创建 ApplicationController (QObject)
  - 定义所有信号（消息、模型、会话、错误等）
  - 实现信号槽连接（GUI ↔ Controller）
  - 实现消息处理、模型切换、会话管理等方法
  - _Requirements: 所有需求_

- [x] 8.3 实现键盘快捷键
  - 实现 Ctrl+N 新建会话（QShortcut）
  - 实现 Ctrl+S 保存会话
  - 实现 Ctrl+Enter 发送消息
  - _Requirements: 7.3_

- [x] 9. 样式和主题
- [x] 9.1 创建 QSS 样式表
  - 创建明亮主题样式表（light_theme.qss）
  - 创建暗黑主题样式表（dark_theme.qss）
  - 实现消息气泡样式
  - 实现会话项样式
  - 实现按钮和输入框样式
  - _Requirements: 2.5, 7.5_

- [x] 10. 错误处理和通知
- [x] 10.1 实现错误处理机制
  - 创建错误类定义（AgentError、ModelError、SessionError、FileError）
  - 实现错误对话框（QMessageBox）
  - 实现错误日志记录
  - _Requirements: 8.1, 8.2, 8.3_

- [x] 10.2 实现通知系统
  - 实现系统托盘通知（QSystemTrayIcon）
  - 实现非阻塞式通知消息框
  - 实现日志查看窗口（QDialog with QTextEdit）
  - _Requirements: 8.2, 8.4, 8.5_

- [x] 11. 应用初始化和启动
- [x] 11.1 实现应用入口（main.py）
  - 实现配置文件检查和默认配置生成
  - 实现目录结构创建（sessions/、logs/）
  - 实现日志系统初始化
  - 实现首次使用引导（添加模型配置）
  - 实现 MainWindow 创建和显示
  - _Requirements: 所有需求_

- [x] 12. 高级功能
- [x] 12.1 实现会话回滚功能
  - 实现消息右键菜单（QMenu）
  - 实现回滚确认对话框（QMessageBox）
  - 实现回滚后消息半透明显示
  - _Requirements: 3.5_

- [x] 12.2 实现文本对比视图
  - 创建分屏对比组件（QSplitter with QTextEdit）
  - 实现差异高亮显示
  - 实现"查看差异"按钮（QPushButton）
  - _Requirements: 6.5_

- [-] 13. 文档和脚本
- [x] 13.1 创建用户使用指南（docs/USER_GUIDE.md）
  - 编写应用简介和功能概述
  - 编写安装和启动说明
  - 编写模型配置指南（如何添加 OpenAI、Azure、自定义模型）
  - 编写基本操作说明（创建会话、发送消息、切换模型）
  - 编写文件操作说明（文件浏览器、让 AI 读取/修改文件）
  - 编写常见问题解答（FAQ）
  - _Requirements: 所有需求_

- [x] 13.2 创建开发者文档（docs/DEVELOPER_GUIDE.md）
  - 编写架构说明（前后端分离、LangChain 核心）
  - 编写开发环境搭建指南
  - 编写代码结构说明
  - 编写开发规范（日志、注释、测试）
  - 编写贡献指南
  - _Requirements: 所有需求_

- [x] 13.3 创建 API 文档（docs/API.md）
  - 编写主要类的说明（ModelConfigManager、SessionManager、ApplicationController）
  - 编写主要方法的说明（参数、返回值、异常）
  - 编写信号槽说明
  - 编写配置文件格式说明
  - _Requirements: 所有需求_

- [x] 13.4 创建安装脚本（所有环境配置必须在此完成）
  - 创建 scripts/install.sh（macOS/Linux）
    - 检查 Python 版本（需要 3.9+）
    - 检查并安装系统依赖（如需要）
    - 创建虚拟环境（venv）
    - 激活虚拟环境
    - 升级 pip 到最新版本
    - 安装所有依赖包（requirements.txt）
    - 创建应用目录结构（sessions/、logs/、docs/）
    - 生成默认配置文件（config.yaml）
    - 设置文件权限
    - 验证安装（检查依赖、目录、配置）
    - 输出安装成功信息和使用说明
  - 创建 scripts/install.bat（Windows）
    - 检查 Python 版本（需要 3.9+）
    - 创建虚拟环境（venv）
    - 激活虚拟环境
    - 升级 pip 到最新版本
    - 安装所有依赖包（requirements.txt）
    - 创建应用目录结构（sessions/、logs/、docs/）
    - 生成默认配置文件（config.yaml）
    - 验证安装（检查依赖、目录、配置）
    - 输出安装成功信息和使用说明
  - **注意：应用代码不得修改系统环境，所有环境配置必须在安装脚本中完成**
  - _Requirements: 所有需求_

- [x] 13.5 创建运行脚本
  - 创建 scripts/run.sh（macOS/Linux）
    - 激活虚拟环境
    - 检查配置文件
    - 启动应用程序
  - 创建 scripts/run.bat（Windows）
    - 激活虚拟环境
    - 检查配置文件
    - 启动应用程序
  - _Requirements: 所有需求_

- [x] 13.6 创建项目 README.md
  - 编写项目简介
  - 编写功能特性列表
  - 编写快速开始指南
  - 编写截图和演示
  - 编写许可证信息
  - _Requirements: 所有需求_

## 开发注意事项

### 环境隔离要求（重要）
- **禁止在编码阶段修改系统环境**
- 所有环境配置（虚拟环境创建、依赖安装、目录创建）必须在安装脚本中完成
- 应用代码只能读取和使用已配置好的环境，不能修改系统级设置
- 不允许在代码中执行 pip install、创建系统目录等操作
- 配置文件（config.yaml）的修改仅限于应用数据目录内

### 日志和注释要求
- 所有关键操作必须记录详细日志（应用启动、模型切换、会话操作、消息处理、文件操作、错误异常）
- 每个模块文件必须包含模块级文档字符串
- 每个类必须包含类级文档字符串
- 每个公共方法必须包含详细的文档字符串（参数、返回值、异常、示例）
- 复杂逻辑必须添加行内注释说明

### 热切换要求
- 模型切换必须支持热切换（动态创建新的 ChatOpenAI 实例，保留会话历史）
- 工作目录切换必须支持热切换（更新 SystemContextProvider，下次对话生效）
- 主题切换必须支持热切换（动态加载新的 QSS 样式表）
- 所有配置变更必须通过信号槽机制通知相关组件

### 测试要求
- 为 LangChain Tools 编写单元测试
- 为模型配置管理编写单元测试
- 为会话管理编写单元测试
- 编写集成测试验证完整的聊天流程

### 代码质量要求
- 遵循 PEP 8 代码规范
- 使用类型提示（Type Hints）
- 避免代码重复，提取公共函数
- 保持函数和方法的单一职责
