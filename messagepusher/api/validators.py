"""
API请求参数验证模块

该模块负责验证API请求的参数是否符合要求。
"""

import logging
from flask import request, jsonify
from typing import Dict, Any, Tuple, Optional, List, Union

# 配置日志
logger = logging.getLogger(__name__)

def validate_push_params() -> Tuple[bool, Optional[Dict[str, Any]], Optional[Tuple[Dict[str, Any], int]]]:
    """
    验证消息推送API的参数
    
    Returns:
        Tuple[bool, Optional[Dict[str, Any]], Optional[Tuple[Dict[str, Any], int]]]: 
            - 验证是否通过
            - 验证通过时的参数字典
            - 验证失败时的错误响应
    """
    # 获取请求参数
    params = {}
    if request.method == 'POST':
        if request.is_json:
            params = request.json
        else:
            params = request.form.to_dict()
    else:  # GET
        params = request.args.to_dict()
    
    # 验证必填参数
    title = params.get('title')
    content = params.get('content')
    url = params.get('url')
    
    # title、content、url至少需要提供一个
    if not any([title, content, url]):
        logger.warning("推送请求缺少必要参数: title, content, url至少需要提供一个")
        return False, None, (jsonify({
            'code': 1002,
            'message': '参数错误: title, content, url至少需要提供一个',
            'data': None
        }), 400)
    
    # 处理渠道参数
    channels = params.get('channels', '')
    if channels:
        try:
            # 将渠道字符串转换为列表
            channel_list = channels.split('|')
            params['channel_list'] = channel_list
        except Exception as e:
            logger.warning(f"渠道参数格式错误: {str(e)}")
            return False, None, (jsonify({
                'code': 1002,
                'message': '渠道参数格式错误',
                'data': None
            }), 400)
    else:
        params['channel_list'] = []
    
    # 处理AI渠道参数
    ai = params.get('ai')
    if ai:
        params['ai_channel'] = ai
    
    return True, params, None

def validate_message_id(message_id: str) -> Tuple[bool, Optional[Tuple[Dict[str, Any], int]]]:
    """
    验证消息ID是否有效
    
    Args:
        message_id: 消息ID
    
    Returns:
        Tuple[bool, Optional[Tuple[Dict[str, Any], int]]]:
            - 验证是否通过
            - 验证失败时的错误响应
    """
    if not message_id or not message_id.strip():
        logger.warning("无效的消息ID")
        return False, (jsonify({
            'code': 1006,
            'message': '无效的消息ID',
            'data': None
        }), 400)
    
    return True, None
