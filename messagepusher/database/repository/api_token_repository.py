"""
API 令牌仓库

封装 API 令牌相关的复杂数据库操作。
"""

import json
from typing import Dict, List, Optional, Any

from ..models.api_token import APIToken


class APITokenRepository:
    """
    API 令牌仓库类
    
    封装 API 令牌相关的复杂数据库操作。
    """
    
    @staticmethod
    def create_token(name: str, default_channels: Optional[List[str]] = None,
                    default_ai: Optional[str] = None, expires_at: Optional[str] = None) -> APIToken:
        """
        创建 API 令牌
        
        Args:
            name (str): 令牌名称
            default_channels (Optional[List[str]], optional): 默认渠道 ID 列表
            default_ai (Optional[str], optional): 默认 AI 渠道 ID
            expires_at (Optional[str], optional): 过期时间
            
        Returns:
            APIToken: 创建的 API 令牌实例
        """
        token = APIToken(
            name=name,
            default_channels=json.dumps(default_channels) if default_channels else "[]",
            default_ai=default_ai,
            expires_at=expires_at,
            status=APIToken.STATUS_ENABLED
        )
        token.save()
        return token
    
    @staticmethod
    def update_token(token_id: str, name: Optional[str] = None,
                    default_channels: Optional[List[str]] = None,
                    default_ai: Optional[str] = None,
                    expires_at: Optional[str] = None,
                    status: Optional[str] = None) -> Optional[APIToken]:
        """
        更新 API 令牌
        
        Args:
            token_id (str): 令牌 ID
            name (Optional[str], optional): 令牌名称
            default_channels (Optional[List[str]], optional): 默认渠道 ID 列表
            default_ai (Optional[str], optional): 默认 AI 渠道 ID
            expires_at (Optional[str], optional): 过期时间
            status (Optional[str], optional): 令牌状态
            
        Returns:
            Optional[APIToken]: 更新后的 API 令牌实例，如果令牌不存在则返回 None
        """
        token = APIToken.get(token_id)
        if not token:
            return None
        
        if name is not None:
            token.name = name
        
        if default_channels is not None:
            token.default_channels = json.dumps(default_channels)
        
        if default_ai is not None:
            token.default_ai = default_ai
        
        if expires_at is not None:
            token.expires_at = expires_at
        
        if status is not None:
            token.status = status
        
        token.save()
        return token
    
    @staticmethod
    def delete_token(token_id: str) -> bool:
        """
        删除 API 令牌
        
        Args:
            token_id (str): 令牌 ID
            
        Returns:
            bool: 操作是否成功
        """
        token = APIToken.get(token_id)
        if not token:
            return False
        
        return token.delete()
    
    @staticmethod
    def get_token(token_id: str) -> Optional[APIToken]:
        """
        获取 API 令牌
        
        Args:
            token_id (str): 令牌 ID
            
        Returns:
            Optional[APIToken]: API 令牌实例，如果不存在则返回 None
        """
        return APIToken.get(token_id)
    
    @staticmethod
    def get_token_by_token_value(token_value: str) -> Optional[APIToken]:
        """
        根据令牌值获取 API 令牌
        
        Args:
            token_value (str): 令牌值
            
        Returns:
            Optional[APIToken]: API 令牌实例，如果不存在则返回 None
        """
        return APIToken.find_by_token(token_value)
    
    @staticmethod
    def get_all_tokens() -> List[APIToken]:
        """
        获取所有 API 令牌
        
        Returns:
            List[APIToken]: 所有 API 令牌列表
        """
        return APIToken.all()
    
    @staticmethod
    def get_valid_tokens() -> List[APIToken]:
        """
        获取所有有效的 API 令牌（启用且未过期）
        
        Returns:
            List[APIToken]: 有效的 API 令牌列表
        """
        return APIToken.find_valid()
    
    @staticmethod
    def enable_token(token_id: str) -> Optional[APIToken]:
        """
        启用 API 令牌
        
        Args:
            token_id (str): 令牌 ID
            
        Returns:
            Optional[APIToken]: 更新后的 API 令牌实例，如果令牌不存在则返回 None
        """
        return APITokenRepository.update_token(token_id, status=APIToken.STATUS_ENABLED)
    
    @staticmethod
    def disable_token(token_id: str) -> Optional[APIToken]:
        """
        禁用 API 令牌
        
        Args:
            token_id (str): 令牌 ID
            
        Returns:
            Optional[APIToken]: 更新后的 API 令牌实例，如果令牌不存在则返回 None
        """
        return APITokenRepository.update_token(token_id, status=APIToken.STATUS_DISABLED)
    
    @staticmethod
    def set_token_expiry(token_id: str, expires_at: str) -> Optional[APIToken]:
        """
        设置 API 令牌过期时间
        
        Args:
            token_id (str): 令牌 ID
            expires_at (str): 过期时间
            
        Returns:
            Optional[APIToken]: 更新后的 API 令牌实例，如果令牌不存在则返回 None
        """
        return APITokenRepository.update_token(token_id, expires_at=expires_at)
    
    @staticmethod
    def set_token_default_channels(token_id: str, channel_ids: List[str]) -> Optional[APIToken]:
        """
        设置 API 令牌默认渠道
        
        Args:
            token_id (str): 令牌 ID
            channel_ids (List[str]): 渠道 ID 列表
            
        Returns:
            Optional[APIToken]: 更新后的 API 令牌实例，如果令牌不存在则返回 None
        """
        return APITokenRepository.update_token(token_id, default_channels=channel_ids)
    
    @staticmethod
    def set_token_default_ai(token_id: str, ai_channel_id: Optional[str]) -> Optional[APIToken]:
        """
        设置 API 令牌默认 AI 渠道
        
        Args:
            token_id (str): 令牌 ID
            ai_channel_id (Optional[str]): AI 渠道 ID，如果为 None 则清除默认 AI 渠道
            
        Returns:
            Optional[APIToken]: 更新后的 API 令牌实例，如果令牌不存在则返回 None
        """
        return APITokenRepository.update_token(token_id, default_ai=ai_channel_id)
    
    @staticmethod
    def regenerate_token_value(token_id: str) -> Optional[APIToken]:
        """
        重新生成 API 令牌值
        
        Args:
            token_id (str): 令牌 ID
            
        Returns:
            Optional[APIToken]: 更新后的 API 令牌实例，如果令牌不存在则返回 None
        """
        token = APIToken.get(token_id)
        if not token:
            return None
        
        token.token = APIToken.generate_token()
        token.save()
        return token 