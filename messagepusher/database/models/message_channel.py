"""
消息渠道关联模型

定义消息与渠道的关联关系和发送状态。
"""

from typing import List, Optional, ClassVar

from .base_model import BaseModel


class MessageChannel(BaseModel):
    """
    消息渠道关联模型类
    
    表示消息与渠道的关联关系和发送状态。
    """
    
    # 表名
    table_name: ClassVar[str] = "message_channels"
    
    # 字段定义
    fields: ClassVar[List[str]] = [
        "id", "message_id", "channel_id", "status", "error",
        "sent_at", "created_at", "updated_at"
    ]
    
    # 状态
    STATUS_PENDING = "pending"
    STATUS_SENDING = "sending"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    
    def __init__(self, **kwargs):
        """
        初始化消息渠道关联实例
        
        Args:
            **kwargs: 消息渠道关联字段值
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
    
    def is_sending(self) -> bool:
        """
        检查是否处于发送中状态
        
        Returns:
            bool: 是否处于发送中状态
        """
        return self.status == self.STATUS_SENDING
    
    def is_success(self) -> bool:
        """
        检查是否发送成功
        
        Returns:
            bool: 是否发送成功
        """
        return self.status == self.STATUS_SUCCESS
    
    def is_failed(self) -> bool:
        """
        检查是否发送失败
        
        Returns:
            bool: 是否发送失败
        """
        return self.status == self.STATUS_FAILED
    
    def mark_as_sending(self) -> bool:
        """
        标记为发送中状态
        
        Returns:
            bool: 操作是否成功
        """
        self.status = self.STATUS_SENDING
        return self.save()
    
    def mark_as_success(self, sent_at: str = None) -> bool:
        """
        标记为发送成功状态
        
        Args:
            sent_at (str, optional): 发送时间，如果为None则使用当前时间
            
        Returns:
            bool: 操作是否成功
        """
        self.status = self.STATUS_SUCCESS
        
        if sent_at is None:
            import datetime
            sent_at = datetime.datetime.now().isoformat()
        
        self.sent_at = sent_at
        return self.save()
    
    def mark_as_failed(self, error: str = None) -> bool:
        """
        标记为发送失败状态
        
        Args:
            error (str, optional): 错误信息
            
        Returns:
            bool: 操作是否成功
        """
        self.status = self.STATUS_FAILED
        self.error = error
        return self.save()
    
    @classmethod
    def find_by_message(cls, message_id: str) -> List['MessageChannel']:
        """
        根据消息 ID 查找消息渠道关联
        
        Args:
            message_id (str): 消息 ID
            
        Returns:
            List[MessageChannel]: 消息渠道关联列表
        """
        return cls.find(message_id=message_id)
    
    @classmethod
    def find_by_channel(cls, channel_id: str) -> List['MessageChannel']:
        """
        根据渠道 ID 查找消息渠道关联
        
        Args:
            channel_id (str): 渠道 ID
            
        Returns:
            List[MessageChannel]: 消息渠道关联列表
        """
        return cls.find(channel_id=channel_id)
    
    @classmethod
    def find_by_status(cls, status: str) -> List['MessageChannel']:
        """
        根据状态查找消息渠道关联
        
        Args:
            status (str): 状态
            
        Returns:
            List[MessageChannel]: 消息渠道关联列表
        """
        return cls.find(status=status)
    
    @classmethod
    def find_pending(cls) -> List['MessageChannel']:
        """
        查找所有等待发送的消息渠道关联
        
        Returns:
            List[MessageChannel]: 等待发送的消息渠道关联列表
        """
        return cls.find_by_status(cls.STATUS_PENDING) 