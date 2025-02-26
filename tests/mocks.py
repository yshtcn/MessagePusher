"""
测试用Mock类

提供测试所需的各种Mock对象。
"""

class MockMessageChannelRepository:
    """消息渠道仓库的Mock实现"""
    
    def __init__(self):
        self.channels = {}
    
    def get_channel(self, channel_id):
        return self.channels.get(channel_id)
    
    def get_all_channels(self):
        return list(self.channels.values())
    
    def add_channel(self, channel):
        self.channels[channel["id"]] = channel
    
    def update_channel(self, channel):
        if channel["id"] in self.channels:
            self.channels[channel["id"]] = channel
            return True
        return False
    
    def delete_channel(self, channel_id):
        if channel_id in self.channels:
            del self.channels[channel_id]
            return True
        return False

class MockChannelRepository:
    """渠道仓库的Mock实现"""
    
    def __init__(self):
        self.channels = {}
    
    def get_channel(self, channel_id):
        return self.channels.get(channel_id)
    
    def get_all_channels(self):
        return list(self.channels.values())

class MockAIChannelRepository:
    """AI渠道仓库的Mock实现"""
    
    def __init__(self):
        self.channels = {}
    
    def get_channel(self, channel_id):
        return self.channels.get(channel_id)
    
    def get_all_channels(self):
        return list(self.channels.values())

class MockAPITokenRepository:
    """API令牌仓库的Mock实现"""
    
    def __init__(self):
        self.tokens = {}
    
    def get_token(self, token_id):
        return self.tokens.get(token_id)
    
    def get_all_tokens(self):
        return list(self.tokens.values())

class MockMessageRepository:
    """消息仓库的Mock实现"""
    
    def __init__(self):
        self.messages = {}
    
    def get_message(self, message_id):
        return self.messages.get(message_id)
    
    def get_all_messages(self):
        return list(self.messages.values())
    
    def add_message(self, message):
        self.messages[message["id"]] = message
        return True

class MockSystemConfigRepository:
    """系统配置仓库的Mock实现"""
    
    def __init__(self):
        self.configs = {}
    
    def get_config(self, key):
        return self.configs.get(key)
    
    def set_config(self, key, value):
        self.configs[key] = value
        return True

class MockMessageAIRepository:
    """消息AI仓库的Mock实现"""
    
    def __init__(self):
        self.results = {}
        self.history = {}
    
    def get_ai_result(self, message_id):
        return self.results.get(message_id)
    
    def save_ai_result(self, message_id, result):
        self.results[message_id] = result
        if message_id not in self.history:
            self.history[message_id] = []
        self.history[message_id].append(result)
        return True
    
    def get_ai_history(self, message_id):
        return self.history.get(message_id, [])
    
    def delete_ai_result(self, message_id):
        if message_id in self.results:
            del self.results[message_id]
            return True
        return False

class MockDatabase:
    """数据库的Mock实现"""
    
    def __init__(self):
        self.message_channel_repository = MockMessageChannelRepository()
        self.channel_repository = MockChannelRepository()
        self.ai_channel_repository = MockAIChannelRepository()
        self.api_token_repository = MockAPITokenRepository()
        self.message_repository = MockMessageRepository()
        self.system_config_repository = MockSystemConfigRepository()
        self.message_ai_repository = MockMessageAIRepository() 