"""
消息渠道模型

定义消息推送渠道的数据模型。
"""

import json
from typing import Dict, Any, List, Optional, ClassVar

from .base_model import BaseModel


class Channel(BaseModel):
    """
    消息渠道模型类
    
    表示一个消息推送渠道，如Telegram、Bark等。
    """
    
    # 表名
    table_name: ClassVar[str] = "channels"
    
    # 字段定义
    fields: ClassVar[List[str]] = [
        "id", "name", "api_url", "method", "content_type", "params", 
        "headers", "placeholders", "proxy", "max_length",
        "created_at", "updated_at", "status"
    ]
    
    # JSON字段
    json_fields: ClassVar[List[str]] = ["params", "headers", "placeholders", "proxy"]
    
    # 请求方法
    METHOD_GET = "GET"
    METHOD_POST = "POST"
    METHOD_PUT = "PUT"
    METHOD_DELETE = "DELETE"
    
    # 内容类型
    CONTENT_TYPE_FORM = "form"
    CONTENT_TYPE_JSON = "json"
    CONTENT_TYPE_XML = "xml"
    
    # 状态
    STATUS_ENABLED = "enabled"
    STATUS_DISABLED = "disabled"
    
    def __init__(self, **kwargs):
        """
        初始化渠道实例
        
        Args:
            **kwargs: 渠道字段值
        """
        super().__init__(**kwargs)
        
        # 设置默认值
        if self.max_length is None:
            self.max_length = 2000
        
        if self.status is None:
            self.status = self.STATUS_ENABLED
            
        if self.method is None:
            self.method = self.METHOD_POST
            
        if self.content_type is None:
            self.content_type = self.CONTENT_TYPE_JSON
            
        # 确保JSON字段是字符串格式
        for field in self.json_fields:
            value = getattr(self, field, None)
            if value is not None and not isinstance(value, str):
                setattr(self, field, json.dumps(value))
    
    @property
    def params_dict(self) -> Dict[str, Any]:
        """
        获取参数映射字典
        
        Returns:
            Dict[str, Any]: 参数映射字典
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
        检查渠道是否启用
        
        Returns:
            bool: 渠道是否启用
        """
        return self.status == self.STATUS_ENABLED
    
    @classmethod
    def find_enabled(cls) -> List['Channel']:
        """
        查找所有启用的渠道
        
        Returns:
            List[Channel]: 启用的渠道列表
        """
        return cls.find(status=cls.STATUS_ENABLED) 