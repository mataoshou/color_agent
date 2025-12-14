# src/gui/notification_manager.py 分析文档

## 1. 文件概述

**文件路径**：`src/gui/notification_manager.py`
**功能定位**：提供系统通知功能，包括系统托盘通知、非阻塞式通知消息框和通知历史记录管理，支持不同级别的通知（信息、警告、错误）。
**核心类**：`NotificationLevel`（枚举类）、`Notification`（数据类）、`NotificationManager`（管理类）
**技术栈**：PyQt6

## 2. 核心实现分析

### 2.1 NotificationLevel 枚举类

**功能**：定义通知级别枚举常量，便于统一管理通知类型。

| 常量名 | 值 | 描述 |
|-------|-----|------|
| INFO | "info" | 信息类通知，用于一般状态提示 |
| WARNING | "warning" | 警告类通知，用于潜在问题提示 |
| ERROR | "error" | 错误类通知，用于严重问题提示 |

### 2.2 Notification 数据类

**功能**：封装通知的基本信息，便于在系统中传递和管理通知数据。

#### 2.2.1 类属性

| 属性名 | 类型 | 描述 |
|-------|------|------|
| level | str | 通知级别（取自NotificationLevel） |
| title | str | 通知标题 |
| message | str | 通知消息内容 |
| timestamp | datetime | 通知创建时间戳 |

#### 2.2.2 核心方法

**`__init__(self, level: str, title: str, message: str)`**
- **功能**：初始化通知对象，自动设置当前时间为时间戳
- **参数**：
  - `level`：通知级别
  - `title`：通知标题
  - `message`：通知消息

**`__str__(self) -> str`**
- **功能**：返回格式化的通知字符串表示
- **返回格式**：`[时间戳] [级别] 标题: 消息`
- **示例**：`[2023-10-10 14:30:00] [INFO] 成功: 操作完成`

### 2.3 NotificationManager 管理类

**功能**：管理系统托盘通知和非阻塞式通知消息框，维护通知历史记录，提供通知的显示、查询和清理功能。

#### 2.3.1 类属性

| 属性名 | 类型 | 描述 |
|-------|------|------|
| parent_widget | Optional[QWidget] | 父窗口组件 |
| tray_icon | Optional[QSystemTrayIcon] | 系统托盘图标对象 |
| notification_history | List[Notification] | 通知历史记录列表 |
| max_history | int | 历史记录最大数量限制（默认100） |

#### 2.3.2 信号

| 信号名 | 参数类型 | 描述 |
|-------|---------|------|
| notification_clicked | Notification | 当通知被点击时发出 |

#### 2.3.3 核心方法

**`__init__(self, parent: Optional[QWidget] = None)`**
- **功能**：初始化通知管理器
- **参数**：`parent` - 父窗口组件（可选）

**`setup_system_tray(self, icon: Optional[QIcon] = None, menu: Optional[QMenu] = None)`**
- **功能**：设置系统托盘图标和右键菜单
- **实现细节**：
  - 检查系统托盘可用性
  - 创建QSystemTrayIcon对象
  - 设置图标和右键菜单
  - 连接激活事件
  - 显示托盘图标

**`show_notification(self, title: str, message: str, level: str = NotificationLevel.INFO, duration: int = 3000, use_tray: bool = True)`**
- **功能**：显示通知的核心方法
- **参数**：
  - `title`：通知标题
  - `message`：通知消息内容
  - `level`：通知级别（默认INFO）
  - `duration`：显示时长（毫秒，默认3000）
  - `use_tray`：是否使用系统托盘（默认True）
- **实现细节**：
  - 创建Notification对象
  - 添加到历史记录
  - 根据级别记录日志
  - 显示系统托盘通知

**便捷方法**：
- `show_info(self, title: str, message: str, duration: int = 3000)` - 显示信息类通知
- `show_warning(self, title: str, message: str, duration: int = 5000)` - 显示警告类通知（默认5秒）
- `show_error(self, title: str, message: str, duration: int = 5000)` - 显示错误类通知（默认5秒）

**历史记录管理**：
- `get_notification_history(self) -> List[Notification]` - 获取通知历史记录（倒序排列）
- `clear_history(self)` - 清空通知历史记录

**托盘管理**：
- `hide_tray_icon(self)` - 隐藏系统托盘图标
- `show_tray_icon(self)` - 显示系统托盘图标

**内部辅助方法**：
- `_add_to_history(self, notification: Notification)` - 添加通知到历史记录，自动限制数量
- `_get_icon_for_level(self, level: str) -> QSystemTrayIcon.MessageIcon` - 根据通知级别获取对应的系统托盘图标
- `_on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason)` - 处理托盘图标激活事件（单击时显示主窗口）

## 3. 与其他模块的关系

| 依赖模块 | 依赖关系 | 使用方式 |
|---------|---------|---------|
| `PyQt6.QtWidgets` | 界面框架 | 使用QSystemTrayIcon、QMenu等组件实现通知功能 |
| `PyQt6.QtGui` | 图形库 | 使用QIcon等图形资源 |
| `PyQt6.QtCore` | 核心功能 | 使用QObject、pyqtSignal、QTimer等核心组件 |
| `logging` | 日志记录 | 记录通知相关操作和错误信息 |
| `datetime` | 时间处理 | 记录通知时间戳 |

## 4. 代码结构与设计模式

```
├── NotificationLevel (枚举类)
│   ├── INFO
│   ├── WARNING
│   └── ERROR
├── Notification (数据类)
│   ├── __init__()
│   └── __str__()
└── NotificationManager (管理类)
    ├── __init__()
    ├── setup_system_tray()
    ├── show_notification()
    ├── show_info()
    ├── show_warning()
    ├── show_error()
    ├── get_notification_history()
    ├── clear_history()
    ├── hide_tray_icon()
    ├── show_tray_icon()
    ├── _add_to_history()
    ├── _get_icon_for_level()
    └── _on_tray_activated()
```

**设计特点**：
- 采用职责分离模式，将通知级别、数据和管理逻辑分别封装
- 使用信号槽机制实现组件间解耦
- 提供便捷的API接口（show_info, show_warning, show_error）简化使用
- 支持系统托盘集成，增强用户体验
- 实现通知历史记录，便于追溯系统状态

## 5. 潜在改进点

1. **通知界面增强**：
   - 添加桌面通知窗口（浮动气泡），提供更丰富的视觉反馈
   - 支持通知内容的富文本格式（如链接、换行等）
   - 添加通知点击事件处理，支持跳转相关功能

2. **通知管理功能扩展**：
   - 实现通知过滤机制（可配置特定级别的通知是否显示）
   - 添加通知历史记录的查询和导出功能
   - 支持通知持久化存储（当前仅保存在内存中）

3. **用户体验优化**：
   - 实现通知显示位置的可配置（如右上角、右下角等）
   - 添加通知动画效果，提升视觉体验
   - 支持通知声音提示（可选）

4. **功能完整性**：
   - 添加通知优先级支持，实现重要通知置顶显示
   - 支持批量处理通知（如批量清除）
   - 实现通知超时自动消失（当前仅系统托盘通知支持）

5. **代码优化**：
   - 将硬编码的通知时长（3000ms, 5000ms）提取为配置常量
   - 增强错误处理，特别是系统托盘不可用时的降级策略
   - 添加单元测试，覆盖各种通知场景

## 6. 总结

`src/gui/notification_manager.py`实现了一个功能完整的通知管理系统，包含了通知级别定义、通知数据封装和通知显示管理等核心功能。该模块采用PyQt6框架实现了系统托盘通知功能，并提供了便捷的API接口供其他模块调用。

核心特点包括：
- 支持三种通知级别（信息、警告、错误）
- 实现系统托盘集成和通知历史记录
- 提供简洁易用的API接口
- 良好的日志记录和错误处理

该模块在整个系统中扮演着重要的用户反馈角色，通过非阻塞式的通知方式，既提供了必要的系统状态提示，又不会打断用户的正常操作流程。