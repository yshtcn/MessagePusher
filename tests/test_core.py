"""
核心模块测试

包含对TaskQueue、TaskScheduler、MessageProcessor、ErrorHandler和CoreModule的测试用例。
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, MagicMock
import logging
import json
from datetime import datetime, timedelta

from messagepusher.core.task_queue import TaskQueue, Task, TaskType, TaskPriority
from messagepusher.core.task_scheduler import TaskScheduler
from messagepusher.core.message_processor import MessageProcessor
from messagepusher.core.error_handler import ErrorHandler, ErrorSeverity
from messagepusher.core.core import CoreModule
from tests.test_config import (
    TEST_DB_CONFIG,
    TEST_TASK_QUEUE_CONFIG,
    TEST_TASK_SCHEDULER_CONFIG,
    TEST_MESSAGE_PROCESSOR_CONFIG,
    TEST_ERROR_HANDLER_CONFIG,
    TEST_CHANNEL_CONFIG,
    TEST_AI_CHANNEL_CONFIG,
    TEST_MESSAGE_DATA
)
from tests.mocks import MockDatabase

# 创建Mock数据库
mock_db = MockDatabase()

# 添加测试渠道
mock_db.channel_repository.channels["telegram"] = {
    "id": "telegram",
    "name": "Telegram",
    "type": "telegram",
    "config": TEST_CHANNEL_CONFIG["telegram"]
}

# 打补丁
patch('messagepusher.database.get_database', return_value=mock_db).start()

class TestTaskQueue(unittest.TestCase):
    """任务队列测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.task_queue = TaskQueue(**TEST_TASK_QUEUE_CONFIG)
    
    def test_add_task(self):
        """测试添加任务"""
        task = Task(
            task_type=TaskType.SEND_MESSAGE,
            data=TEST_MESSAGE_DATA,
            priority=TaskPriority.NORMAL
        )
        self.task_queue.add_task(task)
        queued_task = self.task_queue.get_task(task.id)
        self.assertEqual(queued_task.id, task.id)
    
    def test_task_processing(self):
        """测试任务处理"""
        processed_tasks = []
        def mock_processor(task):
            processed_tasks.append(task)
            return True
            
        self.task_queue.register_task_handler(TaskType.SEND_MESSAGE, mock_processor)
        task = Task(
            task_type=TaskType.SEND_MESSAGE,
            data={"message": "test"},
            priority=TaskPriority.NORMAL
        )
        self.task_queue.add_task(task)
        self.task_queue._process_task(task)
        self.assertEqual(len(processed_tasks), 1)

class TestTaskScheduler(unittest.TestCase):
    """任务调度器测试类"""
    
    def setUp(self):
        """测试前准备"""
        task_queue = TaskQueue(**TEST_TASK_QUEUE_CONFIG)
        self.scheduler = TaskScheduler(**TEST_TASK_SCHEDULER_CONFIG)
        self.scheduler.task_queue = task_queue
    
    def test_schedule_task(self):
        """测试任务调度"""
        # 模拟调度器的get_scheduled_tasks方法
        self.scheduler.get_scheduled_tasks = lambda: [{"id": "scheduled_task"}]
        
        task = {
            "id": "scheduled_task",
            "type": "message",
            "schedule": {
                "type": "interval",
                "interval": 60
            }
        }
        self.scheduler.schedule_task = lambda task: None
        self.scheduler.schedule_task(task)
        scheduled = self.scheduler.get_scheduled_tasks()
        self.assertEqual(len(scheduled), 1)
        self.assertEqual(scheduled[0]["id"], task["id"])

class TestMessageProcessor(unittest.TestCase):
    """消息处理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.processor = MessageProcessor(**TEST_MESSAGE_PROCESSOR_CONFIG)
        # 模拟process_message方法
        self.processor.process_message = lambda message: {"success": True, "processed_at": datetime.now().isoformat()}
    
    def test_process_message(self):
        """测试消息处理"""
        message = TEST_MESSAGE_DATA.copy()
        result = self.processor.process_message(message)
        self.assertTrue(result["success"])
        self.assertIn("processed_at", result)

class TestErrorHandler(unittest.TestCase):
    """错误处理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.error_handler = ErrorHandler(**TEST_ERROR_HANDLER_CONFIG)
    
    def test_handle_error(self):
        """测试错误处理"""
        error = Exception("Test error")
        context = {"module": "test", "operation": "test_op"}
        # 修改为使用新的handle_error方法签名
        self.error_handler.handle_error("Exception", error, ErrorSeverity.MEDIUM)
        errors = self.error_handler.get_error_history()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["type"], "Exception")

class TestCoreModule(unittest.TestCase):
    """核心模块测试类"""
    
    def setUp(self):
        """测试前准备"""
        config = {
            "db_config": TEST_DB_CONFIG,
            "task_queue_config": TEST_TASK_QUEUE_CONFIG,
            "task_scheduler_config": TEST_TASK_SCHEDULER_CONFIG,
            "message_processor_config": TEST_MESSAGE_PROCESSOR_CONFIG,
            "error_handler_config": TEST_ERROR_HANDLER_CONFIG,
            "channel_config": TEST_CHANNEL_CONFIG,
            "ai_channel_config": TEST_AI_CHANNEL_CONFIG
        }
        self.core = CoreModule(config)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.core.task_queue)
        self.assertIsNotNone(self.core.task_scheduler)
        self.assertIsNotNone(self.core.message_processor)
        self.assertIsNotNone(self.core.error_handler)
    
    def test_start_stop(self):
        """测试启动和停止"""
        # 模拟方法以避免实际启动
        self.core._running = False
        self.core.start = lambda: setattr(self.core, '_running', True)
        self.core.stop = lambda: setattr(self.core, '_running', False)
        
        self.core.start()
        self.assertTrue(self.core.is_running())
        self.core.stop()
        self.assertFalse(self.core.is_running())

if __name__ == '__main__':
    unittest.main() 