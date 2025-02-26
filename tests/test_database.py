"""
数据库模块测试脚本

测试数据库的初始化和基本的增删查改操作。
"""

import os
import sys
import uuid
import json
import datetime
import shutil
import logging
import traceback
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from messagepusher.database import init_db, get_db, close_db
from messagepusher.database.models import Channel, AIChannel, APIToken, SystemConfig
from messagepusher.database.repository import (
    ChannelRepository, AIChannelRepository, 
    APITokenRepository, SystemConfigRepository
)

# 测试数据库路径
TEST_DB_PATH = "data/test_db.db"


def setup():
    """设置测试环境"""
    print("=== 设置测试环境 ===")
    
    # 确保测试数据目录存在
    os.makedirs("data", exist_ok=True)
    
    # 如果测试数据库已存在，则删除
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    # 设置环境变量指定测试数据库路径
    os.environ["MESSAGEPUSHER_DB_PATH"] = TEST_DB_PATH
    
    # 初始化数据库
    init_db()
    
    print(f"测试数据库已初始化: {TEST_DB_PATH}")


def teardown():
    """清理测试环境"""
    print("\n=== 清理测试环境 ===")
    
    # 关闭数据库连接
    close_db()
    
    # 删除测试数据库
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    print(f"测试数据库已删除: {TEST_DB_PATH}")


def test_system_config():
    """测试系统配置模块"""
    print("\n=== 测试系统配置模块 ===")
    
    try:
        # 获取默认配置
        version = SystemConfigRepository.get_version()
        print(f"系统版本: {version}")
        
        # 设置新配置
        result = SystemConfigRepository.set_config("test_key", "test_value", "测试配置项")
        print(f"设置配置项 test_key 结果: {'成功' if result else '失败'}")
        
        value = SystemConfigRepository.get_config("test_key")
        print(f"设置配置项 test_key = {value}")
        
        # 更新配置
        result = SystemConfigRepository.set_config("test_key", "updated_value")
        print(f"更新配置项 test_key 结果: {'成功' if result else '失败'}")
        
        value = SystemConfigRepository.get_config("test_key")
        print(f"更新配置项 test_key = {value}")
        
        # 获取所有配置
        configs = SystemConfigRepository.get_all_configs()
        print(f"配置项数量: {len(configs)}")
        
        # 删除配置
        result = SystemConfigRepository.delete_config("test_key")
        print(f"删除配置项 test_key: {'成功' if result else '失败'}")
        
        value = SystemConfigRepository.get_config("test_key")
        print(f"删除后获取 test_key = {value}")
        
        print("系统配置模块测试完成")
    except Exception as e:
        print(f"系统配置模块测试出错: {e}")
        traceback.print_exc()


def test_channel():
    """测试消息渠道模块"""
    print("\n=== 测试消息渠道模块 ===")
    
    try:
        # 创建渠道
        params = {
            "title": "{title}",
            "body": "{content}",
            "url": "{url}"
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {api_key}"
        }
        placeholders = {
            "api_key": "test_api_key_123456"
        }
        proxy = {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890"
        }
        
        channel = ChannelRepository.create_channel(
            name="测试渠道",
            api_url="https://api.example.com/push",
            method="POST",
            content_type="json",
            params=params,
            headers=headers,
            placeholders=placeholders,
            proxy=proxy,
            max_length=1000
        )
        
        print(f"创建渠道: {channel.id}, 名称: {channel.name}")
        
        # 获取渠道
        retrieved_channel = ChannelRepository.get_channel(channel.id)
        print(f"获取渠道: {retrieved_channel.id}, 名称: {retrieved_channel.name}")
        
        # 检查 JSON 字段
        print(f"参数映射: {retrieved_channel.params_dict}")
        print(f"请求头: {retrieved_channel.headers_dict}")
        print(f"占位符: {retrieved_channel.placeholders_dict}")
        print(f"代理配置: {retrieved_channel.proxy_dict}")
        
        # 更新渠道
        updated_channel = ChannelRepository.update_channel(
            channel_id=channel.id,
            name="更新后的测试渠道",
            max_length=2000
        )
        print(f"更新渠道: {updated_channel.id}, 名称: {updated_channel.name}, 最大长度: {updated_channel.max_length}")
        
        # 禁用渠道
        disabled_channel = ChannelRepository.disable_channel(channel.id)
        print(f"禁用渠道: {disabled_channel.id}, 状态: {disabled_channel.status}")
        
        # 启用渠道
        enabled_channel = ChannelRepository.enable_channel(channel.id)
        print(f"启用渠道: {enabled_channel.id}, 状态: {enabled_channel.status}")
        
        # 获取所有渠道
        all_channels = ChannelRepository.get_all_channels()
        print(f"所有渠道数量: {len(all_channels)}")
        
        # 获取启用的渠道
        enabled_channels = ChannelRepository.get_enabled_channels()
        print(f"启用的渠道数量: {len(enabled_channels)}")
        
        # 删除渠道
        result = ChannelRepository.delete_channel(channel.id)
        print(f"删除渠道: {'成功' if result else '失败'}")
        
        # 验证删除
        deleted_channel = ChannelRepository.get_channel(channel.id)
        print(f"获取已删除渠道: {'不存在' if deleted_channel is None else '仍然存在'}")
        
        print("消息渠道模块测试完成")
    except Exception as e:
        print(f"消息渠道模块测试出错: {e}")
        traceback.print_exc()


def test_ai_channel():
    """测试 AI 渠道模块"""
    print("\n=== 测试 AI 渠道模块 ===")
    
    try:
        # 创建 AI 渠道
        params = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 2000,
            "messages": [
                {"role": "system", "content": "{prompt}"},
                {"role": "user", "content": "{content}"}
            ]
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {api_key}"
        }
        placeholders = {
            "api_key": "sk-test_openai_key_123456"
        }
        proxy = {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890"
        }
        
        ai_channel = AIChannelRepository.create_ai_channel(
            name="测试 OpenAI",
            api_url="https://api.openai.com/v1/chat/completions",
            model="gpt-3.5-turbo",
            params=params,
            headers=headers,
            placeholders=placeholders,
            prompt="你是一个有用的助手，请简明扼要地回答问题。",
            proxy=proxy
        )
        
        print(f"创建 AI 渠道: {ai_channel.id}, 名称: {ai_channel.name}")
        
        # 获取 AI 渠道
        retrieved_ai_channel = AIChannelRepository.get_ai_channel(ai_channel.id)
        print(f"获取 AI 渠道: {retrieved_ai_channel.id}, 名称: {retrieved_ai_channel.name}")
        
        # 检查 JSON 字段
        print(f"参数映射: {retrieved_ai_channel.params_dict}")
        print(f"请求头: {retrieved_ai_channel.headers_dict}")
        print(f"占位符: {retrieved_ai_channel.placeholders_dict}")
        print(f"代理配置: {retrieved_ai_channel.proxy_dict}")
        print(f"Prompt: {retrieved_ai_channel.prompt}")
        
        # 更新 AI 渠道
        updated_ai_channel = AIChannelRepository.update_ai_channel(
            ai_channel_id=ai_channel.id,
            name="更新后的测试 OpenAI",
            prompt="你是一个专业的助手，请详细回答问题。"
        )
        print(f"更新 AI 渠道: {updated_ai_channel.id}, 名称: {updated_ai_channel.name}, Prompt: {updated_ai_channel.prompt}")
        
        # 禁用 AI 渠道
        disabled_ai_channel = AIChannelRepository.disable_ai_channel(ai_channel.id)
        print(f"禁用 AI 渠道: {disabled_ai_channel.id}, 状态: {disabled_ai_channel.status}")
        
        # 启用 AI 渠道
        enabled_ai_channel = AIChannelRepository.enable_ai_channel(ai_channel.id)
        print(f"启用 AI 渠道: {enabled_ai_channel.id}, 状态: {enabled_ai_channel.status}")
        
        # 获取所有 AI 渠道
        all_ai_channels = AIChannelRepository.get_all_ai_channels()
        print(f"所有 AI 渠道数量: {len(all_ai_channels)}")
        
        # 获取启用的 AI 渠道
        enabled_ai_channels = AIChannelRepository.get_enabled_ai_channels()
        print(f"启用的 AI 渠道数量: {len(enabled_ai_channels)}")
        
        # 获取特定模型的 AI 渠道
        model_ai_channels = AIChannelRepository.get_ai_channels_by_model("gpt-3.5-turbo")
        print(f"模型为 gpt-3.5-turbo 的 AI 渠道数量: {len(model_ai_channels)}")
        
        # 删除 AI 渠道
        result = AIChannelRepository.delete_ai_channel(ai_channel.id)
        print(f"删除 AI 渠道: {'成功' if result else '失败'}")
        
        # 验证删除
        deleted_ai_channel = AIChannelRepository.get_ai_channel(ai_channel.id)
        print(f"获取已删除 AI 渠道: {'不存在' if deleted_ai_channel is None else '仍然存在'}")
        
        print("AI 渠道模块测试完成")
    except Exception as e:
        print(f"AI 渠道模块测试出错: {e}")
        traceback.print_exc()


def test_api_token():
    """测试 API 令牌模块"""
    print("\n=== 测试 API 令牌模块 ===")
    
    try:
        # 创建渠道用于测试
        channel1 = ChannelRepository.create_channel(
            name="测试渠道1",
            api_url="https://api.example.com/push1",
            method="POST",
            content_type="json",
            params={"message": "{content}"}
        )
        
        channel2 = ChannelRepository.create_channel(
            name="测试渠道2",
            api_url="https://api.example.com/push2",
            method="POST",
            content_type="json",
            params={"message": "{content}"}
        )
        
        # 创建 AI 渠道用于测试
        ai_channel = AIChannelRepository.create_ai_channel(
            name="测试 AI",
            api_url="https://api.example.com/ai",
            model="test-model",
            params={"prompt": "{content}"}
        )
        
        # 创建 API 令牌
        default_channels = [channel1.id, channel2.id]
        
        # 设置过期时间为明天
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        expires_at = tomorrow.isoformat()
        
        token = APITokenRepository.create_token(
            name="测试令牌",
            default_channels=default_channels,
            default_ai=ai_channel.id,
            expires_at=expires_at
        )
        
        print(f"创建 API 令牌: {token.id}, 名称: {token.name}, 令牌值: {token.token}")
        
        # 获取 API 令牌
        retrieved_token = APITokenRepository.get_token(token.id)
        print(f"获取 API 令牌: {retrieved_token.id}, 名称: {retrieved_token.name}")
        
        # 通过令牌值获取 API 令牌
        token_by_value = APITokenRepository.get_token_by_token_value(token.token)
        print(f"通过令牌值获取 API 令牌: {token_by_value.id if token_by_value else 'None'}")
        
        # 检查默认渠道
        print(f"默认渠道: {retrieved_token.default_channels_list}")
        print(f"默认 AI: {retrieved_token.default_ai}")
        
        # 更新 API 令牌
        updated_token = APITokenRepository.update_token(
            token_id=token.id,
            name="更新后的测试令牌",
            default_channels=[channel1.id]  # 只保留一个默认渠道
        )
        print(f"更新 API 令牌: {updated_token.id}, 名称: {updated_token.name}, 默认渠道: {updated_token.default_channels_list}")
        
        # 设置默认渠道
        token_with_channels = APITokenRepository.set_token_default_channels(token.id, [channel2.id])
        print(f"设置默认渠道后: {token_with_channels.default_channels_list}")
        
        # 设置默认 AI
        token_with_ai = APITokenRepository.set_token_default_ai(token.id, None)  # 清除默认 AI
        print(f"清除默认 AI 后: {token_with_ai.default_ai}")
        
        # 重新设置默认 AI
        token_with_ai = APITokenRepository.set_token_default_ai(token.id, ai_channel.id)
        print(f"重新设置默认 AI 后: {token_with_ai.default_ai}")
        
        # 禁用 API 令牌
        disabled_token = APITokenRepository.disable_token(token.id)
        print(f"禁用 API 令牌: {disabled_token.id}, 状态: {disabled_token.status}")
        
        # 启用 API 令牌
        enabled_token = APITokenRepository.enable_token(token.id)
        print(f"启用 API 令牌: {enabled_token.id}, 状态: {enabled_token.status}")
        
        # 设置过期时间
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        expired_token = APITokenRepository.set_token_expiry(token.id, yesterday.isoformat())
        print(f"设置过期时间: {expired_token.expires_at}, 是否过期: {expired_token.is_expired()}")
        
        # 重新生成令牌值
        old_token_value = token.token
        regenerated_token = APITokenRepository.regenerate_token_value(token.id)
        print(f"重新生成令牌值: 旧值: {old_token_value}, 新值: {regenerated_token.token}")
        
        # 获取所有 API 令牌
        all_tokens = APITokenRepository.get_all_tokens()
        print(f"所有 API 令牌数量: {len(all_tokens)}")
        
        # 获取有效的 API 令牌
        valid_tokens = APITokenRepository.get_valid_tokens()
        print(f"有效的 API 令牌数量: {len(valid_tokens)}")
        
        # 删除 API 令牌
        result = APITokenRepository.delete_token(token.id)
        print(f"删除 API 令牌: {'成功' if result else '失败'}")
        
        # 验证删除
        deleted_token = APITokenRepository.get_token(token.id)
        print(f"获取已删除 API 令牌: {'不存在' if deleted_token is None else '仍然存在'}")
        
        # 清理测试数据
        ChannelRepository.delete_channel(channel1.id)
        ChannelRepository.delete_channel(channel2.id)
        AIChannelRepository.delete_ai_channel(ai_channel.id)
        
        print("API 令牌模块测试完成")
    except Exception as e:
        print(f"API 令牌模块测试出错: {e}")
        traceback.print_exc()


def main():
    """主测试函数"""
    try:
        # 设置测试环境
        setup()
        
        # 运行测试
        test_system_config()
        test_channel()
        test_ai_channel()
        test_api_token()
        
        print("\n所有测试完成!")
        
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        traceback.print_exc()
    
    finally:
        # 清理测试环境
        teardown()


if __name__ == "__main__":
    main() 