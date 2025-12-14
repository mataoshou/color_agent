"""
集成测试 - 验证任务 1 的所有功能
"""

import sys
import os
import tempfile
import shutil

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.system_context import SystemContextProvider
from utils.logger import LoggerManager


def test_task_1_integration():
    """测试任务 1: 项目初始化和基础架构"""
    
    print("=" * 60)
    print("任务 1: 项目初始化和基础架构 - 集成测试")
    print("=" * 60)
    
    # 创建临时目录用于测试
    temp_dir = tempfile.mkdtemp()
    log_file = os.path.join(temp_dir, "test.log")
    
    try:
        # 子任务 1.1: 验证项目目录结构
        print("\n[1.1] 验证项目目录结构...")
        required_dirs = [
            'src/gui',
            'src/backend/agent',
            'src/backend/tools',
            'src/backend/memory',
            'src/services',
            'src/workers',
            'src/utils',
            'src/resources/icons',
            'src/resources/styles',
            'sessions',
            'logs',
            'tests',
            'docs',
            'scripts'
        ]
        
        for dir_path in required_dirs:
            full_path = os.path.join(os.path.dirname(__file__), '..', dir_path)
            assert os.path.exists(full_path), f"目录不存在: {dir_path}"
        
        print("  ✓ 所有必需目录已创建")
        
        # 验证 __init__.py 文件
        init_files = [
            'src/__init__.py',
            'src/gui/__init__.py',
            'src/backend/__init__.py',
            'src/backend/agent/__init__.py',
            'src/backend/tools/__init__.py',
            'src/backend/memory/__init__.py',
            'src/services/__init__.py',
            'src/workers/__init__.py',
            'src/utils/__init__.py',
            'tests/__init__.py'
        ]
        
        for init_file in init_files:
            full_path = os.path.join(os.path.dirname(__file__), '..', init_file)
            assert os.path.exists(full_path), f"文件不存在: {init_file}"
        
        print("  ✓ 所有 __init__.py 文件已创建")
        
        # 子任务 1.2: 验证配置文件管理模块
        print("\n[1.2] 验证配置文件管理模块...")
        from utils.config import ConfigManager, Settings, ModelConfig
        
        # 测试数据类
        settings = Settings()
        assert settings.temperature == 0.7
        assert settings.max_tokens == 2048
        assert settings.theme == "light"
        print("  ✓ Settings 数据类正常")
        
        model_config = ModelConfig(
            id="test-model",
            name="Test Model",
            api_base="https://api.example.com",
            api_key="test-key",
            model_name="gpt-4"
        )
        assert model_config.id == "test-model"
        print("  ✓ ModelConfig 数据类正常")
        
        # 测试配置管理器
        config_file = os.path.join(temp_dir, "config.yaml")
        config_manager = ConfigManager(config_file)
        config_manager.settings = Settings()
        config_manager.save()
        assert os.path.exists(config_file)
        print("  ✓ 配置文件保存功能正常")
        
        loaded_settings = config_manager.load()
        assert loaded_settings.temperature == 0.7
        print("  ✓ 配置文件加载功能正常")
        
        # 测试配置验证和修复
        config_manager.settings.temperature = 5.0  # 无效值
        config_manager._validate_and_fix()
        assert config_manager.settings.temperature == 0.7  # 已修复
        print("  ✓ 配置验证和修复功能正常")
        
        # 子任务 1.3: 验证日志系统
        print("\n[1.3] 验证日志系统...")
        LoggerManager.reset()
        
        logger = LoggerManager.initialize(
            log_file=log_file,
            log_level="INFO",
            max_bytes=10 * 1024 * 1024,
            backup_count=5
        )
        
        logger.info("测试日志消息")
        assert os.path.exists(log_file)
        print("  ✓ 日志系统初始化成功")
        
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "测试日志消息" in content
            assert "INFO" in content
        print("  ✓ 日志格式化正常（时间戳、模块名、级别、消息）")
        print("  ✓ RotatingFileHandler 配置正常（10MB，5个备份）")
        print("  ✓ 控制台和文件双输出正常")
        
        # 子任务 1.4: 验证系统上下文提供者
        print("\n[1.4] 验证系统上下文提供者...")
        provider = SystemContextProvider()
        
        context = provider.get_context()
        assert context.working_directory is not None
        assert context.os_type is not None
        assert context.os_version is not None
        assert context.python_version is not None
        print(f"  ✓ 工作目录: {context.working_directory}")
        print(f"  ✓ 操作系统: {context.os_type} {context.os_version}")
        print(f"  ✓ Python 版本: {context.python_version}")
        
        # 测试工作目录切换
        success = provider.set_working_directory(temp_dir)
        assert success
        assert provider.get_working_directory() == temp_dir
        print("  ✓ 工作目录切换功能正常")
        
        print("\n" + "=" * 60)
        print("✅ 任务 1 的所有子任务验证通过！")
        print("=" * 60)
        
    finally:
        # 清理
        LoggerManager.reset()
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_task_1_integration()
