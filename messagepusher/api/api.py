"""
API蓝图创建模块

该模块负责创建Flask蓝图，用于API路由的注册和管理。
"""

import logging
from flask import Blueprint, jsonify

# 配置日志
logger = logging.getLogger(__name__)

def create_api_blueprint() -> Blueprint:
    """
    创建API蓝图
    
    Returns:
        Blueprint: Flask蓝图实例
    """
    # 创建蓝图，URL前缀为/api/v1
    api_blueprint = Blueprint('api', __name__, url_prefix='/api/v1')
    
    # 注册错误处理器
    register_error_handlers(api_blueprint)
    
    logger.info("API蓝图创建成功")
    return api_blueprint

def register_error_handlers(blueprint: Blueprint) -> None:
    """
    注册错误处理器
    
    Args:
        blueprint: Flask蓝图实例
    """
    @blueprint.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'code': 1002,
            'message': '参数错误',
            'data': None
        }), 400
    
    @blueprint.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'code': 1001,
            'message': '无效的API令牌',
            'data': None
        }), 401
    
    @blueprint.errorhandler(404)
    def not_found(error):
        return jsonify({
            'code': 1006,
            'message': '资源不存在',
            'data': None
        }), 404
    
    @blueprint.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"服务器内部错误: {str(error)}")
        return jsonify({
            'code': 1005,
            'message': '服务器内部错误',
            'data': None
        }), 500
