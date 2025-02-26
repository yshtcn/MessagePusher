"""
MessagePusher 应用程序入口点

该文件是MessagePusher应用程序的入口点，用于启动应用程序。
"""

import os
import logging
from messagepusher import create_app

# 创建应用程序实例
app = create_app()

if __name__ == '__main__':
    # 获取端口配置
    port = int(os.environ.get('PORT', 5000))
    
    # 启动应用程序
    app.logger.info(f"启动MessagePusher应用程序，监听端口: {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
