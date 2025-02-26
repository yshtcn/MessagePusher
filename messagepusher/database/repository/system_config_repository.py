"""
系统配置仓库

封装系统配置相关的复杂数据库操作。
"""

from typing import Dict, Any, Optional, List

from ..models.system_config import SystemConfig


class SystemConfigRepository:
    """
    系统配置仓库类
    
    封装系统配置相关的复杂数据库操作。
    """
    
    @staticmethod
    def get_config(key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key (str): 配置键
            default (Any, optional): 默认值，如果配置不存在则返回此值
            
        Returns:
            Any: 配置值
        """
        return SystemConfig.get_value(key, default)
    
    @staticmethod
    def set_config(key: str, value: Any, description: Optional[str] = None) -> bool:
        """
        设置配置值
        
        Args:
            key (str): 配置键
            value (Any): 配置值
            description (Optional[str], optional): 配置描述，如果为None则保留原描述
            
        Returns:
            bool: 操作是否成功
        """
        return SystemConfig.set_value(key, value, description)
    
    @staticmethod
    def get_int_config(key: str, default: int = 0) -> int:
        """
        获取整数配置值
        
        Args:
            key (str): 配置键
            default (int, optional): 默认值
            
        Returns:
            int: 配置值
        """
        return SystemConfig.get_int(key, default)
    
    @staticmethod
    def get_float_config(key: str, default: float = 0.0) -> float:
        """
        获取浮点数配置值
        
        Args:
            key (str): 配置键
            default (float, optional): 默认值
            
        Returns:
            float: 配置值
        """
        return SystemConfig.get_float(key, default)
    
    @staticmethod
    def get_bool_config(key: str, default: bool = False) -> bool:
        """
        获取布尔配置值
        
        Args:
            key (str): 配置键
            default (bool, optional): 默认值
            
        Returns:
            bool: 配置值
        """
        return SystemConfig.get_bool(key, default)
    
    @staticmethod
    def get_all_configs() -> Dict[str, Dict[str, Any]]:
        """
        获取所有配置
        
        Returns:
            Dict[str, Dict[str, Any]]: 配置字典，键为配置键，值为配置信息
        """
        return SystemConfig.get_all_configs()
    
    @staticmethod
    def delete_config(key: str) -> bool:
        """
        删除配置
        
        Args:
            key (str): 配置键
            
        Returns:
            bool: 操作是否成功
        """
        config = SystemConfig.get(key)
        if not config:
            return False
        
        return config.delete()
    
    @staticmethod
    def get_version() -> str:
        """
        获取系统版本
        
        Returns:
            str: 系统版本
        """
        return SystemConfigRepository.get_config(SystemConfig.KEY_VERSION, "1.0.0")
    
    @staticmethod
    def get_max_retry_count() -> int:
        """
        获取最大重试次数
        
        Returns:
            int: 最大重试次数
        """
        return SystemConfigRepository.get_int_config(SystemConfig.KEY_MAX_RETRY_COUNT, 3)
    
    @staticmethod
    def get_retry_interval() -> int:
        """
        获取重试间隔（秒）
        
        Returns:
            int: 重试间隔
        """
        return SystemConfigRepository.get_int_config(SystemConfig.KEY_RETRY_INTERVAL, 300)
    
    @staticmethod
    def get_file_storage_path() -> str:
        """
        获取文件存储路径
        
        Returns:
            str: 文件存储路径
        """
        return SystemConfigRepository.get_config(SystemConfig.KEY_FILE_STORAGE_PATH, "data/files")
    
    @staticmethod
    def get_file_retention_days() -> int:
        """
        获取文件保留天数
        
        Returns:
            int: 文件保留天数
        """
        return SystemConfigRepository.get_int_config(SystemConfig.KEY_FILE_RETENTION_DAYS, 30)
    
    @staticmethod
    def get_default_max_length() -> int:
        """
        获取默认最大消息长度
        
        Returns:
            int: 默认最大消息长度
        """
        return SystemConfigRepository.get_int_config(SystemConfig.KEY_DEFAULT_MAX_LENGTH, 2000)
    
    @staticmethod
    def initialize_default_configs() -> None:
        """
        初始化默认配置
        
        如果配置不存在，则创建默认配置
        """
        default_configs = [
            (SystemConfig.KEY_VERSION, "1.0.0", "系统版本"),
            (SystemConfig.KEY_MAX_RETRY_COUNT, "3", "消息发送最大重试次数"),
            (SystemConfig.KEY_RETRY_INTERVAL, "300", "重试间隔（秒）"),
            (SystemConfig.KEY_FILE_STORAGE_PATH, "data/files", "文件存储路径"),
            (SystemConfig.KEY_FILE_RETENTION_DAYS, "30", "文件保留天数"),
            (SystemConfig.KEY_DEFAULT_MAX_LENGTH, "2000", "默认最大消息长度")
        ]
        
        for key, value, description in default_configs:
            if SystemConfig.get(key) is None:
                SystemConfig(key=key, value=value, description=description).save() 