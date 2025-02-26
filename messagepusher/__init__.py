"""
MessagePusher

统一的消息推送服务，支持多种消息渠道和平台。
"""

import os
import logging
from flask import Flask
from logging.handlers import RotatingFileHandler

__version__ = "0.1.0"

def create_app(test_config=None):
    """
    创建并配置Flask应用程序
    
    Args:
        test_config: 测试配置
    
    Returns:
        Flask: Flask应用程序实例
    """
    # 创建Flask应用
    app = Flask(__name__, instance_relative_config=True)
    
    # 设置默认配置
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'messagepusher.sqlite'),
        LOG_LEVEL=logging.INFO,
        LOG_FILE=os.path.join(app.instance_path, 'messagepusher.log'),
    )
    
    if test_config is None:
        # 加载实例配置（如果存在）
        app.config.from_pyfile('config.py', silent=True)
    else:
        # 加载测试配置
        app.config.from_mapping(test_config)
    
    # 确保实例文件夹存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # 配置日志
    configure_logging(app)
    
    # 初始化数据库
    from messagepusher.database import init_db
    # 设置环境变量以指定数据库路径
    if 'DATABASE' in app.config:
        os.environ['MESSAGEPUSHER_DB_PATH'] = app.config['DATABASE']
    # 调用init_db，不传递app参数
    init_db()
    
    # 初始化核心模块
    from messagepusher.core import init_core
    init_core(app)
    
    # 初始化API模块
    from messagepusher.api import init_api
    init_api(app)
    
    # 注册首页路由
    @app.route('/')
    def index():
        return {
            'name': 'MessagePusher',
            'version': __version__,
            'status': 'running'
        }
    
    return app

def configure_logging(app):
    """
    配置日志
    
    Args:
        app: Flask应用程序实例
    """
    log_level = app.config.get('LOG_LEVEL', logging.INFO)
    log_file = app.config.get('LOG_FILE')
    
    # 创建日志处理器
    handlers = [logging.StreamHandler()]
    
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 添加文件处理器
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10485760, backupCount=10
        )
        handlers.append(file_handler)
    
    # 配置日志格式
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    for handler in handlers:
        handler.setFormatter(log_format)
        root_logger.addHandler(handler)
    
    # 设置Flask日志
    app.logger.setLevel(log_level) 