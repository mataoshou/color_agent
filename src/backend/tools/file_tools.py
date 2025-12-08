"""
LangChain 文件操作工具

提供文件读取、写入、修改和列表功能。
"""

import os
from typing import Optional, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from .base_tool import BaseFileTool


# ============================================================================
# ReadFileTool - 读取文件内容
# ============================================================================

class ReadFileInput(BaseModel):
    """读取文件工具的输入参数"""
    file_path: str = Field(description="要读取的文件路径（相对或绝对路径）")


class ReadFileTool(BaseTool):
    """读取文件内容的工具"""
    
    name: str = "read_file"
    description: str = """读取文件内容。
    输入应该是文件路径（相对或绝对路径）。
    返回文件的完整内容。
    示例输入: "README.md" 或 "src/main.py"
    """
    args_schema: Type[BaseModel] = ReadFileInput
    
    # 内部工具实例
    _file_tool: Optional[BaseFileTool] = None
    
    def __init__(self, working_directory: str, max_file_size: int = 10 * 1024 * 1024,
                 allowed_formats: Optional[list] = None):
        """
        初始化读取文件工具
        
        Args:
            working_directory: 工作目录
            max_file_size: 最大文件大小（字节）
            allowed_formats: 允许的文件格式列表
        """
        super().__init__()
        object.__setattr__(self, '_file_tool', BaseFileTool(working_directory, max_file_size, allowed_formats))
    
    def _run(self, file_path: str) -> str:
        """
        执行文件读取
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 文件内容或错误消息
        """
        try:
            # 验证路径
            valid, error_msg = self._file_tool.validate_path(file_path)
            if not valid:
                return f"错误: {error_msg}"
            
            # 验证文件格式
            valid, error_msg = self._file_tool.validate_file_format(file_path)
            if not valid:
                return f"错误: {error_msg}"
            
            # 解析为绝对路径
            abs_path = self._file_tool._resolve_path(file_path)
            
            # 检查文件是否存在
            if not os.path.exists(abs_path):
                return f"错误: 文件 '{file_path}' 不存在"
            
            if not os.path.isfile(abs_path):
                return f"错误: '{file_path}' 不是一个文件"
            
            # 验证文件大小
            valid, error_msg = self._file_tool.validate_file_size(file_path)
            if not valid:
                return f"错误: {error_msg}"
            
            # 读取文件内容
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return f"文件 '{file_path}' 的内容:\n\n{content}"
            
        except UnicodeDecodeError:
            return f"错误: 文件 '{file_path}' 不是文本文件或编码不支持"
        except Exception as e:
            return f"错误: 读取文件失败 - {str(e)}"
    
    async def _arun(self, file_path: str) -> str:
        """异步执行（暂不支持）"""
        raise NotImplementedError("ReadFileTool 不支持异步执行")


# ============================================================================
# WriteFileTool - 创建或覆盖文件
# ============================================================================

class WriteFileInput(BaseModel):
    """写入文件工具的输入参数"""
    file_path: str = Field(description="要写入的文件路径（相对或绝对路径）")
    content: str = Field(description="要写入的文件内容")


class WriteFileTool(BaseTool):
    """创建或覆盖文件的工具"""
    
    name: str = "write_file"
    description: str = """创建新文件或覆盖现有文件。
    输入应该包含两个参数：
    1. file_path: 文件路径（相对或绝对路径）
    2. content: 要写入的内容
    如果文件已存在，将被覆盖。
    示例输入: file_path="output.txt", content="Hello World"
    """
    args_schema: Type[BaseModel] = WriteFileInput
    
    # 内部工具实例
    _file_tool: Optional[BaseFileTool] = None
    
    def __init__(self, working_directory: str, max_file_size: int = 10 * 1024 * 1024,
                 allowed_formats: Optional[list] = None):
        """
        初始化写入文件工具
        
        Args:
            working_directory: 工作目录
            max_file_size: 最大文件大小（字节）
            allowed_formats: 允许的文件格式列表
        """
        super().__init__()
        object.__setattr__(self, '_file_tool', BaseFileTool(working_directory, max_file_size, allowed_formats))
    
    def _run(self, file_path: str, content: str) -> str:
        """
        执行文件写入
        
        Args:
            file_path: 文件路径
            content: 文件内容
            
        Returns:
            str: 成功消息或错误消息
        """
        try:
            # 验证路径
            valid, error_msg = self._file_tool.validate_path(file_path)
            if not valid:
                return f"错误: {error_msg}"
            
            # 验证文件格式
            valid, error_msg = self._file_tool.validate_file_format(file_path)
            if not valid:
                return f"错误: {error_msg}"
            
            # 检查内容大小
            content_size = len(content.encode('utf-8'))
            if content_size > self._file_tool.max_file_size:
                max_mb = self._file_tool.max_file_size / (1024 * 1024)
                actual_mb = content_size / (1024 * 1024)
                return f"错误: 内容大小 {actual_mb:.2f}MB 超过限制 {max_mb:.2f}MB"
            
            # 解析为绝对路径
            abs_path = self._file_tool._resolve_path(file_path)
            
            # 确保目录存在
            dir_path = os.path.dirname(abs_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            
            # 写入文件
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            file_size = os.path.getsize(abs_path)
            return f"成功: 文件 '{file_path}' 已写入，大小 {file_size} 字节"
            
        except Exception as e:
            return f"错误: 写入文件失败 - {str(e)}"
    
    async def _arun(self, file_path: str, content: str) -> str:
        """异步执行（暂不支持）"""
        raise NotImplementedError("WriteFileTool 不支持异步执行")


# ============================================================================
# ModifyFileTool - 修改文件内容
# ============================================================================

class ModifyFileInput(BaseModel):
    """修改文件工具的输入参数"""
    file_path: str = Field(description="要修改的文件路径（相对或绝对路径）")
    old_content: str = Field(description="要替换的旧内容")
    new_content: str = Field(description="替换后的新内容")


class ModifyFileTool(BaseTool):
    """修改文件内容的工具"""
    
    name: str = "modify_file"
    description: str = """修改文件中的内容。
    输入应该包含三个参数：
    1. file_path: 文件路径（相对或绝对路径）
    2. old_content: 要替换的旧内容（必须完全匹配）
    3. new_content: 替换后的新内容
    文件中所有匹配的旧内容都会被替换。
    示例输入: file_path="config.py", old_content="DEBUG = False", new_content="DEBUG = True"
    """
    args_schema: Type[BaseModel] = ModifyFileInput
    
    # 内部工具实例
    _file_tool: Optional[BaseFileTool] = None
    
    def __init__(self, working_directory: str, max_file_size: int = 10 * 1024 * 1024,
                 allowed_formats: Optional[list] = None):
        """
        初始化修改文件工具
        
        Args:
            working_directory: 工作目录
            max_file_size: 最大文件大小（字节）
            allowed_formats: 允许的文件格式列表
        """
        super().__init__()
        object.__setattr__(self, '_file_tool', BaseFileTool(working_directory, max_file_size, allowed_formats))
    
    def _run(self, file_path: str, old_content: str, new_content: str) -> str:
        """
        执行文件修改
        
        Args:
            file_path: 文件路径
            old_content: 旧内容
            new_content: 新内容
            
        Returns:
            str: 成功消息或错误消息
        """
        try:
            # 验证路径
            valid, error_msg = self._file_tool.validate_path(file_path)
            if not valid:
                return f"错误: {error_msg}"
            
            # 验证文件格式
            valid, error_msg = self._file_tool.validate_file_format(file_path)
            if not valid:
                return f"错误: {error_msg}"
            
            # 解析为绝对路径
            abs_path = self._file_tool._resolve_path(file_path)
            
            # 检查文件是否存在
            if not os.path.exists(abs_path):
                return f"错误: 文件 '{file_path}' 不存在"
            
            if not os.path.isfile(abs_path):
                return f"错误: '{file_path}' 不是一个文件"
            
            # 验证文件大小
            valid, error_msg = self._file_tool.validate_file_size(file_path)
            if not valid:
                return f"错误: {error_msg}"
            
            # 读取文件内容
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查旧内容是否存在
            if old_content not in content:
                return f"错误: 在文件 '{file_path}' 中未找到要替换的内容"
            
            # 替换内容
            modified_content = content.replace(old_content, new_content)
            count = content.count(old_content)
            
            # 检查修改后的内容大小
            modified_size = len(modified_content.encode('utf-8'))
            if modified_size > self._file_tool.max_file_size:
                max_mb = self._file_tool.max_file_size / (1024 * 1024)
                actual_mb = modified_size / (1024 * 1024)
                return f"错误: 修改后内容大小 {actual_mb:.2f}MB 超过限制 {max_mb:.2f}MB"
            
            # 写入修改后的内容
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            return f"成功: 文件 '{file_path}' 已修改，替换了 {count} 处内容"
            
        except UnicodeDecodeError:
            return f"错误: 文件 '{file_path}' 不是文本文件或编码不支持"
        except Exception as e:
            return f"错误: 修改文件失败 - {str(e)}"
    
    async def _arun(self, file_path: str, old_content: str, new_content: str) -> str:
        """异步执行（暂不支持）"""
        raise NotImplementedError("ModifyFileTool 不支持异步执行")


# ============================================================================
# ListFilesTool - 列出目录文件
# ============================================================================

class ListFilesInput(BaseModel):
    """列出文件工具的输入参数"""
    directory: str = Field(description="要列出文件的目录路径（相对或绝对路径），默认为当前工作目录", default=".")


class ListFilesTool(BaseTool):
    """列出目录文件的工具"""
    
    name: str = "list_files"
    description: str = """列出指定目录下的所有文件和子目录。
    输入应该是目录路径（相对或绝对路径）。
    如果不提供路径，将列出当前工作目录的内容。
    返回目录中的文件和子目录列表。
    示例输入: "." 或 "src" 或 "docs"
    """
    args_schema: Type[BaseModel] = ListFilesInput
    
    # 内部工具实例
    _file_tool: Optional[BaseFileTool] = None
    
    def __init__(self, working_directory: str, max_file_size: int = 10 * 1024 * 1024,
                 allowed_formats: Optional[list] = None):
        """
        初始化列出文件工具
        
        Args:
            working_directory: 工作目录
            max_file_size: 最大文件大小（字节）
            allowed_formats: 允许的文件格式列表
        """
        super().__init__()
        object.__setattr__(self, '_file_tool', BaseFileTool(working_directory, max_file_size, allowed_formats))
    
    def _run(self, directory: str = ".") -> str:
        """
        执行列出文件
        
        Args:
            directory: 目录路径
            
        Returns:
            str: 文件列表或错误消息
        """
        try:
            # 验证路径
            valid, error_msg = self._file_tool.validate_path(directory)
            if not valid:
                return f"错误: {error_msg}"
            
            # 解析为绝对路径
            abs_path = self._file_tool._resolve_path(directory)
            
            # 检查目录是否存在
            if not os.path.exists(abs_path):
                return f"错误: 目录 '{directory}' 不存在"
            
            if not os.path.isdir(abs_path):
                return f"错误: '{directory}' 不是一个目录"
            
            # 列出目录内容
            items = os.listdir(abs_path)
            
            if not items:
                return f"目录 '{directory}' 是空的"
            
            # 分类文件和目录
            files = []
            directories = []
            
            for item in sorted(items):
                item_path = os.path.join(abs_path, item)
                if os.path.isdir(item_path):
                    directories.append(f"📁 {item}/")
                else:
                    # 获取文件大小
                    try:
                        size = os.path.getsize(item_path)
                        if size < 1024:
                            size_str = f"{size}B"
                        elif size < 1024 * 1024:
                            size_str = f"{size / 1024:.1f}KB"
                        else:
                            size_str = f"{size / (1024 * 1024):.1f}MB"
                        files.append(f"📄 {item} ({size_str})")
                    except Exception:
                        files.append(f"📄 {item}")
            
            # 构建结果
            result = [f"目录 '{directory}' 的内容:\n"]
            
            if directories:
                result.append("子目录:")
                result.extend([f"  {d}" for d in directories])
                result.append("")
            
            if files:
                result.append("文件:")
                result.extend([f"  {f}" for f in files])
            
            result.append(f"\n总计: {len(directories)} 个目录, {len(files)} 个文件")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"错误: 列出文件失败 - {str(e)}"
    
    async def _arun(self, directory: str = ".") -> str:
        """异步执行（暂不支持）"""
        raise NotImplementedError("ListFilesTool 不支持异步执行")
