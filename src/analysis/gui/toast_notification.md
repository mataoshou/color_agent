# src/gui/toast_notification.py 分析文档

## 1. 文件概述

**文件路径**：`src/gui/toast_notification.py`
**功能定位**：提供非阻塞式通知消息框，在屏幕右下角显示，自动消失，不影响用户操作。
**核心类**：`ToastNotification`, `ToastManager`
**技术栈**：PyQt6

## 2. 核心实现分析

### 2.1 ToastNotification 类

**功能**：创建单个通知消息框，支持不同级别（info/warning/error）和自动消失动画。

#### 2.1.1 类属性

| 属性名 | 类型 | 描述 |
|-------|------|------|
| duration | int | 显示时长（毫秒） |
| level | str | 通知级别（info/warning/error） |
| opacity_effect | QGraphicsOpacityEffect | 透明度效果对象 |
| fade_in_animation | QPropertyAnimation | 淡入动画 |
| fade_out_animation | QPropertyAnimation | 淡出动画 |
| close_timer | QTimer | 自动关闭定时器 |

#### 2.1.2 核心方法

**`__init__(self, title: str, message: str, level: str = "info", duration: int = 3000, parent: Optional[QWidget] = None)`**
- **功能**：初始化通知消息框
- **参数**：`title` - 通知标题，`message` - 通知消息，`level` - 通知级别，`duration` - 显示时长，`parent` - 父窗口
- **实现细节**：
  - 保存显示时长和通知级别
  - 初始化UI界面
  - 设置动画效果

**`_init_ui(self, title: str, message: str)`**
- **功能**：构建通知消息框的用户界面
- **参数**：`title` - 通知标题，`message` - 通知消息
- **实现细节**：
  - 设置窗口属性（无边框、工具窗口、置顶）
  - 设置半透明背景和不激活状态
  - 创建标题和消息标签
  - 设置样式表

**`_set_background_color(self)`**
- **功能**：根据通知级别设置背景颜色
- **实现细节**：
  - info级别：绿色（rgba(40, 167, 69, 0.9)）
  - warning级别：黄色（rgba(255, 193, 7, 0.9)）
  - error级别：红色（rgba(220, 53, 69, 0.9)）

**`_setup_animation(self)`**
- **功能**：设置淡入淡出动画
- **实现细节**：
  - 创建透明度效果
  - 设置淡入动画（300ms，从透明到不透明）
  - 设置淡出动画（300ms，从不透明到透明）
  - 配置自动关闭定时器

**`show_notification(self)`**
- **功能**：显示通知
- **实现细节**：
  - 计算屏幕右下角位置
  - 显示窗口
  - 开始淡入动画
  - 启动自动关闭定时器

**`_start_fade_out(self)`**
- **功能**：开始淡出动画

**`mousePressEvent(self, event)`**
- **功能**：处理鼠标点击事件，点击时关闭通知

### 2.2 ToastManager 类

**功能**：管理多个Toast通知的显示位置和队列。

#### 2.2.1 类属性

| 属性名 | 类型 | 描述 |
|-------|------|------|
| parent | Optional[QWidget] | 父窗口 |
| active_toasts | List[ToastNotification] | 活动通知列表 |
| toast_spacing | int | 通知之间的间距 |

#### 2.2.2 核心方法

**`__init__(self, parent: Optional[QWidget] = None)`**
- **功能**：初始化Toast管理器
- **参数**：`parent` - 父窗口
- **实现细节**：
  - 保存父窗口
  - 初始化活动通知列表
  - 设置通知间距

**`show_toast(self, title: str, message: str, level: str = "info", duration: int = 3000)`**
- **功能**：显示Toast通知
- **参数**：`title` - 通知标题，`message` - 通知消息，`level` - 通知级别，`duration` - 显示时长
- **实现细节**：
  - 创建ToastNotification实例
  - 计算显示位置
  - 添加到活动列表
  - 显示通知
  - 设置通知关闭时的回调

**`show_info(self, title: str, message: str, duration: int = 3000)`**
- **功能**：显示信息通知

**`show_warning(self, title: str, message: str, duration: int = 5000)`**
- **功能**：显示警告通知

**`show_error(self, title: str, message: str, duration: int = 5000)`**
- **功能**：显示错误通知

**`_position_toast(self, toast: ToastNotification)`**
- **功能**：计算Toast的显示位置
- **参数**：`toast` - Toast通知对象
- **实现细节**：
  - 计算屏幕右下角位置
  - 根据已有的通知调整垂直偏移

**`_remove_toast(self, toast: ToastNotification)`**
- **功能**：从活动列表移除Toast
- **参数**：`toast` - Toast通知对象

## 3. 与其他模块的关系

| 依赖模块 | 依赖关系 | 使用方式 |
|---------|---------|---------|
| `PyQt6.QtWidgets` | 界面框架 | 使用QWidget、QLabel、QVBoxLayout等组件构建UI |
| `PyQt6.QtCore` | 核心功能 | 使用Qt、QTimer、QPropertyAnimation等核心组件 |
| `PyQt6.QtGui` | 图形库 | 使用QPalette、QColor等图形资源 |
| `logging` | 日志记录 | 记录Toast通知相关操作和事件 |

## 4. 代码结构与设计模式

```
ToastNotification (QWidget)
├── __init__()
├── _init_ui()
├── _set_background_color()
├── _setup_animation()
├── show_notification()
├── _start_fade_out()
└── mousePressEvent()

ToastManager
├── __init__()
├── show_toast()
├── show_info()
├── show_warning()
├── show_error()
├── _position_toast()
└── _remove_toast()
```

**设计特点**：
- 采用组合模式，通过ToastManager管理多个ToastNotification实例
- 使用动画效果提升用户体验
- 支持不同级别的通知，使用不同颜色区分
- 非阻塞式设计，不影响用户操作
- 自动管理通知队列和位置

## 5. 潜在改进点

1. **功能扩展**：
   - 添加通知点击事件处理，支持点击后执行特定操作
   - 支持通知暂停和恢复动画
   - 添加通知优先级支持

2. **用户体验优化**：
   - 支持自定义通知位置
   - 添加通知声音提示
   - 支持通知内容的格式化（如HTML格式）

3. **性能优化**：
   - 限制最大通知数量，避免屏幕被通知覆盖
   - 实现通知的批量处理，减少动画资源消耗

4. **代码优化**：
   - 将样式表提取到外部文件或常量中
   - 增加单元测试覆盖
   - 优化动画效果和过渡体验

## 6. 总结

`src/gui/toast_notification.py`实现了一个非阻塞式通知消息框系统，包含两个主要类：ToastNotification和ToastManager。ToastNotification类用于创建单个通知消息框，支持不同级别和自动消失动画；ToastManager类用于管理多个通知的显示位置和队列。

核心特点包括：
- 非阻塞式设计，不影响用户操作
- 淡入淡出动画效果，提升用户体验
- 支持不同级别的通知（info/warning/error），使用不同颜色区分
- 自动管理通知队列和位置，避免重叠
- 点击通知可立即关闭
- 可配置显示时长

该组件在系统中主要用于显示临时提示信息，如操作成功、警告或错误信息，提升了用户体验和系统的交互性。