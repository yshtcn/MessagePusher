"""
消息模型

定义消息的数据模型。
"""

import secrets
from typing import List, Optional, ClassVar

from .base_model import BaseModel


class Message(BaseModel):
    """
    消息模型类
    
    表示一条待发送或已发送的消息。
    """
    
    # 表名
    table_name: ClassVar[str] = "messages"
    
    # 字段定义
    fields: ClassVar[List[str]] = [
        "id", "api_token_id", "title", "content", "url", "url_content",
        "file_storage", "view_token", "created_at", "updated_at"
    ]
    
    def __init__(self, **kwargs):
        """
        初始化消息实例
        
        Args:
            **kwargs: 消息字段值
        """
        # 如果没有提供 view_token，则生成一个新的
        if "view_token" not in kwargs:
            kwargs["view_token"] = self.generate_view_token()
        
        super().__init__(**kwargs)
    
    @staticmethod
    def generate_view_token(length: int = 16) -> str:
        """
        生成随机查看令牌
        
        Args:
            length (int, optional): 令牌长度，默认为16
            
        Returns:
            str: 随机令牌
        """
        return secrets.token_hex(length // 2)
    
    def get_view_url(self, base_url: str = "") -> str:
        """
        获取消息查看 URL
        
        Args:
            base_url (str, optional): 基础 URL，默认为空
            
        Returns:
            str: 消息查看 URL
        """
        return f"{base_url}/view/{self.view_token}"
    
    def has_content(self) -> bool:
        """
        检查消息是否有内容
        
        Returns:
            bool: 消息是否有内容
        """
        return bool(self.title or self.content or self.url or self.url_content)
    
    def has_url(self) -> bool:
        """
        检查消息是否有 URL
        
        Returns:
            bool: 消息是否有 URL
        """
        return bool(self.url)
    
    def has_url_content(self) -> bool:
        """
        检查消息是否有 URL 内容
        
        Returns:
            bool: 消息是否有 URL 内容
        """
        return bool(self.url_content)
    
    def has_file_storage(self) -> bool:
        """
        检查消息是否有文件存储
        
        Returns:
            bool: 消息是否有文件存储
        """
        return bool(self.file_storage)
    
    @classmethod
    def find_by_view_token(cls, view_token: str) -> Optional['Message']:
        """
        根据查看令牌查找消息
        
        Args:
            view_token (str): 查看令牌
            
        Returns:
            Optional[Message]: 消息实例，如果不存在则返回None
        """
        return cls.find_one(view_token=view_token)
    
    @classmethod
    def find_by_api_token(cls, api_token_id: str) -> List['Message']:
        """
        根据 API 令牌 ID 查找消息
        
        Args:
            api_token_id (str): API 令牌 ID
            
        Returns:
            List[Message]: 消息列表
        """
        return cls.find(api_token_id=api_token_id) 