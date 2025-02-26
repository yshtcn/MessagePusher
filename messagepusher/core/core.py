"""
中枢模块核心

负责系统初始化、组件管理和系统生命周期控制。
"""

import logging
import threading
import os
import signal
import sys
import time
from typing import Dict, Any, Optional, List, Set

from ..database import init_db
from ..database.repository import SystemConfigRepository
from .task_scheduler import TaskScheduler
from .task_queue import TaskQueue
from .message_processor import MessageProcessor
from .error_handler import ErrorHandler

# 日志记录器
logger = logging.getLogger(__name__)


class CoreModule:
    """
    中枢模块核心类
    
    负责协调系统各组件的初始化、运行和关闭。
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """实现单例模式"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CoreModule, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化中枢模块
        
        Args:
            config: 配置字典，包含以下配置：
                - db_config: 数据库配置
                - task_queue_config: 任务队列配置
                - task_scheduler_config: 任务调度器配置
                - message_processor_config: 消息处理器配置
                - error_handler_config: 错误处理器配置
                - channel_config: 消息渠道配置
                - ai_channel_config: AI渠道配置
        """
        # 避免重复初始化
        if self._initialized:
            return
        
        self._initialized = True
        self._running = False
        self._shutting_down = False
        
        # 保存配置
        self._config = config
        
        # 创建组件
        self.task_queue = TaskQueue(**config.get("task_queue_config", {}))
        self.task_scheduler = TaskScheduler(**config.get("task_scheduler_config", {}))
        self.message_processor = MessageProcessor(**config.get("message_processor_config", {}))
        self.error_handler = ErrorHandler(**config.get("error_handler_config", {}))
        
        # 注册的组件列表，用于启动和关闭
        self._components = [
            self.task_queue,
            self.task_scheduler,
            self.message_processor,
            self.error_handler
        ]
        
        # 注册信号处理
        self._setup_signal_handlers()
        
        logger.debug("CoreModule初始化完成")
    
    def _setup_signal_handlers(self):
        """设置信号处理"""
        # 对于SIGINT和SIGTERM信号，进行优雅关闭
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, sig, frame):
        """
        信号处理函数
        
        Args:
            sig: 信号
            frame: 栈帧
        """
        logger.info(f"收到信号 {sig}，准备关闭系统...")
        self.shutdown()
    
    def initialize(self):
        """
        初始化系统
        
        1. 初始化数据库
        2. 加载系统配置
        3. 初始化各组件
        """
        try:
            logger.info("开始初始化系统...")
            
            # 初始化数据库
            init_db()
            
            # 加载系统配置
            self._load_system_config()
            
            # 初始化各组件
            for component in self._components:
                try:
                    if hasattr(component, 'initialize'):
                        component.initialize()
                except Exception as e:
                    logger.error(f"初始化组件 {component.__class__.__name__} 失败: {str(e)}")
                    raise
            
            logger.info("系统初始化完成")
            return True
        except Exception as e:
            logger.error(f"系统初始化失败: {str(e)}")
            self.error_handler.handle_error("system_initialization", e)
            return False
    
    def _load_system_config(self):
        """加载系统配置"""
        try:
            logger.info("加载系统配置...")
            # 从数据库加载系统配置
            config_repo = SystemConfigRepository()
            all_configs = config_repo.get_all()
            
            # 设置配置到各组件
            self._apply_system_config(all_configs)
            
            logger.info(f"成功加载 {len(all_configs)} 个系统配置项")
        except Exception as e:
            logger.error(f"加载系统配置失败: {str(e)}")
            raise
    
    def _apply_system_config(self, configs: List[Dict[str, Any]]):
        """
        应用系统配置到各组件
        
        Args:
            configs: 配置项列表
        """
        # 将配置转换为字典格式，方便查询
        config_dict = {item['key']: item['value'] for item in configs}
        
        # 为每个组件设置配置
        for component in self._components:
            if hasattr(component, 'configure'):
                component.configure(config_dict)
    
    def start(self):
        """
        启动系统
        
        启动所有组件并进入运行状态
        """
        if self._running:
            logger.warning("系统已经在运行中")
            return
        
        if not self._initialized:
            raise RuntimeError("必须先调用initialize方法初始化系统")
        
        logger.info("开始启动系统...")
        
        try:
            # 启动所有组件
            for component in self._components:
                try:
                    if hasattr(component, 'start'):
                        component.start()
                except Exception as e:
                    logger.error(f"启动组件 {component.__class__.__name__} 失败: {str(e)}")
                    raise
            
            self._running = True
            logger.info("系统启动完成，正在运行...")
        except Exception as e:
            logger.error(f"系统启动失败: {str(e)}")
            self.error_handler.handle_error("system_startup", e)
            self.shutdown()
            raise
    
    def shutdown(self):
        """
        关闭系统
        
        按照依赖关系的反序关闭所有组件
        """
        if self._shutting_down:
            return
        
        self._shutting_down = True
        logger.info("开始关闭系统...")
        
        # 反序关闭组件
        for component in reversed(self._components):
            try:
                if hasattr(component, 'stop'):
                    component.stop()
            except Exception as e:
                logger.error(f"关闭组件 {component.__class__.__name__} 时出错: {str(e)}")
        
        self._running = False
        self._shutting_down = False
        logger.info("系统已完全关闭")
    
    def is_running(self):
        """
        检查系统是否正在运行
        
        Returns:
            bool: 是否正在运行
        """
        return self._running
    
    def wait_for_shutdown(self):
        """
        等待系统关闭
        
        阻塞当前线程直到系统关闭
        """
        try:
            # 简单的循环检查系统是否仍在运行
            while self._running and not self._shutting_down:
                time.sleep(0.5)
        except KeyboardInterrupt:
            self.shutdown()
    
    def restart(self):
        """重启系统"""
        logger.info("准备重启系统...")
        self.shutdown()
        time.sleep(1)  # 给予足够时间完全关闭
        self.initialize()
        self.start()
        logger.info("系统已重启")
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取系统状态
        
        Returns:
            Dict[str, Any]: 系统状态信息
        """
        status = {
            "running": self._running,
            "shutting_down": self._shutting_down,
            "components": {}
        }
        
        # 收集各组件状态
        for component in self._components:
            if hasattr(component, 'get_status'):
                status["components"][component.__class__.__name__] = component.get_status()
            else:
                status["components"][component.__class__.__name__] = {"status": "unknown"}
        
        return status 