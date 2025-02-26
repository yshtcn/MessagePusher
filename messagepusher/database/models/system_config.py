"""
系统配置模型

定义系统配置的数据模型。
"""

from typing import Any, ClassVar, Dict, List, Optional

from .base_model import BaseModel


class SystemConfig(BaseModel):
    """
    系统配置模型类
    
    表示系统的配置项。
    """
    
    # 表名
    table_name: ClassVar[str] = "system_config"
    
    # 主键字段名
    primary_key: ClassVar[str] = "key"
    
    # 字段定义
    fields: ClassVar[List[str]] = [
        "key", "value", "description", "created_at", "updated_at"
    ]
    
    # 常用配置键
    KEY_VERSION = "version"
    KEY_MAX_RETRY_COUNT = "max_retry_count"
    KEY_RETRY_INTERVAL = "retry_interval"
    KEY_FILE_STORAGE_PATH = "file_storage_path"
    KEY_FILE_RETENTION_DAYS = "file_retention_days"
    KEY_DEFAULT_MAX_LENGTH = "default_max_length"
    
    @classmethod
    def get_value(cls, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key (str): 配置键
            default (Any, optional): 默认值，如果配置不存在则返回此值
            
        Returns:
            Any: 配置值
        """
        try:
            config = cls.get(key)
            if config:
                return config.value
            return default
        except Exception:
            # 如果发生任何错误，返回默认值
            return default
    
    @classmethod
    def set_value(cls, key: str, value: Any, description: Optional[str] = None) -> bool:
        """
        设置配置值
        
        Args:
            key (str): 配置键
            value (Any): 配置值
            description (Optional[str], optional): 配置描述，如果为None则保留原描述
            
        Returns:
            bool: 操作是否成功
        """
        try:
            config = cls.get(key)
            if config:
                config.value = str(value)
                if description:
                    config.description = description
                return config.save()
            else:
                if not description:
                    description = f"配置项: {key}"
                config = cls(key=key, value=str(value), description=description)
                return config.save()
        except Exception:
            # 如果发生任何错误，返回失败
            return False
    
    @classmethod
    def get_int(cls, key: str, default: int = 0) -> int:
        """
        获取整数配置值
        
        Args:
            key (str): 配置键
            default (int, optional): 默认值
            
        Returns:
            int: 配置值
        """
        value = cls.get_value(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    @classmethod
    def get_float(cls, key: str, default: float = 0.0) -> float:
        """
        获取浮点数配置值
        
        Args:
            key (str): 配置键
            default (float, optional): 默认值
            
        Returns:
            float: 配置值
        """
        value = cls.get_value(key, default)
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    @classmethod
    def get_bool(cls, key: str, default: bool = False) -> bool:
        """
        获取布尔配置值
        
        Args:
            key (str): 配置键
            default (bool, optional): 默认值
            
        Returns:
            bool: 配置值
        """
        value = cls.get_value(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "yes", "1", "on")
        return bool(value)
    
    @classmethod
    def get_all_configs(cls) -> Dict[str, Dict[str, Any]]:
        """
        获取所有配置
        
        Returns:
            Dict[str, Dict[str, Any]]: 配置字典，键为配置键，值为配置信息
        """
        try:
            configs = cls.all()
            result = {}
            for config in configs:
                result[config.key] = {
                    "value": config.value,
                    "description": config.description,
                    "created_at": config.created_at,
                    "updated_at": config.updated_at
                }
            return result
        except Exception:
            # 如果发生任何错误，返回空字典
            return {} 