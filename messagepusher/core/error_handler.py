"""
错误处理器模块

负责处理系统中的各种错误，提供错误记录、通知和恢复机制。
"""

import logging
import threading
import time
from typing import Dict, Any, List, Callable, Optional
from enum import Enum, auto
from datetime import datetime

# 日志记录器
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = auto()      # 低严重度
    MEDIUM = auto()   # 中等严重度
    HIGH = auto()     # 高严重度
    CRITICAL = auto() # 严重错误


class ErrorHandler:
    """
    错误处理器
    
    负责处理系统中的各种错误，提供错误记录、通知和恢复机制。
    """
    
    def __init__(self, **config):
        """
        初始化错误处理器
        
        Args:
            **config: 配置参数
                - max_error_history: 最大错误历史记录数，默认为1000
                - cleanup_interval: 清理间隔时间，默认为3600秒
                - notification_threshold: 通知阈值，默认为{"low": 100, "medium": 10, "high": 1, "critical": 1}
        """
        # 默认配置
        self._config = {
            "max_error_history": 1000,  # 最大错误历史记录数
            "cleanup_interval": 3600,   # 错误清理间隔，默认1小时
            "notification_threshold": {  # 通知阈值
                ErrorSeverity.LOW: 100,      # 100个低严重度错误
                ErrorSeverity.MEDIUM: 10,     # 10个中等严重度错误
                ErrorSeverity.HIGH: 1,        # 1个高严重度错误
                ErrorSeverity.CRITICAL: 1     # 1个严重错误
            }
        }
        
        # 更新配置
        if "notification_threshold" in config:
            thresholds = config.pop("notification_threshold")
            for severity in ErrorSeverity:
                if severity.name.lower() in thresholds:
                    self._config["notification_threshold"][severity] = int(thresholds[severity.name.lower()])
        self._config.update(config)
        
        # 错误历史记录
        self._error_history: List[Dict[str, Any]] = []
        
        # 错误计数器
        self._error_counters = {
            ErrorSeverity.LOW: 0,
            ErrorSeverity.MEDIUM: 0,
            ErrorSeverity.HIGH: 0,
            ErrorSeverity.CRITICAL: 0
        }
        
        # 错误处理器锁
        self._lock = threading.RLock()
        
        # 错误处理回调函数
        self._error_callbacks: Dict[str, List[Callable]] = {}
        
        logger.debug("ErrorHandler初始化完成")
    
    def handle_error(self, error_type: str, error: Exception, severity: ErrorSeverity = ErrorSeverity.MEDIUM, context: Optional[Dict[str, Any]] = None):
        """
        处理错误
        
        Args:
            error_type: 错误类型
            error: 异常对象
            severity: 错误严重程度，默认为中等
            context: 错误上下文信息，默认为None
        """
        with self._lock:
            # 创建错误记录
            error_record = {
                "id": str(time.time()),
                "type": error_type,
                "message": str(error),
                "severity": severity.name,
                "timestamp": datetime.now().isoformat(),
                "context": context or {}
            }
            
            # 添加到历史记录
            self._error_history.append(error_record)
            
            # 如果超过最大记录数，删除最旧的记录
            if len(self._error_history) > self._config["max_error_history"]:
                self._error_history.pop(0)
            
            # 增加计数器
            self._error_counters[severity] += 1
            
            # 记录日志
            log_message = f"错误: {error_type} - {str(error)}"
            if context:
                log_message += f", 上下文: {context}"
            
            if severity == ErrorSeverity.CRITICAL:
                logger.critical(log_message, exc_info=True)
            elif severity == ErrorSeverity.HIGH:
                logger.error(log_message, exc_info=True)
            elif severity == ErrorSeverity.MEDIUM:
                logger.warning(log_message)
            else:
                logger.info(log_message)
            
            # 检查是否需要发送通知
            self._check_notification(severity, error_record)
            
            # 调用错误处理回调
            self._call_error_callbacks(error_type, error_record)
    
    def get_error_history(self) -> List[Dict[str, Any]]:
        """
        获取错误历史记录
        
        Returns:
            List[Dict[str, Any]]: 错误历史记录
        """
        with self._lock:
            return self._error_history.copy()
    
    def _check_notification(self, severity: ErrorSeverity, error_record: Dict[str, Any]):
        """
        检查是否需要发送通知
        
        Args:
            severity: 错误严重程度
            error_record: 错误记录
        """
        threshold = self._config["notification_threshold"].get(severity)
        if threshold is None:
            return
        
        if self._error_counters[severity] >= threshold:
            # TODO: 发送通知
            logger.warning(f"错误计数达到阈值: {severity.name} = {self._error_counters[severity]}")
            
            # 重置计数器
            self._error_counters[severity] = 0
    
    def register_error_callback(self, error_type: str, callback: Callable[[Dict[str, Any]], None]):
        """
        注册错误处理回调函数
        
        Args:
            error_type: 错误类型
            callback: 回调函数
        """
        with self._lock:
            if error_type not in self._error_callbacks:
                self._error_callbacks[error_type] = []
            
            self._error_callbacks[error_type].append(callback)
            logger.debug(f"注册错误处理回调: {error_type}")
    
    def _call_error_callbacks(self, error_type: str, error_record: Dict[str, Any]):
        """
        调用错误处理回调函数
        
        Args:
            error_type: 错误类型
            error_record: 错误记录
        """
        callbacks = self._error_callbacks.get(error_type, [])
        for callback in callbacks:
            try:
                callback(error_record)
            except Exception as e:
                logger.error(f"调用错误处理回调失败: {str(e)}")
    
    def clear_error_history(self):
        """清空错误历史记录"""
        with self._lock:
            self._error_history.clear()
            logger.debug("清空错误历史记录")
    
    def reset_error_counters(self):
        """重置错误计数器"""
        with self._lock:
            for severity in ErrorSeverity:
                self._error_counters[severity] = 0
            logger.debug("重置错误计数器")
    
    def initialize(self):
        """初始化错误处理器"""
        logger.info("初始化错误处理器...")
    
    def start(self):
        """启动错误处理器"""
        logger.info("启动错误处理器...")
    
    def stop(self):
        """停止错误处理器"""
        logger.info("停止错误处理器...")
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取错误处理器状态
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        with self._lock:
            return {
                "error_counts": {
                    severity.name: count
                    for severity, count in self._error_counters.items()
                },
                "error_history_size": len(self._error_history)
            } 