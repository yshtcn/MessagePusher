"""
API模块测试

测试API模块的功能。
"""

import unittest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from flask import Flask

from messagepusher import create_app
from messagepusher.database.models.api_token import APIToken
from messagepusher.database.models.message import Message
from messagepusher.database.models.channel import Channel
from messagepusher.database.models.ai_channel import AIChannel
from messagepusher.database.models.message_channel import MessageChannel
from messagepusher.database.models.message_ai import MessageAI


class TestAPI(unittest.TestCase):
    """API模块测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建测试应用
        self.app = create_app({
            'TESTING': True,
            'DATABASE': ':memory:'
        })
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """测试后的清理工作"""
        self.app_context.pop()
    
    @patch('messagepusher.database.repository.api_token_repository.APITokenRepository.get_token_by_token_value')
    @patch('messagepusher.database.repository.message_repository.MessageRepository.create')
    @patch('messagepusher.core.task_queue.TaskQueue.create_task')
    def test_push_message(self, mock_create_task, mock_create_message, mock_get_token):
        """测试消息推送API"""
        # 模拟API令牌
        mock_token = MagicMock(spec=APIToken)
        mock_token.id = '123456'
        mock_token.status = 'enabled'
        mock_token.default_channels = []
        mock_token.default_ai = None
        mock_token.is_expired.return_value = False
        mock_get_token.return_value = mock_token
        
        # 模拟消息创建
        mock_message = MagicMock()
        mock_message.id = '789012'
        mock_create_message.return_value = mock_message
        
        # 发送请求
        response = self.client.post('/api/v1/push', data={
            'token': 'test_token',
            'title': '测试标题',
            'content': '测试内容'
        })
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 0)
        self.assertEqual(data['message'], 'success')
        self.assertIn('message_id', data['data'])
        self.assertIn('view_url', data['data'])
        
        # 验证方法调用
        mock_get_token.assert_called_once_with('test_token')
        mock_create_message.assert_called_once()
        mock_create_task.assert_called_once()
    
    @patch('messagepusher.database.repository.api_token_repository.APITokenRepository.get_token_by_token_value')
    @patch('messagepusher.database.repository.message_repository.MessageRepository.create')
    @patch('messagepusher.database.repository.channel_repository.ChannelRepository.get_channel')
    @patch('messagepusher.database.repository.message_channel.MessageChannelRepository')
    @patch('messagepusher.core.task_queue.TaskQueue.create_task')
    def test_push_message_with_channels(self, mock_create_task, mock_message_channel_repo, 
                                       mock_get_channel, mock_create_message, mock_get_token):
        """测试带有渠道的消息推送API"""
        # 模拟API令牌
        mock_token = MagicMock(spec=APIToken)
        mock_token.id = '123456'
        mock_token.status = 'enabled'
        mock_token.default_channels = []
        mock_token.default_ai = None
        mock_token.is_expired.return_value = False
        mock_get_token.return_value = mock_token
        
        # 模拟消息创建
        mock_message = MagicMock()
        mock_message.id = '789012'
        mock_create_message.return_value = mock_message
        
        # 模拟渠道
        mock_channel = MagicMock(spec=Channel)
        mock_channel.id = 'channel1'
        mock_channel.status = 'enabled'
        mock_get_channel.return_value = mock_channel
        
        # 模拟消息渠道仓库
        mock_repo_instance = MagicMock()
        mock_message_channel_repo.return_value = mock_repo_instance
        
        # 发送请求
        response = self.client.post('/api/v1/push', data={
            'token': 'test_token',
            'title': '测试标题',
            'content': '测试内容',
            'channels': 'channel1|channel2'
        })
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 0)
        self.assertEqual(data['message'], 'success')
        self.assertIn('message_id', data['data'])
        self.assertIn('channels', data['data'])
        self.assertEqual(data['data']['channels'], ['channel1'])
        
        # 验证方法调用
        mock_get_token.assert_called_once_with('test_token')
        mock_create_message.assert_called_once()
        mock_get_channel.assert_called()
        mock_repo_instance.add_channel.assert_called_once()
        mock_create_task.assert_called_once()
    
    @patch('messagepusher.database.repository.api_token_repository.APITokenRepository.get_token_by_token_value')
    @patch('messagepusher.database.repository.message_repository.MessageRepository.create')
    @patch('messagepusher.database.repository.ai_channel_repository.AIChannelRepository.get_ai_channel')
    @patch('messagepusher.database.repository.message_ai.MessageAIRepository')
    @patch('messagepusher.core.task_queue.TaskQueue.create_task')
    def test_push_message_with_ai(self, mock_create_task, mock_message_ai_repo, 
                                 mock_get_ai_channel, mock_create_message, mock_get_token):
        """测试带有AI渠道的消息推送API"""
        # 模拟API令牌
        mock_token = MagicMock(spec=APIToken)
        mock_token.id = '123456'
        mock_token.status = 'enabled'
        mock_token.default_channels = []
        mock_token.default_ai = None
        mock_token.is_expired.return_value = False
        mock_get_token.return_value = mock_token
        
        # 模拟消息创建
        mock_message = MagicMock()
        mock_message.id = '789012'
        mock_create_message.return_value = mock_message
        
        # 模拟AI渠道
        mock_ai_channel = MagicMock(spec=AIChannel)
        mock_ai_channel.id = 'ai1'
        mock_ai_channel.status = 'enabled'
        mock_get_ai_channel.return_value = mock_ai_channel
        
        # 模拟消息AI仓库
        mock_repo_instance = MagicMock()
        mock_message_ai_repo.return_value = mock_repo_instance
        
        # 发送请求
        response = self.client.post('/api/v1/push', data={
            'token': 'test_token',
            'title': '测试标题',
            'content': '测试内容',
            'ai': 'ai1'
        })
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 0)
        self.assertEqual(data['message'], 'success')
        self.assertIn('message_id', data['data'])
        self.assertIn('ai', data['data'])
        self.assertEqual(data['data']['ai'], 'ai1')
        
        # 验证方法调用
        mock_get_token.assert_called_once_with('test_token')
        mock_create_message.assert_called_once()
        mock_get_ai_channel.assert_called_once_with('ai1')
        mock_repo_instance.save_ai_result.assert_called_once()
        mock_create_task.assert_called_once()
    
    @patch('messagepusher.database.repository.api_token_repository.APITokenRepository.get_token_by_token_value')
    @patch('messagepusher.database.repository.message_repository.MessageRepository.create')
    @patch('messagepusher.database.repository.channel_repository.ChannelRepository.get_channel')
    def test_push_message_invalid_channel(self, mock_get_channel, mock_create_message, mock_get_token):
        """测试无效渠道的情况"""
        # 模拟API令牌
        mock_token = MagicMock(spec=APIToken)
        mock_token.id = '123456'
        mock_token.status = 'enabled'
        mock_token.default_channels = []
        mock_token.default_ai = None
        mock_token.is_expired.return_value = False
        mock_get_token.return_value = mock_token
        
        # 模拟消息创建
        mock_message = MagicMock()
        mock_message.id = '789012'
        mock_create_message.return_value = mock_message
        
        # 模拟无效渠道
        mock_get_channel.return_value = None
        
        # 发送请求
        response = self.client.post('/api/v1/push', data={
            'token': 'test_token',
            'title': '测试标题',
            'content': '测试内容',
            'channels': 'invalid_channel'
        })
        
        # 验证响应
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 1003)
        self.assertEqual(data['message'], '渠道不存在或已禁用')
    
    @patch('messagepusher.database.repository.api_token_repository.APITokenRepository.get_token_by_token_value')
    @patch('messagepusher.database.repository.message_repository.MessageRepository.create')
    @patch('messagepusher.database.repository.ai_channel_repository.AIChannelRepository.get_ai_channel')
    def test_push_message_invalid_ai(self, mock_get_ai_channel, mock_create_message, mock_get_token):
        """测试无效AI渠道的情况"""
        # 模拟API令牌
        mock_token = MagicMock(spec=APIToken)
        mock_token.id = '123456'
        mock_token.status = 'enabled'
        mock_token.default_channels = []
        mock_token.default_ai = None
        mock_token.is_expired.return_value = False
        mock_get_token.return_value = mock_token
        
        # 模拟消息创建
        mock_message = MagicMock()
        mock_message.id = '789012'
        mock_create_message.return_value = mock_message
        
        # 模拟无效AI渠道
        mock_get_ai_channel.return_value = None
        
        # 发送请求
        response = self.client.post('/api/v1/push', data={
            'token': 'test_token',
            'title': '测试标题',
            'content': '测试内容',
            'ai': 'invalid_ai'
        })
        
        # 验证响应
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 1004)
        self.assertEqual(data['message'], 'AI渠道不存在或已禁用')
    
    @patch('messagepusher.database.repository.api_token_repository.APITokenRepository.get_token_by_token_value')
    def test_push_message_invalid_token(self, mock_get_token):
        """测试无效令牌的情况"""
        # 模拟无效令牌
        mock_get_token.return_value = None
        
        # 发送请求
        response = self.client.post('/api/v1/push', data={
            'token': 'invalid_token',
            'title': '测试标题',
            'content': '测试内容'
        })
        
        # 验证响应
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 1001)
        self.assertEqual(data['message'], '无效的API令牌')
    
    @patch('messagepusher.database.repository.api_token_repository.APITokenRepository.get_token_by_token_value')
    def test_push_message_disabled_token(self, mock_get_token):
        """测试禁用令牌的情况"""
        # 模拟禁用令牌
        mock_token = MagicMock(spec=APIToken)
        mock_token.id = '123456'
        mock_token.status = 'disabled'
        mock_get_token.return_value = mock_token
        
        # 发送请求
        response = self.client.post('/api/v1/push', data={
            'token': 'disabled_token',
            'title': '测试标题',
            'content': '测试内容'
        })
        
        # 验证响应
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 1001)
        self.assertEqual(data['message'], 'API令牌已禁用')
    
    @patch('messagepusher.database.repository.api_token_repository.APITokenRepository.get_token_by_token_value')
    def test_push_message_expired_token(self, mock_get_token):
        """测试过期令牌的情况"""
        # 模拟过期令牌
        mock_token = MagicMock(spec=APIToken)
        mock_token.id = '123456'
        mock_token.status = 'enabled'
        mock_token.is_expired.return_value = True
        mock_get_token.return_value = mock_token
        
        # 发送请求
        response = self.client.post('/api/v1/push', data={
            'token': 'expired_token',
            'title': '测试标题',
            'content': '测试内容'
        })
        
        # 验证响应
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 1001)
        self.assertEqual(data['message'], 'API令牌已过期')
    
    @patch('messagepusher.database.repository.api_token_repository.APITokenRepository.get_token_by_token_value')
    def test_push_message_missing_params(self, mock_get_token):
        """测试缺少参数的情况"""
        # 模拟API令牌
        mock_token = MagicMock(spec=APIToken)
        mock_token.id = '123456'
        mock_token.status = 'enabled'
        mock_token.is_expired.return_value = False
        mock_get_token.return_value = mock_token
        
        # 发送请求（缺少必要参数）
        response = self.client.post('/api/v1/push', data={
            'token': 'test_token'
        })
        
        # 验证响应
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 1002)
        self.assertIn('参数错误', data['message'])
    
    @patch('messagepusher.database.repository.api_token_repository.APITokenRepository.get_token_by_token_value')
    @patch('messagepusher.database.repository.message_repository.MessageRepository.get_message')
    def test_get_message_status(self, mock_get_message, mock_get_token):
        """测试消息状态查询API"""
        # 模拟API令牌
        mock_token = MagicMock(spec=APIToken)
        mock_token.id = '123456'
        mock_token.status = 'enabled'
        mock_token.is_expired.return_value = False
        mock_get_token.return_value = mock_token
        
        # 模拟消息
        mock_message = MagicMock(spec=Message)
        mock_message.id = 'message123'
        mock_message.api_token_id = '123456'
        mock_message.title = '测试标题'
        mock_message.content = '测试内容'
        mock_message.url = 'https://example.com'
        mock_message.view_token = 'view_token123'
        mock_message.created_at = datetime.now()
        mock_get_message.return_value = mock_message
        
        # 模拟消息渠道和AI处理
        mock_message.get_message_channels.return_value = []
        mock_message.get_message_ai.return_value = []
        
        # 发送请求
        response = self.client.get('/api/v1/message/message123?token=test_token')
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 0)
        self.assertEqual(data['message'], 'success')
        self.assertEqual(data['data']['message_id'], 'message123')
        self.assertEqual(data['data']['title'], '测试标题')
        self.assertEqual(data['data']['content'], '测试内容')
        self.assertEqual(data['data']['url'], 'https://example.com')
        self.assertIn('view_url', data['data'])
        self.assertIn('channels', data['data'])
        self.assertIn('created_at', data['data'])
    
    @patch('messagepusher.database.repository.api_token_repository.APITokenRepository.get_token_by_token_value')
    @patch('messagepusher.database.repository.message_repository.MessageRepository.get_message')
    def test_get_message_status_not_found(self, mock_get_message, mock_get_token):
        """测试消息不存在的情况"""
        # 模拟API令牌
        mock_token = MagicMock(spec=APIToken)
        mock_token.id = '123456'
        mock_token.status = 'enabled'
        mock_token.is_expired.return_value = False
        mock_get_token.return_value = mock_token
        
        # 模拟消息不存在
        mock_get_message.return_value = None
        
        # 发送请求
        response = self.client.get('/api/v1/message/nonexistent?token=test_token')
        
        # 验证响应
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 1006)
        self.assertEqual(data['message'], '消息不存在')
    
    @patch('messagepusher.database.repository.api_token_repository.APITokenRepository.get_token_by_token_value')
    @patch('messagepusher.database.repository.message_repository.MessageRepository.get_message')
    def test_get_message_status_unauthorized(self, mock_get_message, mock_get_token):
        """测试无权访问消息的情况"""
        # 模拟API令牌
        mock_token = MagicMock(spec=APIToken)
        mock_token.id = '123456'
        mock_token.status = 'enabled'
        mock_token.is_expired.return_value = False
        mock_get_token.return_value = mock_token
        
        # 模拟消息（属于其他用户）
        mock_message = MagicMock(spec=Message)
        mock_message.id = 'message123'
        mock_message.api_token_id = '789012'  # 不同的令牌ID
        mock_get_message.return_value = mock_message
        
        # 发送请求
        response = self.client.get('/api/v1/message/message123?token=test_token')
        
        # 验证响应
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 1001)
        self.assertEqual(data['message'], '无权访问该消息')
    
    @patch('messagepusher.database.repository.api_token_repository.APITokenRepository.get_token_by_token_value')
    @patch('messagepusher.database.repository.message_repository.MessageRepository.get_message')
    @patch('messagepusher.database.repository.channel_repository.ChannelRepository.get_channel')
    def test_get_message_status_with_channels(self, mock_get_channel, mock_get_message, mock_get_token):
        """测试带有渠道的消息状态查询"""
        # 模拟API令牌
        mock_token = MagicMock(spec=APIToken)
        mock_token.id = '123456'
        mock_token.status = 'enabled'
        mock_token.is_expired.return_value = False
        mock_get_token.return_value = mock_token
        
        # 模拟消息
        mock_message = MagicMock(spec=Message)
        mock_message.id = 'message123'
        mock_message.api_token_id = '123456'
        mock_message.title = '测试标题'
        mock_message.content = '测试内容'
        mock_message.url = 'https://example.com'
        mock_message.view_token = 'view_token123'
        mock_message.created_at = datetime.now()
        mock_get_message.return_value = mock_message
        
        # 模拟消息渠道
        mock_channel = MagicMock(spec=Channel)
        mock_channel.id = 'channel1'
        mock_channel.name = 'Telegram'
        mock_get_channel.return_value = mock_channel
        
        mock_message_channel = MagicMock(spec=MessageChannel)
        mock_message_channel.channel_id = 'channel1'
        mock_message_channel.status = 'sent'
        mock_message_channel.error = None
        mock_message_channel.sent_at = datetime.now()
        
        mock_message.get_message_channels.return_value = [mock_message_channel]
        mock_message.get_message_ai.return_value = []
        
        # 发送请求
        response = self.client.get('/api/v1/message/message123?token=test_token')
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 0)
        self.assertEqual(data['message'], 'success')
        self.assertEqual(data['data']['message_id'], 'message123')
        self.assertIn('channels', data['data'])
        self.assertEqual(len(data['data']['channels']), 1)
        self.assertEqual(data['data']['channels'][0]['id'], 'channel1')
        self.assertEqual(data['data']['channels'][0]['name'], 'Telegram')
        self.assertEqual(data['data']['channels'][0]['status'], 'sent')
    
    @patch('messagepusher.database.repository.api_token_repository.APITokenRepository.get_token_by_token_value')
    @patch('messagepusher.database.repository.message_repository.MessageRepository.get_message')
    @patch('messagepusher.database.repository.ai_channel_repository.AIChannelRepository.get_ai_channel')
    def test_get_message_status_with_ai(self, mock_get_ai_channel, mock_get_message, mock_get_token):
        """测试带有AI处理的消息状态查询"""
        # 模拟API令牌
        mock_token = MagicMock(spec=APIToken)
        mock_token.id = '123456'
        mock_token.status = 'enabled'
        mock_token.is_expired.return_value = False
        mock_get_token.return_value = mock_token
        
        # 模拟消息
        mock_message = MagicMock(spec=Message)
        mock_message.id = 'message123'
        mock_message.api_token_id = '123456'
        mock_message.title = '测试标题'
        mock_message.content = '测试内容'
        mock_message.url = 'https://example.com'
        mock_message.view_token = 'view_token123'
        mock_message.created_at = datetime.now()
        mock_get_message.return_value = mock_message
        
        # 模拟AI渠道
        mock_ai_channel = MagicMock(spec=AIChannel)
        mock_ai_channel.id = 'ai1'
        mock_ai_channel.name = 'OpenAI'
        mock_get_ai_channel.return_value = mock_ai_channel
        
        # 模拟消息AI处理
        mock_message_ai = MagicMock(spec=MessageAI)
        mock_message_ai.ai_channel_id = 'ai1'
        mock_message_ai.status = 'processed'
        mock_message_ai.result = 'AI处理结果'
        mock_message_ai.error = None
        mock_message_ai.processed_at = datetime.now()
        
        mock_message.get_message_channels.return_value = []
        mock_message.get_message_ai.return_value = [mock_message_ai]
        
        # 发送请求
        response = self.client.get('/api/v1/message/message123?token=test_token')
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 0)
        self.assertEqual(data['message'], 'success')
        self.assertEqual(data['data']['message_id'], 'message123')
        self.assertIn('ai', data['data'])
        self.assertIsNotNone(data['data']['ai'])
        self.assertEqual(data['data']['ai']['id'], 'ai1')
        self.assertEqual(data['data']['ai']['name'], 'OpenAI')
        self.assertEqual(data['data']['ai']['status'], 'processed')
        self.assertEqual(data['data']['ai']['result'], 'AI处理结果')


if __name__ == '__main__':
    unittest.main()
