"""
测试配置

包含测试所需的配置项。
"""

# 测试数据库配置
TEST_DB_CONFIG = {
    "db_path": ":memory:"  # 使用内存数据库进行测试
}

# 任务队列配置
TEST_TASK_QUEUE_CONFIG = {
    "max_workers": 2,
    "worker_idle_timeout": 0.1,
    "max_retries": 2,
    "retry_delay": 0.1
}

# 任务调度器配置
TEST_TASK_SCHEDULER_CONFIG = {
    "cleanup_interval": 1,
    "retry_interval": 1,
    "stats_interval": 1,
    "max_task_age": 3600
}

# 消息处理器配置
TEST_MESSAGE_PROCESSOR_CONFIG = {
    "url_fetch_timeout": 5,
    "max_content_length": 1024,
    "max_retries": 2,
    "retry_delay": 1
}

# 错误处理器配置
TEST_ERROR_HANDLER_CONFIG = {
    "max_error_history": 100,
    "cleanup_interval": 1,
    "notification_threshold": {
        "low": 10,
        "medium": 5,
        "high": 1,
        "critical": 1
    }
}

# 测试消息渠道配置
TEST_CHANNEL_CONFIG = {
    "telegram": {
        "api_url": "https://api.telegram.org/bot{token}/sendMessage",
        "method": "POST",
        "content_type": "json",
        "params": {
            "chat_id": "{chat_id}",
            "text": "{content}",
            "parse_mode": "HTML"
        },
        "headers": {},
        "placeholders": {
            "token": "test_token",
            "chat_id": "test_chat_id"
        }
    }
}

# 测试AI渠道配置
TEST_AI_CHANNEL_CONFIG = {
    "openai": {
        "api_url": "https://api.openai.com/v1/chat/completions",
        "method": "POST",
        "model": "gpt-3.5-turbo",
        "params": {
            "temperature": 0.7,
            "max_tokens": 1000
        },
        "headers": {
            "Authorization": "Bearer {api_key}"
        },
        "placeholders": {
            "api_key": "test_api_key"
        }
    }
}

# 测试API令牌
TEST_API_TOKEN = {
    "id": "test_token",
    "name": "测试令牌",
    "token": "test_token_string",
    "default_channels": ["telegram"],
    "default_ai": "openai"
}

# 测试消息数据
TEST_MESSAGE_DATA = {
    "title": "测试标题",
    "content": "测试内容",
    "url": "https://example.com/test"
} 