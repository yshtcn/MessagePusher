"""
AI 渠道仓库

封装 AI 渠道相关的复杂数据库操作。
"""

import json
from typing import Dict, List, Optional, Any

from ..models.ai_channel import AIChannel


class AIChannelRepository:
    """
    AI 渠道仓库类
    
    封装 AI 渠道相关的复杂数据库操作。
    """
    
    @staticmethod
    def create_ai_channel(name: str, api_url: str, model: str,
                         params: Optional[Dict[str, Any]] = None,
                         headers: Optional[Dict[str, Any]] = None,
                         placeholders: Optional[Dict[str, Any]] = None,
                         prompt: Optional[str] = None,
                         proxy: Optional[Dict[str, Any]] = None) -> AIChannel:
        """
        创建 AI 渠道
        
        Args:
            name (str): AI 渠道名称
            api_url (str): API接口地址
            model (str): 模型名称
            params (Optional[Dict[str, Any]], optional): 模型参数
            headers (Optional[Dict[str, Any]], optional): 请求头
            placeholders (Optional[Dict[str, Any]], optional): 占位符值
            prompt (Optional[str], optional): 自定义 Prompt 模板
            proxy (Optional[Dict[str, Any]], optional): 代理配置
            
        Returns:
            AIChannel: 创建的 AI 渠道实例
        """
        ai_channel = AIChannel(
            name=name,
            api_url=api_url,
            method=AIChannel.METHOD_POST,
            model=model,
            params=json.dumps(params) if params else None,
            headers=json.dumps(headers) if headers else None,
            placeholders=json.dumps(placeholders) if placeholders else None,
            prompt=prompt,
            proxy=json.dumps(proxy) if proxy else None,
            status=AIChannel.STATUS_ENABLED
        )
        ai_channel.save()
        return ai_channel
    
    @staticmethod
    def update_ai_channel(ai_channel_id: str, name: Optional[str] = None,
                         api_url: Optional[str] = None, model: Optional[str] = None,
                         params: Optional[Dict[str, Any]] = None,
                         headers: Optional[Dict[str, Any]] = None,
                         placeholders: Optional[Dict[str, Any]] = None,
                         prompt: Optional[str] = None,
                         proxy: Optional[Dict[str, Any]] = None,
                         status: Optional[str] = None) -> Optional[AIChannel]:
        """
        更新 AI 渠道
        
        Args:
            ai_channel_id (str): AI 渠道 ID
            name (Optional[str], optional): AI 渠道名称
            api_url (Optional[str], optional): API接口地址
            model (Optional[str], optional): 模型名称
            params (Optional[Dict[str, Any]], optional): 模型参数
            headers (Optional[Dict[str, Any]], optional): 请求头
            placeholders (Optional[Dict[str, Any]], optional): 占位符值
            prompt (Optional[str], optional): 自定义 Prompt 模板
            proxy (Optional[Dict[str, Any]], optional): 代理配置
            status (Optional[str], optional): AI 渠道状态
            
        Returns:
            Optional[AIChannel]: 更新后的 AI 渠道实例，如果 AI 渠道不存在则返回 None
        """
        ai_channel = AIChannel.get(ai_channel_id)
        if not ai_channel:
            return None
        
        if name is not None:
            ai_channel.name = name
        
        if api_url is not None:
            ai_channel.api_url = api_url
            
        if model is not None:
            ai_channel.model = model
        
        if params is not None:
            ai_channel.params = json.dumps(params) if params else None
            
        if headers is not None:
            ai_channel.headers = json.dumps(headers) if headers else None
            
        if placeholders is not None:
            ai_channel.placeholders = json.dumps(placeholders) if placeholders else None
        
        if prompt is not None:
            ai_channel.prompt = prompt
        
        if proxy is not None:
            ai_channel.proxy = json.dumps(proxy) if proxy else None
        
        if status is not None:
            ai_channel.status = status
        
        ai_channel.save()
        return ai_channel
    
    @staticmethod
    def delete_ai_channel(ai_channel_id: str) -> bool:
        """
        删除 AI 渠道
        
        Args:
            ai_channel_id (str): AI 渠道 ID
            
        Returns:
            bool: 操作是否成功
        """
        ai_channel = AIChannel.get(ai_channel_id)
        if not ai_channel:
            return False
        
        return ai_channel.delete()
    
    @staticmethod
    def get_ai_channel(ai_channel_id: str) -> Optional[AIChannel]:
        """
        获取 AI 渠道
        
        Args:
            ai_channel_id (str): AI 渠道 ID
            
        Returns:
            Optional[AIChannel]: AI 渠道实例，如果不存在则返回 None
        """
        return AIChannel.get(ai_channel_id)
    
    @staticmethod
    def get_all_ai_channels() -> List[AIChannel]:
        """
        获取所有 AI 渠道
        
        Returns:
            List[AIChannel]: 所有 AI 渠道列表
        """
        return AIChannel.all()
    
    @staticmethod
    def get_enabled_ai_channels() -> List[AIChannel]:
        """
        获取所有启用的 AI 渠道
        
        Returns:
            List[AIChannel]: 启用的 AI 渠道列表
        """
        return AIChannel.find_enabled()
    
    @staticmethod
    def get_ai_channels_by_model(model: str) -> List[AIChannel]:
        """
        根据模型名称获取 AI 渠道
        
        Args:
            model (str): 模型名称
            
        Returns:
            List[AIChannel]: AI 渠道列表
        """
        return AIChannel.find_by_model(model)
    
    @staticmethod
    def enable_ai_channel(ai_channel_id: str) -> Optional[AIChannel]:
        """
        启用 AI 渠道
        
        Args:
            ai_channel_id (str): AI 渠道 ID
            
        Returns:
            Optional[AIChannel]: 更新后的 AI 渠道实例，如果 AI 渠道不存在则返回 None
        """
        return AIChannelRepository.update_ai_channel(ai_channel_id, status=AIChannel.STATUS_ENABLED)
    
    @staticmethod
    def disable_ai_channel(ai_channel_id: str) -> Optional[AIChannel]:
        """
        禁用 AI 渠道
        
        Args:
            ai_channel_id (str): AI 渠道 ID
            
        Returns:
            Optional[AIChannel]: 更新后的 AI 渠道实例，如果 AI 渠道不存在则返回 None
        """
        return AIChannelRepository.update_ai_channel(ai_channel_id, status=AIChannel.STATUS_DISABLED) 