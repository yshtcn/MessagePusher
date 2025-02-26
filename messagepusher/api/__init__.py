"""
MessagePusher API模块

该模块提供了MessagePusher的HTTP API接口，用于接收和处理消息推送请求。
"""

from flask import Flask
from .api import create_api_blueprint
from .routes import register_routes

def init_api(app: Flask) -> None:
    """
    初始化API模块
    
    Args:
        app: Flask应用实例
    """
    # 创建API蓝图并注册路由
    api_blueprint = create_api_blueprint()
    register_routes(api_blueprint)
    
    # 注册蓝图到Flask应用
    app.register_blueprint(api_blueprint)
