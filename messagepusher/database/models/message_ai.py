"""
消息 AI 处理模型

定义消息的 AI 处理结果。
"""

from typing import List, Optional, ClassVar

from .base_model import BaseModel


class MessageAI(BaseModel):
    """
    消息 AI 处理模型类
    
    表示消息的 AI 处理结果。
    """
    
    # 表名
    table_name: ClassVar[str] = "message_ai"
    
    # 字段定义
    fields: ClassVar[List[str]] = [
        "id", "message_id", "ai_channel_id", "prompt", "result",
        "status", "error", "processed_at", "created_at", "updated_at"
    ]
    
    # 状态
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    
    def __init__(self, **kwargs):
        """
        初始化消息 AI 处理实例
        
        Args:
            **kwargs: 消息 AI 处理字段值
        """
        super().__init__(**kwargs)
        
        # 设置默认值
        if self.status is None:
            self.status = self.STATUS_PENDING
    
    def is_pending(self) -> bool:
        """
        检查是否处于等待状态
        
        Returns:
            bool: 是否处于等待状态
        """
        return self.status == self.STATUS_PENDING
    
    def is_processing(self) -> bool:
        """
        检查是否处于处理中状态
        
        Returns:
            bool: 是否处于处理中状态
        """
        return self.status == self.STATUS_PROCESSING
    
    def is_success(self) -> bool:
        """
        检查是否处理成功
        
        Returns:
            bool: 是否处理成功
        """
        return self.status == self.STATUS_SUCCESS
    
    def is_failed(self) -> bool:
        """
        检查是否处理失败
        
        Returns:
            bool: 是否处理失败
        """
        return self.status == self.STATUS_FAILED
    
    def mark_as_processing(self) -> bool:
        """
        标记为处理中状态
        
        Returns:
            bool: 操作是否成功
        """
        self.status = self.STATUS_PROCESSING
        return self.save()
    
    def mark_as_success(self, result: str, processed_at: str = None) -> bool:
        """
        标记为处理成功状态
        
        Args:
            result (str): 处理结果
            processed_at (str, optional): 处理时间，如果为None则使用当前时间
            
        Returns:
            bool: 操作是否成功
        """
        self.status = self.STATUS_SUCCESS
        self.result = result
        
        if processed_at is None:
            import datetime
            processed_at = datetime.datetime.now().isoformat()
        
        self.processed_at = processed_at
        return self.save()
    
    def mark_as_failed(self, error: str = None) -> bool:
        """
        标记为处理失败状态
        
        Args:
            error (str, optional): 错误信息
            
        Returns:
            bool: 操作是否成功
        """
        self.status = self.STATUS_FAILED
        self.error = error
        return self.save()
    
    @classmethod
    def find_by_message(cls, message_id: str) -> List['MessageAI']:
        """
        根据消息 ID 查找消息 AI 处理
        
        Args:
            message_id (str): 消息 ID
            
        Returns:
            List[MessageAI]: 消息 AI 处理列表
        """
        return cls.find(message_id=message_id)
    
    @classmethod
    def find_by_ai_channel(cls, ai_channel_id: str) -> List['MessageAI']:
        """
        根据 AI 渠道 ID 查找消息 AI 处理
        
        Args:
            ai_channel_id (str): AI 渠道 ID
            
        Returns:
            List[MessageAI]: 消息 AI 处理列表
        """
        return cls.find(ai_channel_id=ai_channel_id)
    
    @classmethod
    def find_by_status(cls, status: str) -> List['MessageAI']:
        """
        根据状态查找消息 AI 处理
        
        Args:
            status (str): 状态
            
        Returns:
            List[MessageAI]: 消息 AI 处理列表
        """
        return cls.find(status=status)
    
    @classmethod
    def find_pending(cls) -> List['MessageAI']:
        """
        查找所有等待处理的消息 AI 处理
        
        Returns:
            List[MessageAI]: 等待处理的消息 AI 处理列表
        """
        return cls.find_by_status(cls.STATUS_PENDING) 