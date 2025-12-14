# services/system_context.py 分析文档

## 1. 文件概述

**文件路径**: `src/services/system_context.py`
**文件类型**: Python业务服务类
**核心功能**: 提供系统上下文信息，包括工作目录、操作系统类型和版本、Python版本等，并提供路径处理和验证功能
**技术亮点**: 采用数据类设计，提供统一的系统信息访问接口，支持工作目录管理和路径安全验证

## 2. 数据模型定义

### SystemContext数据类

```python
@dataclass
class SystemContext:
    """系统上下文数据类"""
    working_directory: str
    os_type: str
    os_version: str
    python_version: str
```

**功能**: 表示系统上下文信息

**属性说明**:
- `working_directory`: 当前工作目录
- `os_type`: 操作系统类型（Darwin, Linux, Windows）
- `os_version`: 操作系统版本
- `python_version`: Python版本

**核心方法**:

#### `to_dict(self) -> dict`
```python
def to_dict(self) -> dict:
    """转换为字典"""
    return {
        'working_directory': self.working_directory,
        'os_type': self.os_type,
        'os_version': self.os_version,
        'python_version': self.python_version
    }
```
**功能**: 将系统上下文转换为字典格式

#### `to_prompt_text(self) -> str`
```python
def to_prompt_text(self) -> str:
    """转换为 Prompt 文本"""
    return f"""系统上下文信息：
- 当前工作目录: {self.working_directory}
- 操作系统: {self.os_type} {self.os_version}
- Python 版本: {self.python_version}"""
```
**功能**: 将系统上下文转换为适合作为提示词的文本格式

## 3. SystemContextProvider类定义

### 3.1 核心属性

| 属性名 | 类型 | 用途 |
|-------|------|------|
| _working_directory | str | 当前工作目录 |
| _os_type | str | 操作系统类型 |
| _os_version | str | 操作系统版本 |
| _python_version | str | Python版本 |

### 3.2 初始化方法

```python
def __init__(self, working_directory: Optional[str] = None):
    """
    初始化系统上下文提供者
    
    Args:
        working_directory: 工作目录路径，如果为 None 则使用当前目录
    """
    self._working_directory = working_directory or os.getcwd()
    self._os_type = self._get_os_type()
    self._os_version = self._get_os_version()
    self._python_version = self._get_python_version()
```

**功能**: 初始化系统上下文提供者，设置工作目录和系统信息

**设计亮点**:
- 允许自定义工作目录
- 默认使用当前目录
- 自动获取系统信息

## 4. 核心方法分析

### 4.1 系统上下文获取

#### `get_context(self) -> SystemContext`
```python
def get_context(self) -> SystemContext:
    """
    获取系统上下文
    
    Returns:
        SystemContext: 系统上下文对象
    """
    return SystemContext(
        working_directory=self._working_directory,
        os_type=self._os_type,
        os_version=self._os_version,
        python_version=self._python_version
    )
```

**功能**: 获取完整的系统上下文对象

### 4.2 工作目录管理

#### `get_working_directory(self) -> str`
```python
def get_working_directory(self) -> str:
    """
    获取当前工作目录
    
    Returns:
        str: 工作目录路径
    """
    return self._working_directory
```

**功能**: 获取当前工作目录

#### `set_working_directory(self, directory: str) -> bool`
```python
def set_working_directory(self, directory: str) -> bool:
    """
    设置工作目录
    
    Args:
        directory: 新的工作目录路径
        
    Returns:
        bool: 设置是否成功
    """
    # 验证目录是否存在
    if not os.path.exists(directory):
        return False
    
    if not os.path.isdir(directory):
        return False
    
    # 转换为绝对路径
    abs_path = os.path.abspath(directory)
    self._working_directory = abs_path
    
    return True
```

**功能**: 设置工作目录

**设计亮点**:
- 验证目录是否存在
- 验证目录是否为目录（非文件）
- 自动转换为绝对路径
- 返回设置结果

### 4.3 系统信息获取

#### `get_os_info(self) -> tuple[str, str]`
```python
def get_os_info(self) -> tuple[str, str]:
    """
    获取操作系统信息
    
    Returns:
        tuple: (操作系统类型, 操作系统版本)
    """
    return self._os_type, self._os_version
```

**功能**: 获取操作系统信息

#### `get_python_version(self) -> str`
```python
def get_python_version(self) -> str:
    """
    获取 Python 版本
    
    Returns:
        str: Python 版本
    """
    return self._python_version
```

**功能**: 获取Python版本

### 4.4 路径处理与验证

#### `validate_path(self, path: str) -> bool`
```python
def validate_path(self, path: str) -> bool:
    """
    验证路径是否在工作目录内
    
    Args:
        path: 要验证的路径
        
    Returns:
        bool: 路径是否有效
    """
    try:
        # 转换为绝对路径
        abs_path = os.path.abspath(path)
        abs_working_dir = os.path.abspath(self._working_directory)
        
        # 检查路径是否在工作目录内
        return abs_path.startswith(abs_working_dir)
    except Exception:
        return False
```

**功能**: 验证路径是否在工作目录内

**设计亮点**:
- 安全验证：防止路径遍历攻击
- 转换为绝对路径进行比较
- 异常处理：确保即使路径处理失败也能返回安全结果

#### `resolve_path(self, path: str) -> str`
```python
def resolve_path(self, path: str) -> str:
    """
    解析相对路径为绝对路径
    
    Args:
        path: 相对或绝对路径
        
    Returns:
        str: 绝对路径
    """
    if os.path.isabs(path):
        return path
    
    # 相对于工作目录的路径
    return os.path.join(self._working_directory, path)
```

**功能**: 解析相对路径为绝对路径

#### `get_relative_path(self, abs_path: str) -> str`
```python
def get_relative_path(self, abs_path: str) -> str:
    """
    获取相对于工作目录的相对路径
    
    Args:
        abs_path: 绝对路径
        
    Returns:
        str: 相对路径
    """
    try:
        return os.path.relpath(abs_path, self._working_directory)
    except Exception:
        return abs_path
```

**功能**: 获取相对于工作目录的相对路径

**设计亮点**:
- 异常处理：确保即使路径转换失败也能返回有效的路径

### 4.5 内部辅助方法

#### `_get_os_type(self) -> str`
```python
def _get_os_type(self) -> str:
    """
    获取操作系统类型
    
    Returns:
        str: 操作系统类型 (Darwin, Linux, Windows)
    """
    return platform.system()
```

**功能**: 获取操作系统类型

#### `_get_os_version(self) -> str`
```python
def _get_os_version(self) -> str:
    """
    获取操作系统版本
    
    Returns:
        str: 操作系统版本
    """
    try:
        if platform.system() == 'Darwin':
            # macOS
            return f"macOS {platform.mac_ver()[0]}"
        elif platform.system() == 'Linux':
            # Linux
            return f"{platform.system()} {platform.release()}"
        elif platform.system() == 'Windows':
            # Windows
            return f"Windows {platform.release()}"
        else:
            return platform.release()
    except Exception:
        return "Unknown"
```

**功能**: 获取操作系统版本

**设计亮点**:
- 针对不同操作系统进行特殊处理
- 异常处理：确保即使获取失败也能返回有效的版本信息

#### `_get_python_version(self) -> str`
```python
def _get_python_version(self) -> str:
    """
    获取 Python 版本
    
    Returns:
        str: Python 版本
    """
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
```

**功能**: 获取Python版本

## 5. 架构设计与模式

### 5.1 数据类设计模式

使用Python的dataclass装饰器定义SystemContext数据类，提高了代码的可读性和维护性。数据类自动生成了`__init__`、`__repr__`等方法，减少了重复代码。

### 5.2 上下文提供者模式

SystemContextProvider实现了上下文提供者模式，为应用程序提供统一的系统信息访问接口。这种模式的优点是：

- 集中管理系统上下文
- 提供统一的访问接口
- 方便扩展和维护
- 支持上下文的动态更新

### 5.3 安全设计

SystemContextProvider实现了安全的路径验证机制，防止路径遍历攻击：

```python
def validate_path(self, path: str) -> bool:
    try:
        abs_path = os.path.abspath(path)
        abs_working_dir = os.path.abspath(self._working_directory)
        return abs_path.startswith(abs_working_dir)
    except Exception:
        return False
```

这种设计确保了应用程序只能访问工作目录内的文件，提高了系统的安全性。

## 6. 与其他模块关系

### 6.1 与ApplicationController的关系

SystemContextProvider被ApplicationController依赖，用于管理系统上下文：

```
ApplicationController
└── SystemContextProvider
    └── SystemContext数据类
```

- ApplicationController调用SystemContextProvider的方法来获取和设置系统上下文
- SystemContextProvider为ApplicationController提供系统信息

### 6.2 与FileTools的关系

SystemContextProvider提供的路径验证和解析功能被用于FileTools：

```
FileTools
└── SystemContextProvider (提供路径验证和解析)
```

- FileTools使用SystemContextProvider来验证和解析文件路径
- SystemContextProvider确保FileTools只能访问工作目录内的文件

## 7. 潜在改进点

### 7.1 更多系统信息支持

**问题**: 当前只提供了基本的系统信息
**建议**: 添加更多系统信息，如硬件信息、环境变量等

```python
@dataclass
class SystemContext:
    working_directory: str
    os_type: str
    os_version: str
    python_version: str
    cpu_info: str
    memory_info: str
    environment_variables: dict
```

### 7.2 路径安全增强

**问题**: 当前路径验证只检查是否在工作目录内
**建议**: 增强路径安全验证，如防止符号链接攻击

```python
def validate_path(self, path: str) -> bool:
    try:
        # 解析符号链接
        abs_path = os.path.realpath(path)
        abs_working_dir = os.path.realpath(self._working_directory)
        
        # 检查路径是否在工作目录内
        return abs_path.startswith(abs_working_dir)
    except Exception:
        return False
```

### 7.3 上下文持久化

**问题**: 当前系统上下文不支持持久化
**建议**: 添加上下文持久化功能

```python
def save_context(self, path: str) -> bool:
    """保存系统上下文"""
    try:
        context = self.get_context()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(context.to_dict(), f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def load_context(self, path: str) -> bool:
    """加载系统上下文"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            context_data = json.load(f)
        
        # 设置工作目录
        if 'working_directory' in context_data:
            self.set_working_directory(context_data['working_directory'])
        
        return True
    except Exception:
        return False
```

### 7.4 路径操作增强

**问题**: 当前路径操作功能有限
**建议**: 添加更多路径操作方法

```python
def get_files_in_directory(self, path: str = None) -> List[str]:
    """获取目录中的文件列表"""
    directory = path or self._working_directory
    if not self.validate_path(directory):
        return []
    
    try:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    except Exception:
        return []

def get_directories_in_directory(self, path: str = None) -> List[str]:
    """获取目录中的子目录列表"""
    directory = path or self._working_directory
    if not self.validate_path(directory):
        return []
    
    try:
        return [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
    except Exception:
        return []
```

### 7.5 工作目录历史记录

**问题**: 当前不支持工作目录历史记录
**建议**: 添加工作目录历史记录功能

```python
def __init__(self, working_directory: Optional[str] = None):
    self._working_directory = working_directory or os.getcwd()
    self._working_directory_history = [self._working_directory]
    # ... 其他初始化代码

def set_working_directory(self, directory: str) -> bool:
    if not super().set_working_directory(directory):
        return False
    
    # 添加到历史记录
    if directory != self._working_directory_history[-1]:
        self._working_directory_history.append(directory)
        # 限制历史记录长度
        if len(self._working_directory_history) > 10:
            self._working_directory_history.pop(0)
    
    return True

def get_working_directory_history(self) -> List[str]:
    """获取工作目录历史记录"""
    return self._working_directory_history.copy()
```

### 7.6 环境变量管理

**问题**: 当前不支持环境变量管理
**建议**: 添加环境变量管理功能

```python
def get_environment_variable(self, name: str) -> Optional[str]:
    """获取环境变量"""
    return os.environ.get(name)

def set_environment_variable(self, name: str, value: str) -> None:
    """设置环境变量"""
    os.environ[name] = value

def get_all_environment_variables(self) -> dict:
    """获取所有环境变量"""
    return dict(os.environ)
```

## 8. 总结

SystemContextProvider是一个设计良好的系统上下文提供者，它提供了完整的系统信息访问和管理功能，包括：

1. **系统信息获取**：提供操作系统类型、版本、Python版本等系统信息
2. **工作目录管理**：支持获取和设置工作目录
3. **路径处理与验证**：提供路径验证、解析和转换功能，确保路径安全
4. **上下文转换**：支持将系统上下文转换为字典和提示词格式

该组件具有以下特点：

1. **良好的设计**：采用数据类设计，结构清晰，易于理解和维护
2. **安全可靠**：实现了安全的路径验证机制，防止路径遍历攻击
3. **灵活扩展**：提供了统一的接口，便于扩展和维护
4. **方便使用**：提供了简洁的API，便于应用程序使用

SystemContextProvider在应用程序架构中扮演着重要角色，为应用程序提供了统一的系统信息访问接口，同时确保了系统的安全性。通过进一步优化，可以提高其功能和性能，更好地满足应用程序的需求。