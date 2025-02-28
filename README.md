# MessagePusher

MessagePusher 是一个统一的消息推送服务，支持多种消息渠道和平台。

## 系统特点

- **单用户系统**：设计为个人使用的单用户系统，无需用户注册和登录
- **多渠道支持**：支持Telegram、Bark、PushDeer等多种消息推送渠道
- **AI增强**：集成AI服务，提供消息内容分析和处理
- **简单易用**：简洁的Web界面和API，易于配置和使用
- **轻量部署**：基于Docker的轻量级部署，适合个人服务器

## 技术栈

- **编程语言**：Python
- **数据库**：SQLite
- **Web框架**：Flask/FastAPI
- **前端**：简单的HTML/CSS/JavaScript
- **部署**：Docker
- **任务调度**：APScheduler

## 项目文档

- [项目需求文档](docs/requirements/README.md)
- [系统流程文档](docs/requirements/system_flow.md)
- [API 设计文档](docs/requirements/api.md)
- [消息渠道需求](docs/requirements/channels.md)
- [数据库设计](docs/requirements/database.md)
- [HTTP管理模块](docs/requirements/http_management.md)
- [AI模块](docs/requirements/ai_module.md)
- [中枢模块](docs/requirements/core_module.md)
- [项目进度报告](docs/progress_report.md)

## 开发进度

项目当前处于开发阶段，已完成以下模块：

- ✅ **数据库模块**：完成数据库初始化和基本的增删查改操作
- ✅ **核心模块**：完成任务队列、任务调度器、消息处理器、错误处理器的实现
- ✅ **API模块**：已完成，所有功能已实现并通过测试
- 📝 **HTTP管理模块**：计划中
- 📝 **AI模块**：计划中

详细进度请查看[项目进度报告](docs/progress_report.md)。

## 测试状态

- ✅ 数据库模块测试：全部通过
- ✅ 核心模块测试：全部通过
- ✅ API模块测试：全部通过
- ✅ API集成测试：全部通过

## 贡献

欢迎提交Issue和Pull Request。

## 许可证

本项目采用MIT许可证。