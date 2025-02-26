"""
AI 渠道模型

定义 AI 服务的数据模型。
"""

import json
from typing import Dict, Any, List, Optional, ClassVar

from .base_model import BaseModel


class AIChannel(BaseModel):
    """
    AI 渠道模型类
    
    表示一个 AI 服务，如 OpenAI、文心一言等。
    """
    
    # 表名
    table_name: ClassVar[str] = "ai_channels"
    
    # 字段定义
    fields: ClassVar[List[str]] = [
        "id", "name", "api_url", "method", "model", "params", 
        "headers", "placeholders", "prompt", "proxy",
        "created_at", "updated_at", "status"
    ]
    
    # JSON字段
    json_fields: ClassVar[List[str]] = ["params", "headers", "placeholders", "proxy"]
    
    # 请求方法
    METHOD_POST = "POST"
    
    # 状态
    STATUS_ENABLED = "enabled"
    STATUS_DISABLED = "disabled"
    
    def __init__(self, **kwargs):
        """
        初始化 AI 渠道实例
        
        Args:
            **kwargs: AI 渠道字段值
        """
        super().__init__(**kwargs)
        
        # 设置默认值
        if self.status is None:
            self.status = self.STATUS_ENABLED
            
        if self.method is None:
            self.method = self.METHOD_POST
            
        # 确保JSON字段是字符串格式
        for field in self.json_fields:
            value = getattr(self, field, None)
            if value is not None and not isinstance(value, str):
                setattr(self, field, json.dumps(value))
    
    @property
    def params_dict(self) -> Dict[str, Any]:
        """
        获取模型参数字典
        
        Returns:
            Dict[str, Any]: 模型参数字典
        """
        return self._get_json_field("params")
    
    @property
    def headers_dict(self) -> Dict[str, Any]:
        """
        获取请求头字典
        
        Returns:
            Dict[str, Any]: 请求头字典
        """
        return self._get_json_field("headers")
    
    @property
    def placeholders_dict(self) -> Dict[str, Any]:
        """
        获取占位符字典
        
        Returns:
            Dict[str, Any]: 占位符字典
        """
        return self._get_json_field("placeholders")
    
    @property
    def proxy_dict(self) -> Optional[Dict[str, Any]]:
        """
        获取代理配置字典
        
        Returns:
            Optional[Dict[str, Any]]: 代理配置字典，如果没有代理则返回None
        """
        result = self._get_json_field("proxy")
        return result if result else None
    
    def _get_json_field(self, field_name: str) -> Dict[str, Any]:
        """
        获取JSON字段的字典值
        
        Args:
            field_name (str): 字段名
            
        Returns:
            Dict[str, Any]: 字典值，如果解析失败则返回空字典
        """
        value = getattr(self, field_name, None)
        if not value:
            return {}
        
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return {}
        elif isinstance(value, dict):
            return value
        return {}
    
    def is_enabled(self) -> bool:
        """
        检查 AI 渠道是否启用
        
        Returns:
            bool: AI 渠道是否启用
        """
        return self.status == self.STATUS_ENABLED
    
    @classmethod
    def find_by_model(cls, model: str) -> List['AIChannel']:
        """
        根据模型名称查找 AI 渠道
        
        Args:
            model (str): 模型名称
            
        Returns:
            List[AIChannel]: AI 渠道列表
        """
        return cls.find(model=model)
    
    @classmethod
    def find_enabled(cls) -> List['AIChannel']:
        """
        查找所有启用的 AI 渠道
        
        Returns:
            List[AIChannel]: 启用的 AI 渠道列表
        """
        return cls.find(status=cls.STATUS_ENABLED) 