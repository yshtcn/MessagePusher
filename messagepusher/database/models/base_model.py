"""
基础模型类

所有数据模型类的基类，提供通用的数据库操作方法。
"""

import json
import uuid
import sqlite3
import datetime
from typing import Dict, List, Any, Optional, Type, TypeVar, Generic, ClassVar

from ..core import get_db, execute_query

T = TypeVar('T', bound='BaseModel')


class BaseModel:
    """
    基础模型类
    
    所有数据模型类的基类，提供通用的数据库操作方法。
    """
    
    # 表名，子类必须覆盖
    table_name: ClassVar[str] = ""
    
    # 主键字段名
    primary_key: ClassVar[str] = "id"
    
    # 时间戳字段
    created_at_field: ClassVar[str] = "created_at"
    updated_at_field: ClassVar[str] = "updated_at"
    
    # 字段定义，子类必须覆盖
    fields: ClassVar[List[str]] = []
    
    def __init__(self, **kwargs):
        """
        初始化模型实例
        
        Args:
            **kwargs: 模型字段值
        """
        # 设置默认ID
        if self.primary_key not in kwargs:
            kwargs[self.primary_key] = str(uuid.uuid4())
        
        # 设置字段值
        for field in self.fields:
            if field in kwargs:
                setattr(self, field, kwargs[field])
            else:
                setattr(self, field, None)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将模型转换为字典
        
        Returns:
            Dict[str, Any]: 模型字段字典
        """
        result = {}
        for field in self.fields:
            value = getattr(self, field, None)
            # 处理JSON字段
            if value is not None and field in getattr(self, 'json_fields', []):
                if isinstance(value, str):
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        pass
            result[field] = value
        return result
    
    def save(self) -> bool:
        """
        保存模型到数据库
        
        如果模型已存在则更新，否则插入新记录
        
        Returns:
            bool: 操作是否成功
        """
        conn = get_db()
        
        # 检查记录是否存在
        primary_key_value = getattr(self, self.primary_key)
        cursor = conn.execute(
            f"SELECT COUNT(*) FROM {self.table_name} WHERE {self.primary_key} = ?",
            (primary_key_value,)
        )
        exists = cursor.fetchone()[0] > 0
        
        # 准备数据
        data = {}
        for field in self.fields:
            value = getattr(self, field, None)
            # 处理JSON字段
            if value is not None and field in getattr(self, 'json_fields', []):
                if not isinstance(value, str):
                    value = json.dumps(value)
            data[field] = value
        
        # 更新时间戳
        now = datetime.datetime.now().isoformat()
        if exists and self.updated_at_field in self.fields:
            data[self.updated_at_field] = now
        elif not exists:
            if self.created_at_field in self.fields:
                data[self.created_at_field] = now
            if self.updated_at_field in self.fields:
                data[self.updated_at_field] = now
        
        try:
            if exists:
                # 更新记录
                set_clause = ", ".join([f"{field} = ?" for field in data.keys()])
                values = list(data.values())
                conn.execute(
                    f"UPDATE {self.table_name} SET {set_clause} WHERE {self.primary_key} = ?",
                    values + [primary_key_value]
                )
            else:
                # 插入记录
                fields_str = ", ".join(data.keys())
                placeholders = ", ".join(["?" for _ in data.keys()])
                conn.execute(
                    f"INSERT INTO {self.table_name} ({fields_str}) VALUES ({placeholders})",
                    list(data.values())
                )
            return True
        except sqlite3.Error:
            return False
    
    def delete(self) -> bool:
        """
        从数据库中删除模型
        
        Returns:
            bool: 操作是否成功
        """
        conn = get_db()
        primary_key_value = getattr(self, self.primary_key)
        
        try:
            conn.execute(
                f"DELETE FROM {self.table_name} WHERE {self.primary_key} = ?",
                (primary_key_value,)
            )
            return True
        except sqlite3.Error:
            return False
    
    @classmethod
    def get(cls: Type[T], id_value: str) -> Optional[T]:
        """
        通过ID获取模型实例
        
        Args:
            id_value (str): 主键值
            
        Returns:
            Optional[T]: 模型实例，如果不存在则返回None
        """
        conn = get_db()
        
        # 设置 SQLite 连接以返回行作为字典
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute(
            f"SELECT * FROM {cls.table_name} WHERE {cls.primary_key} = ?",
            (id_value,)
        )
        
        row = cursor.fetchone()
        if row:
            # 将 sqlite3.Row 对象转换为字典
            row_dict = dict(row)
            return cls(**row_dict)
        
        return None
    
    @classmethod
    def find(cls: Type[T], **kwargs) -> List[T]:
        """
        根据条件查找模型实例
        
        Args:
            **kwargs: 查询条件
            
        Returns:
            List[T]: 模型实例列表
        """
        conn = get_db()
        
        # 设置 SQLite 连接以返回行作为字典
        conn.row_factory = sqlite3.Row
        
        # 构建查询条件
        conditions = []
        values = []
        for key, value in kwargs.items():
            conditions.append(f"{key} = ?")
            values.append(value)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        cursor = conn.execute(
            f"SELECT * FROM {cls.table_name} WHERE {where_clause}",
            values
        )
        
        return [cls(**dict(row)) for row in cursor.fetchall()]
    
    @classmethod
    def find_one(cls: Type[T], **kwargs) -> Optional[T]:
        """
        根据条件查找单个模型实例
        
        Args:
            **kwargs: 查询条件
            
        Returns:
            Optional[T]: 模型实例，如果不存在则返回None
        """
        results = cls.find(**kwargs)
        return results[0] if results else None
    
    @classmethod
    def all(cls: Type[T]) -> List[T]:
        """
        获取所有模型实例
        
        Returns:
            List[T]: 所有模型实例列表
        """
        conn = get_db()
        
        # 设置 SQLite 连接以返回行作为字典
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute(f"SELECT * FROM {cls.table_name}")
        return [cls(**dict(row)) for row in cursor.fetchall()]
    
    @classmethod
    def count(cls, **kwargs) -> int:
        """
        计算符合条件的记录数
        
        Args:
            **kwargs: 查询条件
            
        Returns:
            int: 记录数
        """
        conn = get_db()
        
        # 构建查询条件
        conditions = []
        values = []
        for key, value in kwargs.items():
            conditions.append(f"{key} = ?")
            values.append(value)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        cursor = conn.execute(
            f"SELECT COUNT(*) FROM {cls.table_name} WHERE {where_clause}",
            values
        )
        
        return cursor.fetchone()[0] 