"""
API认证模块

该模块负责API请求的认证，验证API令牌的有效性。
"""

import logging
from functools import wraps
from flask import request, jsonify, g
from typing import Callable, Any

# 导入数据库模块
from messagepusher.database.repository.api_token_repository import APITokenRepository

# 配置日志
logger = logging.getLogger(__name__)

def require_token(f: Callable) -> Callable:
    """
    API令牌验证装饰器
    
    Args:
        f: 被装饰的函数
    
    Returns:
        装饰后的函数
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        # 从请求参数中获取token
        token = request.args.get('token') or request.form.get('token')
        
        if not token:
            logger.warning("API请求缺少令牌")
            return jsonify({
                'code': 1001,
                'message': '缺少API令牌',
                'data': None
            }), 401
        
        # 验证令牌
        api_token_repo = APITokenRepository()
        api_token = api_token_repo.get_token_by_token_value(token)
        
        if not api_token:
            logger.warning(f"无效的API令牌: {token}")
            return jsonify({
                'code': 1001,
                'message': '无效的API令牌',
                'data': None
            }), 401
        
        if api_token.status != 'enabled':
            logger.warning(f"API令牌已禁用: {token}")
            return jsonify({
                'code': 1001,
                'message': 'API令牌已禁用',
                'data': None
            }), 401
        
        # 检查令牌是否过期
        if api_token.is_expired():
            logger.warning(f"API令牌已过期: {token}")
            return jsonify({
                'code': 1001,
                'message': 'API令牌已过期',
                'data': None
            }), 401
        
        # 将API令牌对象存储在g对象中，以便后续使用
        g.api_token = api_token
        
        return f(*args, **kwargs)
    
    return decorated_function
