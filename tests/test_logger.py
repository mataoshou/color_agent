"""
测试日志系统
"""

import sys
import os
import tempfile
import shutil

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.logger import LoggerManager, get_logger, log_exception, log_operation


def test_logger():
    """测试日志系统基本功能"""
    # 创建临时日志目录
    temp_dir = tempfile.mkdtemp()
    log_file = os.path.join(temp_dir, "test.log")
    
    try:
        # 重置日志系统
        LoggerManager.reset()
        
        # 初始化日志系统
        logger = LoggerManager.initialize(
            log_file=log_file,
            log_level="INFO"
        )
        
        print("✓ 日志系统初始化成功")
        
        # 测试不同级别的日志
        logger.debug("这是 DEBUG 日志")
        logger.info("这是 INFO 日志")
        logger.warning("这是 WARNING 日志")
        logger.error("这是 ERROR 日志")
        
        print("✓ 日志记录成功")
        
        # 测试便捷函数
        logger2 = get_logger()
        assert logger2 == logger
        print("✓ get_logger() 函数正常")
        
        # 测试操作日志
        log_operation(logger, "测试操作", param1="value1", param2="value2")
        print("✓ log_operation() 函数正常")
        
        # 测试异常日志
        try:
            raise ValueError("测试异常")
        except Exception as e:
            log_exception(logger, "捕获到异常", e)
        print("✓ log_exception() 函数正常")
        
        # 验证日志文件存在
        assert os.path.exists(log_file)
        print(f"✓ 日志文件已创建: {log_file}")
        
        # 读取日志文件内容
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "INFO" in content
            assert "WARNING" in content
            assert "ERROR" in content
        print("✓ 日志文件内容正确")
        
    finally:
        # 清理临时目录
        LoggerManager.reset()
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_logger()
    print("\n所有测试通过！")
