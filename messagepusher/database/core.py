"""
数据库核心模块

负责数据库的初始化、连接管理和基本操作。
"""

import os
import sqlite3
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import datetime

# 数据库连接池
_db_connections: Dict[int, sqlite3.Connection] = {}

# 默认数据库路径
DEFAULT_DB_PATH = "data/messagepusher.db"

# 日志记录器
logger = logging.getLogger(__name__)


# 自定义时间戳转换函数
def adapt_datetime(val):
    """将 datetime 对象转换为 ISO 格式字符串"""
    return val.isoformat() if val else None


def convert_timestamp(val):
    """将 ISO 格式字符串转换为 datetime 对象"""
    if not val:
        return None
    
    try:
        if isinstance(val, bytes):
            val = val.decode('utf-8')
        return datetime.datetime.fromisoformat(val)
    except (ValueError, TypeError):
        return val


def get_db_path() -> str:
    """
    获取数据库路径
    
    Returns:
        str: 数据库路径
    """
    # 优先使用环境变量中的路径
    env_path = os.environ.get("MESSAGEPUSHER_DB_PATH")
    if env_path:
        return env_path
    
    # 使用默认路径
    return DEFAULT_DB_PATH


def get_db() -> sqlite3.Connection:
    """
    获取数据库连接
    
    如果当前线程已有连接，则返回已有连接，否则创建新连接
    
    Returns:
        sqlite3.Connection: 数据库连接
    """
    import threading
    thread_id = threading.get_ident()
    
    # 如果当前线程已有连接，则返回已有连接
    if thread_id in _db_connections:
        return _db_connections[thread_id]
    
    # 创建数据库目录
    db_path = get_db_path()
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    
    # 创建新连接
    conn = sqlite3.connect(db_path)
    
    # 设置行工厂为返回字典
    conn.row_factory = sqlite3.Row
    
    # 启用外键约束
    conn.execute("PRAGMA foreign_keys = ON")
    
    # 存储连接
    _db_connections[thread_id] = conn
    
    logger.debug(f"Created new database connection for thread {thread_id}")
    
    return conn


def close_db(thread_id: Optional[int] = None) -> None:
    """
    关闭数据库连接
    
    Args:
        thread_id (Optional[int], optional): 线程ID，如果为None则关闭当前线程的连接
    """
    if thread_id is None:
        import threading
        thread_id = threading.get_ident()
    
    if thread_id in _db_connections:
        _db_connections[thread_id].close()
        del _db_connections[thread_id]
        logger.debug(f"Closed database connection for thread {thread_id}")


def init_db() -> None:
    """
    初始化数据库
    
    创建数据库表结构和初始数据
    """
    db_path = get_db_path()
    db_exists = os.path.exists(db_path)
    
    if not db_exists:
        logger.info(f"Creating new database at {db_path}")
    else:
        logger.info(f"Using existing database at {db_path}")
    
    # 注册自定义时间戳转换函数
    sqlite3.register_adapter(datetime.datetime, adapt_datetime)
    sqlite3.register_converter("TIMESTAMP", convert_timestamp)
    
    # 获取数据库连接
    conn = get_db()
    
    # 创建表结构
    create_tables(conn)
    
    # 初始化系统配置
    initialize_system_config(conn)
    
    logger.info("Database initialization completed")


def create_tables(conn: sqlite3.Connection) -> None:
    """
    创建数据库表
    
    Args:
        conn (sqlite3.Connection): 数据库连接
    """
    # 创建消息渠道表
    conn.execute("""
    CREATE TABLE IF NOT EXISTS channels (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        api_url TEXT NOT NULL,
        method TEXT NOT NULL,
        content_type TEXT NOT NULL,
        params TEXT NOT NULL,  -- JSON格式
        headers TEXT,          -- JSON格式，可为null
        placeholders TEXT,     -- JSON格式，可为null
        proxy TEXT,            -- JSON格式，可为null
        max_length INTEGER NOT NULL DEFAULT 2000,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        status TEXT NOT NULL DEFAULT 'enabled'
    )
    """)
    
    # 创建AI渠道表
    conn.execute("""
    CREATE TABLE IF NOT EXISTS ai_channels (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        api_url TEXT NOT NULL,
        method TEXT NOT NULL,
        model TEXT NOT NULL,
        params TEXT,           -- JSON格式，可为null
        headers TEXT,          -- JSON格式，可为null
        placeholders TEXT,     -- JSON格式，可为null
        prompt TEXT,           -- 可为null
        proxy TEXT,            -- JSON格式，可为null
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        status TEXT NOT NULL DEFAULT 'enabled'
    )
    """)
    
    # 创建API令牌表
    conn.execute("""
    CREATE TABLE IF NOT EXISTS api_tokens (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        token TEXT NOT NULL UNIQUE,
        default_channels TEXT,  -- JSON数组，可为null
        default_ai TEXT,        -- 可为null
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        expires_at TEXT,   -- 可为null
        status TEXT NOT NULL DEFAULT 'enabled'
    )
    """)
    
    # 创建消息表
    conn.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        api_token_id TEXT NOT NULL,
        title TEXT,            -- 可为null
        content TEXT,          -- 可为null
        url TEXT,              -- 可为null
        url_content TEXT,      -- 可为null
        file_storage TEXT,     -- 可为null
        view_token TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (api_token_id) REFERENCES api_tokens (id) ON DELETE CASCADE
    )
    """)
    
    # 创建消息渠道关联表
    conn.execute("""
    CREATE TABLE IF NOT EXISTS message_channels (
        id TEXT PRIMARY KEY,
        message_id TEXT NOT NULL,
        channel_id TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        error TEXT,            -- 可为null
        sent_at TEXT,     -- 可为null
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (message_id) REFERENCES messages (id) ON DELETE CASCADE,
        FOREIGN KEY (channel_id) REFERENCES channels (id) ON DELETE CASCADE
    )
    """)
    
    # 创建消息AI处理表
    conn.execute("""
    CREATE TABLE IF NOT EXISTS message_ai (
        id TEXT PRIMARY KEY,
        message_id TEXT NOT NULL,
        ai_channel_id TEXT NOT NULL,
        prompt TEXT NOT NULL,
        result TEXT,           -- 可为null
        status TEXT NOT NULL DEFAULT 'pending',
        error TEXT,            -- 可为null
        processed_at TEXT, -- 可为null
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (message_id) REFERENCES messages (id) ON DELETE CASCADE,
        FOREIGN KEY (ai_channel_id) REFERENCES ai_channels (id) ON DELETE CASCADE
    )
    """)
    
    # 创建系统配置表
    conn.execute("""
    CREATE TABLE IF NOT EXISTS system_config (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        description TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 创建索引
    conn.execute("CREATE INDEX IF NOT EXISTS idx_channels_api_url ON channels (api_url)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ai_channels_api_url ON ai_channels (api_url)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ai_channels_model ON ai_channels (model)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_api_tokens_token ON api_tokens (token)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_api_token_id ON messages (api_token_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages (created_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_message_channels_message_id ON message_channels (message_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_message_channels_channel_id ON message_channels (channel_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_message_channels_status ON message_channels (status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_message_ai_message_id ON message_ai (message_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_message_ai_ai_channel_id ON message_ai (ai_channel_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_message_ai_status ON message_ai (status)")


def initialize_system_config(conn: sqlite3.Connection) -> None:
    """
    初始化系统配置
    
    Args:
        conn (sqlite3.Connection): 数据库连接
    """
    # 插入初始系统配置
    initial_configs = [
        ('version', '1.0.0', '系统版本'),
        ('max_retry_count', '3', '消息发送最大重试次数'),
        ('retry_interval', '300', '重试间隔（秒）'),
        ('file_storage_path', 'data/files', '文件存储路径'),
        ('file_retention_days', '30', '文件保留天数'),
        ('default_max_length', '2000', '默认最大消息长度')
    ]
    
    for key, value, description in initial_configs:
        conn.execute(
            "INSERT OR IGNORE INTO system_config (key, value, description) VALUES (?, ?, ?)",
            (key, value, description)
        )


def execute_query(query: str, params: Optional[Dict[str, Any]] = None) -> sqlite3.Cursor:
    """
    执行SQL查询
    
    Args:
        query (str): SQL查询语句
        params (Optional[Dict[str, Any]], optional): 查询参数
        
    Returns:
        sqlite3.Cursor: 查询结果游标
    """
    conn = get_db()
    
    if params:
        return conn.execute(query, params)
    else:
        return conn.execute(query) 