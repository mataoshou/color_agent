"""
测试系统上下文提供者
"""

import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.system_context import SystemContextProvider, SystemContext


def test_system_context_provider():
    """测试系统上下文提供者基本功能"""
    provider = SystemContextProvider()
    
    # 测试获取上下文
    context = provider.get_context()
    assert isinstance(context, SystemContext)
    assert context.working_directory is not None
    assert context.os_type is not None
    assert context.python_version is not None
    
    print("✓ SystemContextProvider 基本功能测试通过")
    
    # 测试工作目录
    working_dir = provider.get_working_directory()
    assert os.path.exists(working_dir)
    print(f"✓ 工作目录: {working_dir}")
    
    # 测试操作系统信息
    os_type, os_version = provider.get_os_info()
    print(f"✓ 操作系统: {os_type} {os_version}")
    
    # 测试 Python 版本
    python_version = provider.get_python_version()
    print(f"✓ Python 版本: {python_version}")
    
    # 测试 Prompt 文本生成
    prompt_text = context.to_prompt_text()
    assert "工作目录" in prompt_text
    assert "操作系统" in prompt_text
    print("✓ Prompt 文本生成成功")


if __name__ == "__main__":
    test_system_context_provider()
    print("\n所有测试通过！")
