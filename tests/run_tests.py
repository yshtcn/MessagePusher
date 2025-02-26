"""
测试运行脚本

执行所有测试用例。
"""

import unittest
import sys
import os
import logging

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# 导入测试模块
from .test_core import (
    TestTaskQueue,
    TestTaskScheduler,
    TestMessageProcessor,
    TestErrorHandler,
    TestCoreModule
)

def run_tests():
    """运行所有测试"""
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加测试用例
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTaskQueue))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTaskScheduler))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMessageProcessor))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestErrorHandler))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCoreModule))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1) 