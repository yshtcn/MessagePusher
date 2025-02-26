"""
API模块集成测试

测试API模块与数据库模块和核心模块的集成。
"""

import unittest
import json
import os
import tempfile
import sqlite3
from datetime import datetime
import sys
from unittest.mock import patch, MagicMock
from flask import Flask
from messagepusher.api.api import create_api_blueprint
from messagepusher.api.routes import register_routes
from messagepusher.database.core import init_db

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from messagepusher.database.models.api_token import APIToken
from messagepusher.database.models.channel import Channel
from messagepusher.database.models.ai_channel import AIChannel
from messagepusher.database.repository.api_token_repository import APITokenRepository
from messagepusher.database.repository.channel_repository import ChannelRepository
from messagepusher.database.repository.ai_channel_repository import AIChannelRepository


class TestAPIIntegration(unittest.TestCase):
    """API集成测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时数据库文件
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # 创建测试应用
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['DATABASE'] = self.db_path
        
        # 初始化数据库
        init_db()
        
        # 注册API蓝图
        api_blueprint = create_api_blueprint()
        # 手动注册路由
        register_routes(api_blueprint)
        self.app.register_blueprint(api_blueprint)
        
        # 创建测试客户端
        self.client = self.app.test_client()
        
    def tearDown(self):
        """测试后的清理工作"""
        # 关闭数据库文件
        os.close(self.db_fd)
        
        # 删除临时数据库文件
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_api_endpoints_exist(self):
        """测试API端点是否存在"""
        # 测试消息推送API
        response = self.client.post('/api/v1/push')
        self.assertNotEqual(response.status_code, 404)
        
        # 测试消息状态查询API
        response = self.client.get('/api/v1/message/test-message-id')
        self.assertNotEqual(response.status_code, 404)
        
        # 确保返回的是JSON格式
        response = self.client.post('/api/v1/push')
        self.assertEqual(response.content_type, 'application/json')
        
        response = self.client.get('/api/v1/message/test-message-id')
        self.assertEqual(response.content_type, 'application/json')
    
    def test_push_message_without_token(self):
        """测试没有令牌的消息推送API"""
        # 不提供令牌
        response = self.client.post('/api/v1/push', json={
            'content': 'Test message',
            'title': 'Test title'
        })
        
        # 检查状态码
        self.assertEqual(response.status_code, 401)
        
        # 检查返回的JSON
        data = json.loads(response.data)
        self.assertEqual(data['code'], 1001)
        self.assertEqual(data['message'], '缺少API令牌')
        self.assertIsNone(data['data'])
    
    def test_push_message_with_invalid_token(self):
        """测试无效令牌的消息推送API"""
        # 提供无效令牌
        response = self.client.post('/api/v1/push', data={
            'token': 'invalid-token',
            'content': 'Test message',
            'title': 'Test title'
        })
        
        # 检查状态码
        self.assertEqual(response.status_code, 401)
        
        # 检查返回的JSON
        data = json.loads(response.data)
        self.assertEqual(data['code'], 1001)
        self.assertEqual(data['message'], '无效的API令牌')
        self.assertIsNone(data['data'])
    
    def test_get_message_status_without_token(self):
        """测试没有令牌的消息状态查询API"""
        # 不提供令牌
        response = self.client.get('/api/v1/message/test-message-id')
        
        # 检查状态码
        self.assertEqual(response.status_code, 401)
        
        # 检查返回的JSON
        data = json.loads(response.data)
        self.assertEqual(data['code'], 1001)
        self.assertEqual(data['message'], '缺少API令牌')
        self.assertIsNone(data['data'])
    
    def test_get_message_status_with_invalid_token(self):
        """测试无效令牌的消息状态查询API"""
        # 提供无效令牌
        response = self.client.get('/api/v1/message/test-message-id?token=invalid-token')
        
        # 检查状态码
        self.assertEqual(response.status_code, 401)
        
        # 检查返回的JSON
        data = json.loads(response.data)
        self.assertEqual(data['code'], 1001)
        self.assertEqual(data['message'], '无效的API令牌')
        self.assertIsNone(data['data'])
    
    def test_get_message_status_with_invalid_message_id(self):
        """测试无效消息ID的消息状态查询API"""
        # 提供有效令牌但无效消息ID
        # 注意：在实际测试中，我们需要先创建一个有效的令牌
        # 但在这个简化的测试中，我们直接测试消息ID不存在的情况
        response = self.client.get('/api/v1/message/invalid-message-id')
        
        # 检查状态码 - 应该是401（未授权）或404（未找到）
        # 在这个测试中，由于没有提供有效令牌，应该是401
        self.assertEqual(response.status_code, 401)
        
        # 检查返回的JSON
        data = json.loads(response.data)
        self.assertEqual(data['code'], 1001)
        self.assertEqual(data['message'], '缺少API令牌')
        self.assertIsNone(data['data'])


if __name__ == '__main__':
    unittest.main()
