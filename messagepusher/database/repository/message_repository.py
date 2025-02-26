"""
消息仓库

封装消息相关的复杂数据库操作。
"""

import datetime
from typing import Dict, List, Optional, Any, Tuple

from ..models.message import Message
from ..models.message_channel import MessageChannel
from ..models.message_ai import MessageAI
from ..core import get_db


class MessageRepository:
    """
    消息仓库类
    
    封装消息相关的复杂数据库操作。
    """
    
    @staticmethod
    def create_message(api_token_id: str, title: Optional[str] = None,
                      content: Optional[str] = None, url: Optional[str] = None,
                      url_content: Optional[str] = None,
                      file_storage: Optional[str] = None) -> Message:
        """
        创建消息
        
        Args:
            api_token_id (str): API令牌ID
            title (Optional[str], optional): 消息标题
            content (Optional[str], optional): 消息内容
            url (Optional[str], optional): 链接地址
            url_content (Optional[str], optional): URL内容的摘要或简短描述
            file_storage (Optional[str], optional): URL抓取内容的文件存储路径
            
        Returns:
            Message: 创建的消息实例
        """
        message = Message(
            api_token_id=api_token_id,
            title=title,
            content=content,
            url=url,
            url_content=url_content,
            file_storage=file_storage
        )
        message.save()
        return message
    
    @staticmethod
    def add_channel_to_message(message_id: str, channel_id: str) -> Optional[MessageChannel]:
        """
        为消息添加渠道
        
        Args:
            message_id (str): 消息ID
            channel_id (str): 渠道ID
            
        Returns:
            Optional[MessageChannel]: 创建的消息渠道关联实例，如果消息或渠道不存在则返回None
        """
        # 检查消息和渠道是否存在
        message = Message.get(message_id)
        if not message:
            return None
        
        # 检查是否已经存在相同的消息渠道关联
        existing = MessageChannel.find_one(message_id=message_id, channel_id=channel_id)
        if existing:
            return existing
        
        # 创建新的消息渠道关联
        message_channel = MessageChannel(
            message_id=message_id,
            channel_id=channel_id,
            status=MessageChannel.STATUS_PENDING
        )
        message_channel.save()
        return message_channel
    
    @staticmethod
    def add_ai_to_message(message_id: str, ai_channel_id: str, prompt: str) -> Optional[MessageAI]:
        """
        为消息添加AI处理
        
        Args:
            message_id (str): 消息ID
            ai_channel_id (str): AI渠道ID
            prompt (str): 使用的Prompt
            
        Returns:
            Optional[MessageAI]: 创建的消息AI处理实例，如果消息或AI渠道不存在则返回None
        """
        # 检查消息是否存在
        message = Message.get(message_id)
        if not message:
            return None
        
        # 检查是否已经存在相同的消息AI处理
        existing = MessageAI.find_one(message_id=message_id, ai_channel_id=ai_channel_id)
        if existing:
            return existing
        
        # 创建新的消息AI处理
        message_ai = MessageAI(
            message_id=message_id,
            ai_channel_id=ai_channel_id,
            prompt=prompt,
            status=MessageAI.STATUS_PENDING
        )
        message_ai.save()
        return message_ai
    
    @staticmethod
    def get_message(message_id: str) -> Optional[Message]:
        """
        获取消息
        
        Args:
            message_id (str): 消息ID
            
        Returns:
            Optional[Message]: 消息实例，如果不存在则返回None
        """
        return Message.get(message_id)
    
    @staticmethod
    def get_message_by_view_token(view_token: str) -> Optional[Message]:
        """
        根据查看令牌获取消息
        
        Args:
            view_token (str): 查看令牌
            
        Returns:
            Optional[Message]: 消息实例，如果不存在则返回None
        """
        return Message.find_by_view_token(view_token)
    
    @staticmethod
    def get_message_channels(message_id: str) -> List[MessageChannel]:
        """
        获取消息的所有渠道关联
        
        Args:
            message_id (str): 消息ID
            
        Returns:
            List[MessageChannel]: 消息渠道关联列表
        """
        return MessageChannel.find_by_message(message_id)
    
    @staticmethod
    def get_message_ai(message_id: str) -> List[MessageAI]:
        """
        获取消息的所有AI处理
        
        Args:
            message_id (str): 消息ID
            
        Returns:
            List[MessageAI]: 消息AI处理列表
        """
        return MessageAI.find_by_message(message_id)
    
    @staticmethod
    def get_pending_message_channels() -> List[MessageChannel]:
        """
        获取所有等待发送的消息渠道关联
        
        Returns:
            List[MessageChannel]: 等待发送的消息渠道关联列表
        """
        return MessageChannel.find_pending()
    
    @staticmethod
    def get_pending_message_ai() -> List[MessageAI]:
        """
        获取所有等待处理的消息AI处理
        
        Returns:
            List[MessageAI]: 等待处理的消息AI处理列表
        """
        return MessageAI.find_pending()
    
    @staticmethod
    def get_messages_by_api_token(api_token_id: str, limit: int = 100, offset: int = 0) -> List[Message]:
        """
        根据API令牌获取消息
        
        Args:
            api_token_id (str): API令牌ID
            limit (int, optional): 限制数量
            offset (int, optional): 偏移量
            
        Returns:
            List[Message]: 消息列表
        """
        conn = get_db()
        cursor = conn.execute(
            "SELECT * FROM messages WHERE api_token_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (api_token_id, limit, offset)
        )
        return [Message(**dict(row)) for row in cursor.fetchall()]
    
    @staticmethod
    def get_message_count_by_api_token(api_token_id: str) -> int:
        """
        获取API令牌的消息数量
        
        Args:
            api_token_id (str): API令牌ID
            
        Returns:
            int: 消息数量
        """
        return Message.count(api_token_id=api_token_id)
    
    @staticmethod
    def get_message_statistics(days: int = 7) -> Dict[str, int]:
        """
        获取消息统计信息
        
        Args:
            days (int, optional): 统计天数
            
        Returns:
            Dict[str, int]: 统计信息
        """
        conn = get_db()
        
        # 计算起始日期
        start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        
        # 获取总消息数
        cursor = conn.execute("SELECT COUNT(*) FROM messages")
        total_count = cursor.fetchone()[0]
        
        # 获取最近N天的消息数
        cursor = conn.execute(
            "SELECT COUNT(*) FROM messages WHERE created_at >= ?",
            (start_date,)
        )
        recent_count = cursor.fetchone()[0]
        
        # 获取成功发送的消息数
        cursor = conn.execute(
            "SELECT COUNT(DISTINCT message_id) FROM message_channels WHERE status = ?",
            (MessageChannel.STATUS_SUCCESS,)
        )
        success_count = cursor.fetchone()[0]
        
        # 获取失败的消息数
        cursor = conn.execute(
            "SELECT COUNT(DISTINCT message_id) FROM message_channels WHERE status = ?",
            (MessageChannel.STATUS_FAILED,)
        )
        failed_count = cursor.fetchone()[0]
        
        # 获取AI处理的消息数
        cursor = conn.execute(
            "SELECT COUNT(DISTINCT message_id) FROM message_ai WHERE status = ?",
            (MessageAI.STATUS_SUCCESS,)
        )
        ai_count = cursor.fetchone()[0]
        
        return {
            "total": total_count,
            "recent": recent_count,
            "success": success_count,
            "failed": failed_count,
            "ai": ai_count
        }
    
    @staticmethod
    def get_daily_message_count(days: int = 30) -> List[Tuple[str, int]]:
        """
        获取每日消息数量
        
        Args:
            days (int, optional): 统计天数
            
        Returns:
            List[Tuple[str, int]]: 每日消息数量列表，每个元素为(日期, 数量)
        """
        conn = get_db()
        
        # 计算起始日期
        start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        
        # 获取每日消息数量
        cursor = conn.execute(
            "SELECT date(created_at) as day, COUNT(*) as count FROM messages "
            "WHERE created_at >= ? GROUP BY day ORDER BY day",
            (start_date,)
        )
        
        return [(row[0], row[1]) for row in cursor.fetchall()] 