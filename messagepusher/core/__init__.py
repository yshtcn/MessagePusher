"""
MessagePusher 中枢模块

负责系统的核心控制，包括系统初始化、任务调度、消息处理流程协调和错误处理。
"""

from .core import CoreModule
from .task_scheduler import TaskScheduler
from .message_processor import MessageProcessor
from .error_handler import ErrorHandler
from .task_queue import TaskQueue

# 核心模块实例
_core_module = None

def init_core(app=None):
    """
    初始化核心模块
    
    Args:
        app: Flask应用实例，可选
    
    Returns:
        CoreModule: 核心模块实例
    """
    global _core_module
    
    # 如果已经初始化，则直接返回
    if _core_module is not None:
        return _core_module
    
    # 创建配置
    config = {}
    if app is not None:
        # 从Flask应用配置中提取核心模块配置
        config = {
            "task_queue_config": app.config.get("TASK_QUEUE", {}),
            "task_scheduler_config": app.config.get("TASK_SCHEDULER", {}),
            "message_processor_config": app.config.get("MESSAGE_PROCESSOR", {}),
            "error_handler_config": app.config.get("ERROR_HANDLER", {})
        }
    
    # 创建核心模块实例
    _core_module = CoreModule(config)
    
    # 初始化核心模块
    _core_module.initialize()
    
    return _core_module

def get_core_module():
    """
    获取核心模块实例
    
    Returns:
        CoreModule: 核心模块实例
    """
    global _core_module
    if _core_module is None:
        _core_module = init_core()
    return _core_module

__all__ = [
    'CoreModule',
    'TaskScheduler',
    'MessageProcessor',
    'ErrorHandler',
    'TaskQueue',
    'init_core',
    'get_core_module',
] 