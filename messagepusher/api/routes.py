"""
API路由模块

该模块定义了API的路由和处理函数。
"""

import logging
import uuid
from datetime import datetime
from flask import Blueprint, jsonify, g, request, current_app
from typing import Dict, Any, List

# 导入认证和验证模块
from .auth import require_token
from .validators import validate_push_params, validate_message_id

# 导入数据库模块
from messagepusher.database.repository.message_repository import MessageRepository
from messagepusher.database.repository.channel_repository import ChannelRepository
from messagepusher.database.repository.ai_channel_repository import AIChannelRepository
from messagepusher.database.repository.message_channel import MessageChannelRepository
from messagepusher.database.repository.message_ai import MessageAIRepository

# 导入核心模块
from messagepusher.core.task_queue import TaskQueue, TaskType, TaskPriority
from messagepusher.core.message_processor import MessageProcessor

# 配置日志
logger = logging.getLogger(__name__)

def register_routes(blueprint: Blueprint) -> None:
    """
    注册API路由
    
    Args:
        blueprint: Flask蓝图实例
    """
    # 消息推送API
    blueprint.route('/push', methods=['POST', 'GET'])(push_message)
    
    # 消息状态查询API
    blueprint.route('/message/<message_id>', methods=['GET'])(get_message_status)
    
    logger.info("API路由注册成功")

@require_token
def push_message() -> Dict[str, Any]:
    """
    消息推送API
    
    Returns:
        Dict[str, Any]: API响应
    """
    # 验证请求参数
    is_valid, params, error_response = validate_push_params()
    if not is_valid:
        return error_response
    
    # 获取API令牌对象
    api_token = g.api_token
    
    # 创建消息ID和查看令牌
    message_id = str(uuid.uuid4())
    view_token = str(uuid.uuid4())
    
    # 准备消息数据
    message_data = {
        'id': message_id,
        'api_token_id': api_token.id,
        'title': params.get('title'),
        'content': params.get('content'),
        'url': params.get('url'),
        'view_token': view_token,
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    # 获取渠道列表
    channel_list = params.get('channel_list', [])
    if not channel_list and api_token.default_channels:
        # 使用API令牌的默认渠道
        channel_list = api_token.default_channels
    
    # 获取AI渠道
    ai_channel = params.get('ai_channel')
    if not ai_channel:
        # 尝试从'ai'参数获取
        ai_channel = params.get('ai')
    if not ai_channel and api_token.default_ai:
        # 使用API令牌的默认AI渠道
        ai_channel = api_token.default_ai
    
    try:
        # 保存消息到数据库
        message_repo = MessageRepository()
        message = message_repo.create(message_data)
        
        # 处理渠道列表
        if not channel_list:
            # 如果没有提供渠道，使用API令牌的默认渠道
            channel_list = api_token.default_channels
        
        if channel_list:
            channel_repo = ChannelRepository()
            message_channel_repo = MessageChannelRepository(db_connection=None)
            valid_channels = []
            for channel_id in channel_list:
                channel = channel_repo.get_channel(channel_id)
                if channel and channel.status == 'enabled':
                    valid_channels.append(channel_id)
                    # 创建消息渠道关联
                    message_channel_repo.add_channel({
                        'id': str(uuid.uuid4()),
                        'message_id': message_id,
                        'channel_id': channel_id,
                        'status': 'waiting',
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    })
            
            if not valid_channels and channel_list:
                logger.warning(f"所有指定的渠道都无效: {channel_list}")
                return jsonify({
                    'code': 1003,
                    'message': '渠道不存在或已禁用',
                    'data': None
                }), 400
            
            # 更新channel_list为只包含有效的渠道
            channel_list = valid_channels
        
        # 验证AI渠道是否存在
        if ai_channel:
            ai_channel_repo = AIChannelRepository()
            ai = ai_channel_repo.get_ai_channel(ai_channel)
            if not ai or ai.status != 'enabled':
                logger.warning(f"指定的AI渠道无效: {ai_channel}")
                return jsonify({
                    'code': 1004,
                    'message': 'AI渠道不存在或已禁用',
                    'data': None
                }), 400
            
            # 创建消息AI关联
            message_ai_repo = MessageAIRepository(db_connection=None)
            message_ai_repo.save_ai_result(message_id, {
                'id': str(uuid.uuid4()),
                'ai_channel_id': ai_channel,
                'status': 'waiting',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
        
        # 将消息添加到处理队列
        task_queue = TaskQueue()
        task_queue.create_task(
            task_type=TaskType.SEND_MESSAGE,
            data={'message_id': message_id},
            priority=TaskPriority.NORMAL
        )
        
        # 构建响应数据
        view_url = f"{request.host_url.rstrip('/')}/view/{view_token}"
        response_data = {
            'message_id': message_id,
            'channels': channel_list,
            'ai': ai_channel,
            'view_url': view_url
        }
        
        logger.info(f"消息推送成功: {message_id}")
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': response_data
        })
    
    except Exception as e:
        logger.error(f"消息推送失败: {str(e)}")
        return jsonify({
            'code': 1005,
            'message': f'消息发送失败: {str(e)}',
            'data': None
        }), 500

@require_token
def get_message_status(message_id: str) -> Dict[str, Any]:
    """
    消息状态查询API
    
    Args:
        message_id: 消息ID
    
    Returns:
        Dict[str, Any]: API响应
    """
    # 验证消息ID
    is_valid, error_response = validate_message_id(message_id)
    if not is_valid:
        return error_response
    
    try:
        # 获取消息
        message_repo = MessageRepository()
        message = message_repo.get_message(message_id)
        
        if not message:
            logger.warning(f"消息不存在: {message_id}")
            return jsonify({
                'code': 1006,
                'message': '消息不存在',
                'data': None
            }), 404
        
        # 验证API令牌是否有权限查看该消息
        api_token = g.api_token
        if message.api_token_id != api_token.id:
            logger.warning(f"无权访问消息: {message_id}")
            return jsonify({
                'code': 1001,
                'message': '无权访问该消息',
                'data': None
            }), 403
        
        # 获取消息渠道状态
        message_channel_repo = MessageChannelRepository(db_connection=None)
        channel_repo = ChannelRepository()
        channels_status = []
        
        message_channels = message.get_message_channels()
        for mc in message_channels:
            channel = channel_repo.get_channel(mc.channel_id)
            if channel:
                channels_status.append({
                    'id': channel.id,
                    'name': channel.name,
                    'status': mc.status,
                    'error': mc.error,
                    'sent_at': mc.sent_at.isoformat() if mc.sent_at else None
                })
        
        # 获取消息AI处理状态
        message_ai_repo = MessageAIRepository(db_connection=None)
        ai_channel_repo = AIChannelRepository()
        ai_status = None
        
        message_ai_list = message.get_message_ai()
        if message_ai_list and len(message_ai_list) > 0:
            message_ai = message_ai_list[0]
            ai_channel = ai_channel_repo.get_ai_channel(message_ai.ai_channel_id)
            if ai_channel:
                ai_status = {
                    'id': ai_channel.id,
                    'name': ai_channel.name,
                    'status': message_ai.status,
                    'result': message_ai.result,
                    'error': message_ai.error,
                    'processed_at': message_ai.processed_at.isoformat() if message_ai.processed_at else None
                }
        
        # 构建响应数据
        view_url = f"{request.host_url.rstrip('/')}/view/{message.view_token}"
        response_data = {
            'message_id': message.id,
            'title': message.title,
            'content': message.content,
            'url': message.url,
            'channels': channels_status,
            'ai': ai_status,
            'created_at': message.created_at.isoformat(),
            'view_url': view_url
        }
        
        logger.info(f"消息状态查询成功: {message_id}")
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': response_data
        })
    
    except Exception as e:
        logger.error(f"消息状态查询失败: {str(e)}")
        return jsonify({
            'code': 1005,
            'message': f'查询失败: {str(e)}',
            'data': None
        }), 500
