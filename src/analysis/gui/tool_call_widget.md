# src/gui/tool_call_widget.py 文件分析

## 1. 文件概述

`tool_call_widget.py` 定义了用于可视化显示工具调用过程和结果的 `ToolCallWidget` 组件，是 Color Agent 应用中工具调用功能的用户界面表示层。该组件提供了直观的工具调用状态展示，包括工具名称、输入参数、执行状态和输出结果，同时支持动画效果增强用户体验。

## 2. 核心实现分析

### 2.1 类定义与基本结构

```python
class ToolCallWidget(QWidget):
    def __init__(self, tool_name: str, input_str: str = "", parent: Optional[QWidget] = None):
        # 初始化代码...
```

**主要属性**：
- `tool_name`: 工具名称
- `input_str`: 工具输入参数
- `output_str`: 工具输出结果
- `is_finished`: 工具调用是否完成状态
- `_animation_timer`: 执行状态动画定时器
- `_animation_dots`: 动画点数计数器

### 2.2 核心方法

#### 2.2.1 初始化与 UI 构建

```python
def _init_ui(self) -> None:
    # 主布局
    main_layout = QHBoxLayout(self)
    main_layout.setContentsMargins(10, 5, 10, 5)
    
    # 气泡容器
    bubble = QWidget()
    bubble.setObjectName("toolCallBubble")
    bubble.setMaximumWidth(500)
    
    # 内部布局
    layout = QVBoxLayout(bubble)
    # ... 构建工具图标、名称、参数和状态标签
```

- **UI 结构**：采用气泡式设计，包含工具图标、名称、输入参数和状态信息
- **响应式设计**：设置最大宽度限制，确保在不同屏幕尺寸下显示效果一致
- **交互性**：支持文本选择功能，方便用户复制参数和结果

#### 2.2.2 样式管理

```python
def _apply_style(self) -> None:
    if self.is_finished:
        # 完成状态：绿色边框
        style = """QWidget#toolCallBubble { background-color: #f0f9ff; border: 2px solid #4CAF50; ... }"""
    else:
        # 执行中状态：蓝色边框
        style = """QWidget#toolCallBubble { background-color: #f0f9ff; border: 2px solid #2196F3; ... }"""
    
    # 应用完整样式表
    self.setStyleSheet(style)
```

- **状态驱动样式**：根据执行状态动态切换边框颜色（蓝色表示执行中，绿色表示完成）
- **组件样式**：为不同元素定义了统一的视觉风格，包括字体、颜色和边距

#### 2.2.3 数据格式化

```python
def _format_input(self, input_str: str) -> str:
    try:
        # 尝试解析为 JSON
        data = json.loads(input_str)
        formatted = json.dumps(data, ensure_ascii=False, indent=2)
        # 限制长度
        if len(formatted) > 200:
            formatted = formatted[:200] + "..."
        return formatted
    except:
        # 如果不是 JSON，直接返回（限制长度）
        if len(input_str) > 200:
            return input_str[:200] + "..."
        return input_str
```

- **智能格式化**：自动检测并格式化 JSON 数据，提升可读性
- **长度限制**：对过长内容进行截断处理，避免 UI 布局变形
- **容错处理**：非 JSON 格式数据也能正确显示

#### 2.2.4 动画效果

```python
def _update_animation(self) -> None:
    if self.is_finished:
        self._animation_timer.stop()
        return
    
    # 更新点数（0-3）
    self._animation_dots = (self._animation_dots + 1) % 4
    dots = "." * self._animation_dots
    self.status_label.setText(f"执行中{dots}")
```

- **执行中动画**：通过动态更新状态文本的点数量，提供视觉反馈
- **资源管理**：工具调用完成后自动停止动画，避免资源浪费

#### 2.2.5 结果更新

```python
def set_output(self, output_str: str) -> None:
    self.output_str = output_str
    self.is_finished = True
    
    # 停止动画
    self._animation_timer.stop()
    
    # 更新状态
    self.status_label.setText("✓ 执行完成")
    self.status_label.setStyleSheet("color: #4CAF50;")
    
    # 显示输出结果
    self.output_label.show()
    self.output_content.setText(self._format_output(output_str))
    self.output_content.show()
    
    # 更新样式
    self._apply_style()
```

- **状态转换**：从执行中状态转换为完成状态
- **结果展示**：显示格式化后的输出结果
- **视觉反馈**：通过颜色变化和文本更新提供完成通知

## 3. 与其他模块关系

- **依赖关系**：
  - `PyQt6`：用于 UI 组件和布局管理
  - `json`：用于参数和结果的格式化
  - `logging`：用于组件创建和状态变化的日志记录

- **被依赖关系**：
  - 可能被聊天窗口或会话组件使用，用于显示工具调用过程
  - 作为 Color Agent 工具调用功能的可视化表现层

## 4. 代码结构与设计模式

```
ToolCallWidget
├── __init__              # 初始化组件
├── _init_ui              # 构建用户界面
├── _apply_style          # 应用样式表
├── _format_input         # 格式化输入参数
├── _format_output        # 格式化输出结果
├── _update_animation     # 更新执行中动画
└── set_output            # 设置并显示执行结果
```

- **设计模式**：采用组件化设计，将工具调用的显示逻辑封装为独立组件
- **关注点分离**：UI 构建、样式管理、数据格式化和动画效果分别由不同方法处理
- **可扩展性**：组件设计允许轻松添加新功能或修改现有行为

## 5. 潜在改进点

1. **错误状态处理**：当前实现只区分执行中和已完成状态，建议添加错误状态支持，显示不同的错误信息和样式

2. **复制功能**：增加一键复制参数和结果的按钮，提升用户操作便捷性

3. **展开/折叠功能**：对于长文本内容，提供展开/折叠功能，节省 UI 空间

4. **主题适配**：当前样式硬编码了颜色值，建议改为使用应用程序的主题系统

5. **响应式优化**：针对移动设备或小屏幕设备，进一步优化布局和字体大小

## 6. 总结

`tool_call_widget.py` 实现了一个功能完整、视觉友好的工具调用可视化组件。该组件通过气泡式设计、动态样式切换和执行中动画，为用户提供了清晰直观的工具调用过程反馈。其模块化设计和良好的封装性使得组件可以轻松集成到应用的不同部分。虽然当前实现已经满足基本需求，但通过添加错误状态处理、复制功能和主题适配等改进，可以进一步提升用户体验和组件的可维护性。