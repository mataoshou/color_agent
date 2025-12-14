# API 文档

本文档详细说明了 AI Chat Agent 系统的主要类、方法、信号槽和配置文件格式。

## 目录

- [核心服务类](#核心服务类)
  - [ModelConfigManager](#modelconfigmanager)
  - [SessionManager](#sessionmanager)
  - [ApplicationController](#applicationcontroller)
  - [SystemContextProvider](#systemcontextprovider)
- [数据模型](#数据模型)
  - [ModelConfig](#modelconfig)
  - [Session](#session)
  - [Message](#message)
  - [Settings](#settings)
- [信号槽系统](#信号槽系统)
- [配置文件格式](#配置文件格式)
- [LangChain 组件](#langchain-组件)

---

## 核心服务类

### ModelConfigManager

模型配置管理器，负责管理多个 OpenAPI 模型配置。

**位置**: `src/services/model_config_manager.py`

#### 初始化

```python
def __init__(self, config_manager: Optional[ConfigManager] = None)
```

**参数**:
- `config_manager` (Optional[ConfigManager]): 配置管理器实例，如果为 None 则创建新实例

#### 主要方法

##### add_model

```python
def add_model(self, model_config: ModelConfig) -> bool
```

添加模型配置。

**参数**:
- `model_config` (ModelConfig): 模型配置对象

**返回值**:
- `bool`: 添加成功返回 True，失败返回 False

**异常**:
- 如果模型 ID 已存在，返回 False
- 如果模型配置验证失败，返回 False

##### update_model

```python
def update_model(self, model_config: ModelConfig) -> bool
```

更新模型配置。

**参数**:
- `model_config` (ModelConfig): 模型配置对象

**返回值**:
- `bool`: 更新成功返回 True，失败返回 False

**异常**:
- 如果模型不存在，返回 False
- 如果模型配置验证失败，返回 False

##### delete_model

```python
def delete_model(self, model_id: str) -> bool
```

删除模型配置。

**参数**:
- `model_id` (str): 模型 ID

**返回值**:
- `bool`: 删除成功返回 True，失败返回 False

##### get_model_config

```python
def get_model_config(self, model_id: str) -> Optional[ModelConfig]
```

获取模型配置。

**参数**:
- `model_id` (str): 模型 ID

**返回值**:
- `Optional[ModelConfig]`: 模型配置对象，如果不存在返回 None

##### get_all_models

```python
def get_all_models(self) -> List[ModelConfig]
```

获取所有模型配置。

**返回值**:
- `List[ModelConfig]`: 模型配置列表

##### get_active_model

```python
def get_active_model(self) -> Optional[ModelConfig]
```

获取当前激活的模型配置。

**返回值**:
- `Optional[ModelConfig]`: 当前激活的模型配置，如果没有返回 None

##### set_active_model

```python
def set_active_model(self, model_id: str) -> bool
```

设置当前激活的模型。

**参数**:
- `model_id` (str): 模型 ID

**返回值**:
- `bool`: 设置成功返回 True，失败返回 False

**异常**:
- 如果模型不存在，返回 False

##### validate_model_config

```python
def validate_model_config(self, model_config: ModelConfig) -> bool
```

验证模型配置的有效性。

**参数**:
- `model_config` (ModelConfig): 模型配置对象

**返回值**:
- `bool`: 验证通过返回 True，否则返回 False

**验证规则**:
- 模型 ID 不能为空
- 模型名称不能为空
- API 端点不能为空且必须以 http:// 或 https:// 开头
- API 密钥不能为空
- 模型标识符不能为空

##### has_models

```python
def has_models(self) -> bool
```

检查是否有已配置的模型。

**返回值**:
- `bool`: 有模型返回 True，否则返回 False

---

### SessionManager

会话管理器，负责会话的创建、保存、加载、删除和重命名。

**位置**: `src/services/session_manager.py`

#### 初始化

```python
def __init__(self, storage_path: str = "./sessions", auto_save: bool = True)
```

**参数**:
- `storage_path` (str): 会话存储路径，默认为 "./sessions"
- `auto_save` (bool): 是否启用自动保存，默认为 True

#### 主要方法

##### create_session

```python
def create_session(self, name: Optional[str] = None) -> Session
```

创建新会话。

**参数**:
- `name` (Optional[str]): 会话名称，如果为 None 则自动生成（格式："新会话 - YYYY-MM-DD HH:MM:SS"）

**返回值**:
- `Session`: 创建的会话对象

**行为**:
- 生成唯一的会话 ID（UUID）
- 创建会话目录（`storage_path/session_id/`）
- 自动保存会话到磁盘
- 设置为当前会话

##### save_session

```python
def save_session(self, session: Session) -> None
```

保存会话到磁盘。

**参数**:
- `session` (Session): 要保存的会话对象

**异常**:
- 如果保存失败，抛出异常

**保存内容**:
- `metadata.json`: 会话元数据（ID、名称、创建时间、更新时间、消息数量）
- `messages.json`: 消息历史记录

##### load_session

```python
def load_session(self, session_id: str) -> Session
```

加载会话。

**参数**:
- `session_id` (str): 会话 ID

**返回值**:
- `Session`: 加载的会话对象

**异常**:
- `FileNotFoundError`: 会话不存在
- `ValueError`: 会话文件损坏

**行为**:
- 从磁盘加载会话数据
- 设置为当前会话

##### list_sessions

```python
def list_sessions(self) -> List[Dict[str, Any]]
```

列出所有会话。

**返回值**:
- `List[Dict[str, Any]]`: 会话列表，按更新时间倒序排列

**返回字典格式**:
```python
{
    'session_id': str,
    'name': str,
    'created_at': str,
    'updated_at': str,
    'message_count': int,
    'preview': str,  # 最新消息预览（最多50字符）
    'corrupted': bool  # 可选，如果会话文件损坏则为 True
}
```

##### delete_session

```python
def delete_session(self, session_id: str) -> None
```

删除会话。

**参数**:
- `session_id` (str): 会话 ID

**异常**:
- `FileNotFoundError`: 会话不存在

**行为**:
- 删除会话目录及其所有文件
- 如果删除的是当前会话，清空当前会话

##### rename_session

```python
def rename_session(self, session_id: str, new_name: str) -> None
```

重命名会话。

**参数**:
- `session_id` (str): 会话 ID
- `new_name` (str): 新的会话名称

**异常**:
- `FileNotFoundError`: 会话不存在

**行为**:
- 更新会话元数据中的名称
- 更新时间戳
- 如果是当前会话，同步更新当前会话对象

##### add_message

```python
def add_message(self, role: str, content: str) -> Optional[Message]
```

向当前会话添加消息。

**参数**:
- `role` (str): 消息角色（'user' 或 'assistant'）
- `content` (str): 消息内容

**返回值**:
- `Optional[Message]`: 创建的消息对象，如果没有当前会话返回 None

**行为**:
- 创建消息对象并添加到当前会话
- 如果启用自动保存，自动保存会话

##### get_current_session

```python
def get_current_session(self) -> Optional[Session]
```

获取当前会话。

**返回值**:
- `Optional[Session]`: 当前会话对象，如果没有返回 None

##### rollback_to_message

```python
def rollback_to_message(self, sequence_number: int) -> bool
```

回滚会话到指定消息。

**参数**:
- `sequence_number` (int): 消息序号

**返回值**:
- `bool`: 是否成功回滚

**行为**:
- 在会话元数据中标记回滚点
- 不删除消息，仅标记
- 如果启用自动保存，自动保存会话

##### get_rollback_point

```python
def get_rollback_point(self) -> Optional[int]
```

获取当前会话的回滚点。

**返回值**:
- `Optional[int]`: 回滚点序号，如果没有回滚返回 None

---

### ApplicationController

应用程序控制器，连接前端 GUI 和后端 LangChain 架构。

**位置**: `src/services/application_controller.py`

**继承**: `QObject`

#### 初始化

```python
def __init__(self, parent: Optional[QObject] = None)
```

**参数**:
- `parent` (Optional[QObject]): 父对象

**初始化组件**:
- ConfigManager: 配置管理器
- ModelConfigManager: 模型配置管理器
- SessionManager: 会话管理器
- SystemContextProvider: 系统上下文提供者
- AgentExecutorManager: Agent 管理器（延迟初始化）

#### 主要方法

##### initialize

```python
def initialize(self) -> bool
```

初始化控制器。

**返回值**:
- `bool`: 初始化是否成功

**行为**:
- 检查是否有可用的模型配置
- 初始化 Agent 管理器
- 加载工作目录配置

##### on_send_message

```python
def on_send_message(self, message: str) -> None
```

处理发送消息。

**参数**:
- `message` (str): 用户消息

**行为**:
- 检查 Agent 是否已初始化
- 如果没有当前会话，自动创建新会话
- 添加用户消息到会话
- 创建 ChatWorker 线程处理消息
- 连接工作线程信号

**发出信号**:
- `message_chunk`: 流式响应文本块
- `message_complete`: 消息生成完成
- `tool_call_started`: 工具调用开始
- `tool_call_finished`: 工具调用完成
- `error_occurred`: 错误发生

##### on_model_changed

```python
def on_model_changed(self, model_id: str) -> None
```

处理模型切换。

**参数**:
- `model_id` (str): 模型 ID

**行为**:
- 获取模型配置
- 设置为激活模型
- 重新初始化 Agent 管理器（热切换）
- 保留现有会话历史

**发出信号**:
- `model_switched`: 模型切换成功
- `status_message`: 状态消息
- `error_occurred`: 错误发生

##### on_create_session

```python
def on_create_session(self, name: Optional[str] = None) -> None
```

处理创建会话。

**参数**:
- `name` (Optional[str]): 会话名称

**发出信号**:
- `session_created`: 会话创建
- `sessions_list_updated`: 会话列表更新
- `status_message`: 状态消息

##### on_load_session

```python
def on_load_session(self, session_id: str) -> None
```

处理加载会话。

**参数**:
- `session_id` (str): 会话 ID

**行为**:
- 保存当前会话（如果有）
- 加载目标会话
- 获取回滚点信息

**发出信号**:
- `session_loaded`: 会话加载（携带会话数据）
- `status_message`: 状态消息
- `error_occurred`: 错误发生

##### on_save_session

```python
def on_save_session(self) -> None
```

处理保存会话。

**发出信号**:
- `session_saved`: 会话保存
- `status_message`: 状态消息

##### on_delete_session

```python
def on_delete_session(self, session_id: str) -> None
```

处理删除会话。

**参数**:
- `session_id` (str): 会话 ID

**发出信号**:
- `session_deleted`: 会话删除
- `sessions_list_updated`: 会话列表更新
- `status_message`: 状态消息

##### on_rename_session

```python
def on_rename_session(self, session_id: str, new_name: str) -> None
```

处理重命名会话。

**参数**:
- `session_id` (str): 会话 ID
- `new_name` (str): 新名称

**发出信号**:
- `session_renamed`: 会话重命名
- `sessions_list_updated`: 会话列表更新
- `status_message`: 状态消息

##### on_directory_changed

```python
def on_directory_changed(self, directory: str) -> None
```

处理工作目录变更。

**参数**:
- `directory` (str): 新的工作目录路径

**行为**:
- 更新系统上下文
- 更新配置文件
- 重新初始化 Agent（更新系统上下文）

**发出信号**:
- `working_directory_changed`: 工作目录变更
- `status_message`: 状态消息
- `error_occurred`: 错误发生

##### on_rollback_requested

```python
def on_rollback_requested(self, message_index: int) -> None
```

处理会话回滚请求。

**参数**:
- `message_index` (int): 消息索引

**发出信号**:
- `status_message`: 状态消息
- `error_occurred`: 错误发生

##### on_ai_read_file

```python
def on_ai_read_file(self, file_path: str) -> None
```

处理 AI 阅读文件请求。

**参数**:
- `file_path` (str): 文件路径

**行为**:
- 读取文件内容
- 构建包含文件内容的消息
- 发送给 AI 处理

##### on_ai_modify_file

```python
def on_ai_modify_file(self, file_path: str) -> None
```

处理 AI 修改文件请求。

**参数**:
- `file_path` (str): 文件路径

**行为**:
- 读取文件内容
- 构建包含文件内容的消息
- 发送给 AI 处理

##### load_sessions_list

```python
def load_sessions_list(self) -> None
```

加载会话列表。

**发出信号**:
- `sessions_list_updated`: 会话列表更新

##### get_active_model_name

```python
def get_active_model_name(self) -> str
```

获取当前激活的模型名称。

**返回值**:
- `str`: 模型名称，如果没有配置返回 "未配置"

##### cleanup

```python
def cleanup(self) -> None
```

清理资源。

**行为**:
- 停止工作线程
- 保存当前会话

---

### SystemContextProvider

系统上下文提供者，提供工作目录、操作系统等信息。

**位置**: `src/services/system_context.py`

#### 主要方法

##### get_context

```python
def get_context(self) -> Dict[str, str]
```

获取系统上下文信息。

**返回值**:
- `Dict[str, str]`: 系统上下文字典

**返回格式**:
```python
{
    'working_directory': str,  # 当前工作目录
    'os_type': str,            # 操作系统类型（Darwin/Linux/Windows）
    'os_version': str,         # 操作系统版本
    'python_version': str      # Python 版本
}
```

##### set_working_directory

```python
def set_working_directory(self, directory: str) -> bool
```

设置工作目录。

**参数**:
- `directory` (str): 目录路径

**返回值**:
- `bool`: 设置成功返回 True，失败返回 False

**验证**:
- 检查目录是否存在
- 检查是否为有效目录

##### get_working_directory

```python
def get_working_directory(self) -> str
```

获取当前工作目录。

**返回值**:
- `str`: 工作目录路径

---

## 数据模型

### ModelConfig

模型配置数据类。

**位置**: `src/utils/config.py`

**字段**:
- `id` (str): 模型唯一标识符
- `name` (str): 模型显示名称
- `api_base` (str): API 端点 URL
- `api_key` (str): API 密钥
- `model_name` (str): 模型标识符（如 "gpt-4"）
- `description` (Optional[str]): 模型描述

**方法**:
- `to_dict() -> Dict`: 转换为字典

### Session

会话数据类。

**位置**: `src/services/session_manager.py`

**字段**:
- `session_id` (str): 会话唯一标识符（UUID）
- `name` (str): 会话名称
- `messages` (List[Message]): 消息列表
- `created_at` (str): 创建时间（ISO 格式）
- `updated_at` (str): 最后更新时间（ISO 格式）
- `metadata` (Dict[str, Any]): 元数据字典

**方法**:
- `to_dict() -> Dict`: 转换为字典
- `from_dict(data: Dict) -> Session`: 从字典创建会话对象（静态方法）
- `add_message(role: str, content: str) -> Message`: 添加消息到会话
- `get_latest_message_preview(max_length: int = 50) -> str`: 获取最新消息预览

### Message

消息数据类。

**位置**: `src/services/session_manager.py`

**字段**:
- `role` (str): 消息角色（'user' 或 'assistant'）
- `content` (str): 消息内容
- `timestamp` (str): 消息时间戳（ISO 格式）
- `sequence_number` (int): 消息序号

**方法**:
- `to_dict() -> Dict`: 转换为字典
- `from_dict(data: Dict) -> Message`: 从字典创建消息对象（静态方法）

### Settings

系统设置数据类。

**位置**: `src/utils/config.py`

**字段**:

**模型配置**:
- `active_model_id` (Optional[str]): 当前激活的模型 ID
- `models` (Dict[str, Dict]): 模型配置字典

**LangChain 配置**:
- `temperature` (float): 温度参数（默认 0.7，范围 0.0-2.0）
- `max_tokens` (int): 最大 token 数（默认 2048，范围 512-4096）
- `streaming` (bool): 是否启用流式响应（默认 True）
- `verbose` (bool): 是否显示详细日志（默认 False）

**工作目录配置**:
- `working_directory` (str): 当前工作目录（默认 "."）

**会话配置**:
- `storage_path` (str): 会话存储路径（默认 "./sessions"）
- `auto_save` (bool): 是否自动保存（默认 True）
- `max_history` (int): 最多保留的历史消息数（默认 100）

**文件操作配置**:
- `allowed_formats` (List[str]): 允许的文件格式列表
- `max_file_size` (int): 最大文件大小（默认 10MB）

**日志配置**:
- `log_level` (str): 日志级别（默认 "INFO"）
- `log_file` (str): 日志文件路径（默认 "./logs/agent.log"）

**UI 配置**:
- `theme` (str): 主题（'light' 或 'dark'，默认 'light'）
- `window_width` (int): 窗口宽度（默认 1200）
- `window_height` (int): 窗口高度（默认 800）

**方法**:
- `to_dict() -> Dict`: 转换为字典

---

## 信号槽系统

ApplicationController 使用 Qt 信号槽机制进行前后端通信。

### 消息相关信号

#### message_chunk
```python
message_chunk = pyqtSignal(str)
```
流式响应的文本块。

**参数**:
- `str`: 文本块内容

#### message_complete
```python
message_complete = pyqtSignal(str)
```
消息生成完成。

**参数**:
- `str`: 完整的响应内容

#### tool_call_started
```python
tool_call_started = pyqtSignal(str, str)
```
工具调用开始。

**参数**:
- `str`: 工具名称
- `str`: 工具输入参数（JSON 字符串）

#### tool_call_finished
```python
tool_call_finished = pyqtSignal(str, str)
```
工具调用完成。

**参数**:
- `str`: 工具名称
- `str`: 工具输出结果（JSON 字符串）

### 模型相关信号

#### model_switched
```python
model_switched = pyqtSignal(str)
```
模型切换成功。

**参数**:
- `str`: 模型名称

#### model_connection_failed
```python
model_connection_failed = pyqtSignal(str)
```
模型连接失败。

**参数**:
- `str`: 错误信息

### 会话相关信号

#### session_created
```python
session_created = pyqtSignal(str)
```
会话创建。

**参数**:
- `str`: 会话 ID

#### session_loaded
```python
session_loaded = pyqtSignal(dict)
```
会话加载。

**参数**:
- `dict`: 会话数据字典

**字典格式**:
```python
{
    'session_id': str,
    'name': str,
    'messages': List[Dict],
    'created_at': str,
    'updated_at': str,
    'rollback_point': Optional[int]
}
```

#### session_saved
```python
session_saved = pyqtSignal(str)
```
会话保存。

**参数**:
- `str`: 会话 ID

#### session_deleted
```python
session_deleted = pyqtSignal(str)
```
会话删除。

**参数**:
- `str`: 会话 ID

#### session_renamed
```python
session_renamed = pyqtSignal(str, str)
```
会话重命名。

**参数**:
- `str`: 会话 ID
- `str`: 新名称

#### sessions_list_updated
```python
sessions_list_updated = pyqtSignal(list)
```
会话列表更新。

**参数**:
- `list`: 会话列表

**列表项格式**:
```python
{
    'session_id': str,
    'name': str,
    'created_at': str,
    'updated_at': str,
    'message_count': int,
    'preview': str,
    'corrupted': bool  # 可选
}
```

### 系统上下文相关信号

#### working_directory_changed
```python
working_directory_changed = pyqtSignal(str)
```
工作目录变更。

**参数**:
- `str`: 新的目录路径

### 错误相关信号

#### error_occurred
```python
error_occurred = pyqtSignal(str)
```
错误发生。

**参数**:
- `str`: 错误信息

### 状态相关信号

#### status_message
```python
status_message = pyqtSignal(str, int)
```
状态消息。

**参数**:
- `str`: 消息文本
- `int`: 超时时间（毫秒）

---

## 配置文件格式

配置文件采用 YAML 格式，位于项目根目录的 `config.yaml`。

### 完整配置示例

```yaml
# 模型配置
active_model_id: "openai-gpt4"
models:
  openai-gpt4:
    id: "openai-gpt4"
    name: "OpenAI GPT-4"
    api_base: "https://api.openai.com/v1"
    api_key: "sk-..."
    model_name: "gpt-4"
    description: "OpenAI GPT-4 模型"
  
  azure-gpt35:
    id: "azure-gpt35"
    name: "Azure GPT-3.5"
    api_base: "https://your-resource.openai.azure.com"
    api_key: "your-azure-key"
    model_name: "gpt-35-turbo"
    description: "Azure OpenAI GPT-3.5 Turbo"

# LangChain 配置
temperature: 0.7
max_tokens: 2048
streaming: true
verbose: false

# 工作目录配置
working_directory: "."

# 会话配置
storage_path: "./sessions"
auto_save: true
max_history: 100

# 文件操作配置
allowed_formats:
  - ".txt"
  - ".md"
  - ".py"
  - ".js"
  - ".json"
  - ".yaml"
  - ".yml"
  - ".html"
  - ".css"
  - ".xml"
  - ".csv"
  - ".log"
max_file_size: 10485760  # 10MB

# 日志配置
log_level: "INFO"
log_file: "./logs/agent.log"

# UI 配置
theme: "light"
window_width: 1200
window_height: 800
```

### 配置字段说明

#### 模型配置

- **active_model_id**: 当前激活的模型 ID，必须存在于 models 字典中
- **models**: 模型配置字典，键为模型 ID，值为模型配置对象
  - **id**: 模型唯一标识符
  - **name**: 模型显示名称
  - **api_base**: API 端点 URL（必须以 http:// 或 https:// 开头）
  - **api_key**: API 密钥
  - **model_name**: 模型标识符（如 "gpt-4"）
  - **description**: 模型描述（可选）

#### LangChain 配置

- **temperature**: 温度参数，控制响应的随机性（范围 0.0-2.0，默认 0.7）
- **max_tokens**: 最大 token 数（范围 512-4096，默认 2048）
- **streaming**: 是否启用流式响应（默认 true）
- **verbose**: 是否显示详细日志（默认 false）

#### 工作目录配置

- **working_directory**: 当前工作目录（默认 "."）

#### 会话配置

- **storage_path**: 会话存储路径（默认 "./sessions"）
- **auto_save**: 是否自动保存（默认 true）
- **max_history**: 最多保留的历史消息数（默认 100）

#### 文件操作配置

- **allowed_formats**: 允许的文件格式列表
- **max_file_size**: 最大文件大小（字节，默认 10MB）

#### 日志配置

- **log_level**: 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL，默认 INFO）
- **log_file**: 日志文件路径（默认 "./logs/agent.log"）

#### UI 配置

- **theme**: 主题（'light' 或 'dark'，默认 'light'）
- **window_width**: 窗口宽度（默认 1200）
- **window_height**: 窗口高度（默认 800）

### 配置验证规则

系统启动时会自动验证配置并修复无效值：

1. **温度参数**: 必须在 0.0-2.0 范围内，否则重置为 0.7
2. **max_tokens**: 必须在 512-4096 范围内，否则重置为 2048
3. **工作目录**: 必须存在，否则重置为 "."
4. **主题**: 必须为 'light' 或 'dark'，否则重置为 'light'
5. **active_model_id**: 必须存在于 models 字典中，否则重置为 None
6. **日志级别**: 必须为有效级别，否则重置为 'INFO'

---

## LangChain 组件

### AgentExecutorManager

Agent 执行器管理器，管理 LangChain Agent 和工具。

**位置**: `src/backend/agent/agent_executor.py`

#### 初始化

```python
def __init__(
    self,
    api_base: str,
    api_key: str,
    model_name: str,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    system_context: Optional[Dict[str, str]] = None
)
```

**参数**:
- `api_base` (str): API 端点 URL
- `api_key` (str): API 密钥
- `model_name` (str): 模型标识符
- `temperature` (float): 温度参数
- `max_tokens` (int): 最大 token 数
- `system_context` (Optional[Dict[str, str]]): 系统上下文信息

#### 主要方法

##### run

```python
def run(self, message: str, callbacks: Optional[List] = None) -> str
```

运行 Agent 处理消息。

**参数**:
- `message` (str): 用户消息
- `callbacks` (Optional[List]): 回调函数列表

**返回值**:
- `str`: AI 响应

### LangChain Tools

系统提供以下 LangChain 工具，允许 AI 模型自主调用。

**位置**: `src/backend/tools/file_tools.py`

#### ReadFileTool

读取文件内容。

**输入参数**:
- `file_path` (str): 文件路径

**返回值**:
- `str`: 文件内容

**验证**:
- 文件路径必须在工作目录内
- 文件大小不超过配置的最大值
- 文件格式在允许列表中

#### WriteFileTool

创建或覆盖文件。

**输入参数**:
- `file_path` (str): 文件路径
- `content` (str): 文件内容

**返回值**:
- `str`: 操作结果消息

**验证**:
- 文件路径必须在工作目录内
- 内容大小不超过配置的最大值

#### ModifyFileTool

修改文件内容。

**输入参数**:
- `file_path` (str): 文件路径
- `old_content` (str): 要替换的内容
- `new_content` (str): 新内容

**返回值**:
- `str`: 操作结果消息

**验证**:
- 文件路径必须在工作目录内
- 文件必须存在
- old_content 必须在文件中存在

#### ListFilesTool

列出目录文件。

**输入参数**:
- `directory` (str): 目录路径（可选，默认为工作目录）

**返回值**:
- `str`: 文件列表（JSON 格式）

**验证**:
- 目录路径必须在工作目录内
- 目录必须存在

---

## 使用示例

### 初始化应用控制器

```python
from src.services.application_controller import ApplicationController

# 创建控制器
controller = ApplicationController()

# 初始化
if controller.initialize():
    print("控制器初始化成功")
else:
    print("控制器初始化失败")
```

### 连接信号槽

```python
# 连接消息相关信号
controller.message_chunk.connect(on_message_chunk)
controller.message_complete.connect(on_message_complete)
controller.tool_call_started.connect(on_tool_call_started)
controller.tool_call_finished.connect(on_tool_call_finished)

# 连接模型相关信号
controller.model_switched.connect(on_model_switched)
controller.model_connection_failed.connect(on_model_connection_failed)

# 连接会话相关信号
controller.session_created.connect(on_session_created)
controller.session_loaded.connect(on_session_loaded)
controller.sessions_list_updated.connect(on_sessions_list_updated)

# 连接错误信号
controller.error_occurred.connect(on_error_occurred)

# 连接状态信号
controller.status_message.connect(on_status_message)
```

### 发送消息

```python
# 发送用户消息
controller.on_send_message("你好，请帮我读取 README.md 文件")
```

### 管理会话

```python
# 创建新会话
controller.on_create_session("我的新会话")

# 加载会话
controller.on_load_session("session-id-here")

# 保存会话
controller.on_save_session()

# 删除会话
controller.on_delete_session("session-id-here")

# 重命名会话
controller.on_rename_session("session-id-here", "新名称")

# 加载会话列表
controller.load_sessions_list()
```

### 切换模型

```python
# 切换到指定模型
controller.on_model_changed("openai-gpt4")
```

### 管理模型配置

```python
from src.services.model_config_manager import ModelConfigManager
from src.utils.config import ModelConfig

# 创建模型配置管理器
model_manager = ModelConfigManager()

# 添加模型
model_config = ModelConfig(
    id="my-model",
    name="My Custom Model",
    api_base="https://api.example.com/v1",
    api_key="your-api-key",
    model_name="custom-model-name",
    description="My custom model"
)
model_manager.add_model(model_config)

# 获取所有模型
models = model_manager.get_all_models()

# 设置激活模型
model_manager.set_active_model("my-model")

# 获取激活模型
active_model = model_manager.get_active_model()
```

### 管理会话

```python
from src.services.session_manager import SessionManager

# 创建会话管理器
session_manager = SessionManager(storage_path="./sessions", auto_save=True)

# 创建新会话
session = session_manager.create_session("我的会话")

# 添加消息
session_manager.add_message('user', "你好")
session_manager.add_message('assistant', "你好！有什么可以帮助你的吗？")

# 保存会话
session_manager.save_session(session)

# 加载会话
loaded_session = session_manager.load_session(session.session_id)

# 列出所有会话
sessions = session_manager.list_sessions()

# 删除会话
session_manager.delete_session(session.session_id)

# 重命名会话
session_manager.rename_session(session.session_id, "新名称")

# 回滚会话
session_manager.rollback_to_message(5)  # 回滚到第 5 条消息
```

### 配置管理

```python
from src.utils.config import ConfigManager, Settings

# 创建配置管理器
config_manager = ConfigManager("config.yaml")

# 加载配置
settings = config_manager.load()

# 更新配置
config_manager.update_settings(
    temperature=0.8,
    max_tokens=3000,
    theme='dark'
)

# 获取配置
settings = config_manager.get_settings()
print(f"当前温度: {settings.temperature}")
print(f"当前主题: {settings.theme}")

# 创建默认配置
ConfigManager.create_default_config("config.yaml")
```

### 系统上下文

```python
from src.services.system_context import SystemContextProvider

# 创建系统上下文提供者
context_provider = SystemContextProvider()

# 获取系统上下文
context = context_provider.get_context()
print(f"工作目录: {context['working_directory']}")
print(f"操作系统: {context['os_type']}")
print(f"Python 版本: {context['python_version']}")

# 设置工作目录
context_provider.set_working_directory("/path/to/directory")

# 获取工作目录
working_dir = context_provider.get_working_directory()
```

---

## 错误处理

系统定义了以下错误类型：

**位置**: `src/utils/errors.py`

### AgentError

所有 Agent 相关错误的基类。

### ModelError

模型相关错误（连接失败、API 调用失败等）。

### SessionError

会话相关错误（创建失败、加载失败、保存失败等）。

### FileError

文件相关错误（读取失败、写入失败、权限错误等）。

### 错误处理示例

```python
from src.utils.errors import ModelError, SessionError

try:
    controller.on_send_message("Hello")
except ModelError as e:
    print(f"模型错误: {e}")
except SessionError as e:
    print(f"会话错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

---

## 注意事项

1. **线程安全**: ApplicationController 使用 QThread 处理耗时操作，确保 UI 不被阻塞
2. **自动保存**: SessionManager 默认启用自动保存，每次添加消息后自动保存会话
3. **配置验证**: ConfigManager 在加载配置时自动验证并修复无效值
4. **热切换**: 模型切换、工作目录切换、主题切换都支持热切换，无需重启应用
5. **错误恢复**: 系统提供完善的错误处理和恢复机制，配置文件损坏时自动备份并创建新配置
6. **日志记录**: 所有关键操作都记录详细日志，便于问题定位和调试

---

## 版本信息

- **文档版本**: 1.0
- **最后更新**: 2024
- **适用系统版本**: 1.0.0

---

## 相关文档

- [用户使用指南](USER_GUIDE.md)
- [开发者文档](DEVELOPER_GUIDE.md)
- [项目 README](../README.md)
