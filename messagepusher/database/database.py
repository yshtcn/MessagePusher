"""
数据库类

提供数据库连接和管理功能。
"""

import sqlite3
from typing import Optional, Dict, Any
from .repository import (
    MessageChannelRepository,
    ChannelRepository,
    AIChannelRepository,
    APITokenRepository,
    MessageRepository,
    SystemConfigRepository,
    MessageAIRepository
)

class Database:
    """数据库类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化数据库
        
        Args:
            config: 数据库配置
        """
        self._config = config or {"db_path": ":memory:"}
        self._connection = None
        
        # 初始化仓库
        self.message_channel_repository = None
        self.channel_repository = None
        self.ai_channel_repository = None
        self.api_token_repository = None
        self.message_repository = None
        self.system_config_repository = None
        self.message_ai_repository = None
    
    def connect(self):
        """连接数据库"""
        if self._connection is None:
            self._connection = sqlite3.connect(self._config["db_path"])
            self._connection.row_factory = sqlite3.Row
            
            # 初始化仓库
            self.message_channel_repository = MessageChannelRepository(self._connection)
            self.channel_repository = ChannelRepository(self._connection)
            self.ai_channel_repository = AIChannelRepository(self._connection)
            self.api_token_repository = APITokenRepository(self._connection)
            self.message_repository = MessageRepository(self._connection)
            self.system_config_repository = SystemConfigRepository(self._connection)
            self.message_ai_repository = MessageAIRepository(self._connection)
    
    def disconnect(self):
        """断开数据库连接"""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            
            # 清空仓库
            self.message_channel_repository = None
            self.channel_repository = None
            self.ai_channel_repository = None
            self.api_token_repository = None
            self.message_repository = None
            self.system_config_repository = None
            self.message_ai_repository = None
    
    def commit(self):
        """提交事务"""
        if self._connection is not None:
            self._connection.commit()
    
    def rollback(self):
        """回滚事务"""
        if self._connection is not None:
            self._connection.rollback()
    
    def execute(self, sql: str, params: Optional[tuple] = None) -> sqlite3.Cursor:
        """
        执行SQL语句
        
        Args:
            sql: SQL语句
            params: SQL参数
            
        Returns:
            sqlite3.Cursor: 游标对象
        """
        if self._connection is None:
            self.connect()
        
        if params is None:
            return self._connection.execute(sql)
        return self._connection.execute(sql, params)
    
    def executemany(self, sql: str, params: list) -> sqlite3.Cursor:
        """
        执行多条SQL语句
        
        Args:
            sql: SQL语句
            params: SQL参数列表
            
        Returns:
            sqlite3.Cursor: 游标对象
        """
        if self._connection is None:
            self.connect()
        
        return self._connection.executemany(sql, params)
    
    def executescript(self, sql_script: str) -> sqlite3.Cursor:
        """
        执行SQL脚本
        
        Args:
            sql_script: SQL脚本
            
        Returns:
            sqlite3.Cursor: 游标对象
        """
        if self._connection is None:
            self.connect()
        
        return self._connection.executescript(sql_script)
    
    def get_connection(self) -> sqlite3.Connection:
        """
        获取数据库连接
        
        Returns:
            sqlite3.Connection: 数据库连接对象
        """
        if self._connection is None:
            self.connect()
        
        return self._connection 