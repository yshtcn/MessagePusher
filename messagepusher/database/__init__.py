"""
MessagePusher 数据库模块

该模块负责数据库的初始化、连接管理和基本操作。
"""

from .core import init_db, get_db, close_db
from .models import *
from .repository import *
from typing import Optional
from .database import Database

_database_instance: Optional[Database] = None

def get_database() -> Database:
    """
    获取数据库实例
    
    Returns:
        Database: 数据库实例
    """
    global _database_instance
    if _database_instance is None:
        _database_instance = Database()
    return _database_instance

def init_database(config: dict) -> None:
    """
    初始化数据库
    
    Args:
        config: 数据库配置
    """
    global _database_instance
    _database_instance = Database(config)

__all__ = ['init_db', 'get_db', 'close_db', 'get_database', 'init_database'] 