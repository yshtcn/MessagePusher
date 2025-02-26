"""
渠道仓库

封装渠道相关的复杂数据库操作。
"""

import json
from typing import Dict, List, Optional, Any

from ..models.channel import Channel


class ChannelRepository:
    """
    渠道仓库类
    
    封装渠道相关的复杂数据库操作。
    """
    
    @staticmethod
    def create_channel(name: str, api_url: str, method: str, content_type: str,
                      params: Dict[str, Any], headers: Optional[Dict[str, Any]] = None,
                      placeholders: Optional[Dict[str, Any]] = None,
                      proxy: Optional[Dict[str, Any]] = None, max_length: int = 2000) -> Channel:
        """
        创建渠道
        
        Args:
            name (str): 渠道名称
            api_url (str): API接口地址
            method (str): 请求方法
            content_type (str): 内容类型
            params (Dict[str, Any]): 参数映射
            headers (Optional[Dict[str, Any]], optional): 请求头
            placeholders (Optional[Dict[str, Any]], optional): 占位符值
            proxy (Optional[Dict[str, Any]], optional): 代理配置
            max_length (int, optional): 最大消息长度
            
        Returns:
            Channel: 创建的渠道实例
        """
        channel = Channel(
            name=name,
            api_url=api_url,
            method=method,
            content_type=content_type,
            params=json.dumps(params),
            headers=json.dumps(headers) if headers else None,
            placeholders=json.dumps(placeholders) if placeholders else None,
            proxy=json.dumps(proxy) if proxy else None,
            max_length=max_length,
            status=Channel.STATUS_ENABLED
        )
        channel.save()
        return channel
    
    @staticmethod
    def update_channel(channel_id: str, name: Optional[str] = None,
                      api_url: Optional[str] = None, method: Optional[str] = None,
                      content_type: Optional[str] = None, params: Optional[Dict[str, Any]] = None,
                      headers: Optional[Dict[str, Any]] = None, placeholders: Optional[Dict[str, Any]] = None,
                      proxy: Optional[Dict[str, Any]] = None, max_length: Optional[int] = None,
                      status: Optional[str] = None) -> Optional[Channel]:
        """
        更新渠道
        
        Args:
            channel_id (str): 渠道ID
            name (Optional[str], optional): 渠道名称
            api_url (Optional[str], optional): API接口地址
            method (Optional[str], optional): 请求方法
            content_type (Optional[str], optional): 内容类型
            params (Optional[Dict[str, Any]], optional): 参数映射
            headers (Optional[Dict[str, Any]], optional): 请求头
            placeholders (Optional[Dict[str, Any]], optional): 占位符值
            proxy (Optional[Dict[str, Any]], optional): 代理配置
            max_length (Optional[int], optional): 最大消息长度
            status (Optional[str], optional): 渠道状态
            
        Returns:
            Optional[Channel]: 更新后的渠道实例，如果渠道不存在则返回None
        """
        channel = Channel.get(channel_id)
        if not channel:
            return None
        
        if name is not None:
            channel.name = name
        
        if api_url is not None:
            channel.api_url = api_url
            
        if method is not None:
            channel.method = method
            
        if content_type is not None:
            channel.content_type = content_type
        
        if params is not None:
            channel.params = json.dumps(params)
            
        if headers is not None:
            channel.headers = json.dumps(headers) if headers else None
            
        if placeholders is not None:
            channel.placeholders = json.dumps(placeholders) if placeholders else None
        
        if proxy is not None:
            channel.proxy = json.dumps(proxy) if proxy else None
        
        if max_length is not None:
            channel.max_length = max_length
        
        if status is not None:
            channel.status = status
        
        channel.save()
        return channel
    
    @staticmethod
    def delete_channel(channel_id: str) -> bool:
        """
        删除渠道
        
        Args:
            channel_id (str): 渠道ID
            
        Returns:
            bool: 操作是否成功
        """
        channel = Channel.get(channel_id)
        if not channel:
            return False
        
        return channel.delete()
    
    @staticmethod
    def get_channel(channel_id: str) -> Optional[Channel]:
        """
        获取渠道
        
        Args:
            channel_id (str): 渠道ID
            
        Returns:
            Optional[Channel]: 渠道实例，如果不存在则返回None
        """
        return Channel.get(channel_id)
    
    @staticmethod
    def get_all_channels() -> List[Channel]:
        """
        获取所有渠道
        
        Returns:
            List[Channel]: 所有渠道列表
        """
        return Channel.all()
    
    @staticmethod
    def get_enabled_channels() -> List[Channel]:
        """
        获取所有启用的渠道
        
        Returns:
            List[Channel]: 启用的渠道列表
        """
        return Channel.find_enabled()
    
    @staticmethod
    def get_channels_by_type(channel_type: str) -> List[Channel]:
        """
        根据类型获取渠道
        
        Args:
            channel_type (str): 渠道类型
            
        Returns:
            List[Channel]: 渠道列表
        """
        return Channel.find_by_type(channel_type)
    
    @staticmethod
    def enable_channel(channel_id: str) -> Optional[Channel]:
        """
        启用渠道
        
        Args:
            channel_id (str): 渠道ID
            
        Returns:
            Optional[Channel]: 更新后的渠道实例，如果渠道不存在则返回None
        """
        return ChannelRepository.update_channel(channel_id, status=Channel.STATUS_ENABLED)
    
    @staticmethod
    def disable_channel(channel_id: str) -> Optional[Channel]:
        """
        禁用渠道
        
        Args:
            channel_id (str): 渠道ID
            
        Returns:
            Optional[Channel]: 更新后的渠道实例，如果渠道不存在则返回None
        """
        return ChannelRepository.update_channel(channel_id, status=Channel.STATUS_DISABLED) 