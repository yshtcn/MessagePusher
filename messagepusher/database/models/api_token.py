"""
API 令牌模型

定义 API 访问令牌的数据模型。
"""

import json
import secrets
from typing import Dict, Any, List, Optional, ClassVar

from .base_model import BaseModel


class APIToken(BaseModel):
    """
    API 令牌模型类
    
    表示一个 API 访问令牌。
    """
    
    # 表名
    table_name: ClassVar[str] = "api_tokens"
    
    # 字段定义
    fields: ClassVar[List[str]] = [
        "id", "name", "token", "default_channels", "default_ai",
        "created_at", "updated_at", "expires_at", "status"
    ]
    
    # JSON字段
    json_fields: ClassVar[List[str]] = ["default_channels"]
    
    # 状态
    STATUS_ENABLED = "enabled"
    STATUS_DISABLED = "disabled"
    
    def __init__(self, **kwargs):
        """
        初始化 API 令牌实例
        
        Args:
            **kwargs: API 令牌字段值
        """
        # 如果没有提供 token，则生成一个新的
        if "token" not in kwargs:
            kwargs["token"] = self.generate_token()
        
        super().__init__(**kwargs)
        
        # 设置默认值
        if self.status is None:
            self.status = self.STATUS_ENABLED
        
        if self.default_channels is None:
            self.default_channels = "[]"
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """
        生成随机令牌
        
        Args:
            length (int, optional): 令牌长度，默认为32
            
        Returns:
            str: 随机令牌
        """
        return secrets.token_hex(length // 2)
    
    @property
    def default_channels_list(self) -> List[str]:
        """
        获取默认渠道 ID 列表
        
        Returns:
            List[str]: 默认渠道 ID 列表
        """
        if not self.default_channels:
            return []
        
        if isinstance(self.default_channels, str):
            try:
                return json.loads(self.default_channels)
            except json.JSONDecodeError:
                return []
        elif isinstance(self.default_channels, list):
            return self.default_channels
        return []
    
    def set_default_channels(self, channel_ids: List[str]) -> None:
        """
        设置默认渠道 ID 列表
        
        Args:
            channel_ids (List[str]): 渠道 ID 列表
        """
        self.default_channels = json.dumps(channel_ids)
    
    def is_enabled(self) -> bool:
        """
        检查 API 令牌是否启用
        
        Returns:
            bool: API 令牌是否启用
        """
        return self.status == self.STATUS_ENABLED
    
    def is_expired(self) -> bool:
        """
        检查 API 令牌是否过期
        
        Returns:
            bool: API 令牌是否过期
        """
        if not self.expires_at:
            return False
        
        import datetime
        now = datetime.datetime.now()
        
        # 将字符串转换为日期时间对象
        if isinstance(self.expires_at, str):
            try:
                expires_at = datetime.datetime.fromisoformat(self.expires_at)
                return now > expires_at
            except ValueError:
                return False
        
        return False
    
    def is_valid(self) -> bool:
        """
        检查 API 令牌是否有效（启用且未过期）
        
        Returns:
            bool: API 令牌是否有效
        """
        return self.is_enabled() and not self.is_expired()
    
    @classmethod
    def find_by_token(cls, token: str) -> Optional['APIToken']:
        """
        根据令牌值查找 API 令牌
        
        Args:
            token (str): 令牌值
            
        Returns:
            Optional[APIToken]: API 令牌实例，如果不存在则返回None
        """
        return cls.find_one(token=token)
    
    @classmethod
    def find_valid(cls) -> List['APIToken']:
        """
        查找所有有效的 API 令牌（启用且未过期）
        
        Returns:
            List[APIToken]: 有效的 API 令牌列表
        """
        # 注意：这里只能过滤启用状态，过期状态需要在应用层处理
        return [token for token in cls.find(status=cls.STATUS_ENABLED) if not token.is_expired()] 