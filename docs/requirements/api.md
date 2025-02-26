# MessagePusher API 需求文档

本文档描述了 MessagePusher 项目的 API 设计和需求。

## API 概述

MessagePusher API 是一组简单的 HTTP 接口，主要用于发送消息到各种渠道。API 设计遵循 RESTful 原则，提供简单直观的接口，专注于消息推送功能。

API 将使用 Python 的 Flask 框架实现，这是一个简单灵活的框架，非常适合构建轻量级的 RESTful API。

## API 端点

### 1. 消息推送 API

#### 1.1 发送消息

```
POST /api/v1/push
```

**请求参数：**

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| token | string | 是 | API 访问令牌 |
| title | string | 否* | 消息标题 |
| content | string | 否* | 消息正文 |
| url | string | 否* | 链接地址 |
| channels | string | 否 | 渠道编号，多个用竖线分隔，如 "1\|2\|3" |
| ai | string | 否 | AI 渠道编号 |

*注：title、content、url 至少需要提供一个

**响应：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "message_id": "12345678",
    "channels": ["1", "2"],
    "ai": "1",
    "view_url": "https://example.com/view/12345678"
  }
}
```

#### 1.2 查询消息状态

```
GET /api/v1/message/{message_id}
```

**请求参数：**

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| token | string | 是 | API 访问令牌 |

**响应：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "message_id": "12345678",
    "title": "消息标题",
    "content": "消息内容...",
    "url": "https://example.com/article",
    "channels": [
      {
        "id": "1",
        "name": "Telegram",
        "status": "sent",
        "sent_at": "2023-01-01T12:00:00Z"
      },
      {
        "id": "2",
        "name": "Bark",
        "status": "failed",
        "error": "连接超时"
      }
    ],
    "ai": {
      "id": "1",
      "name": "OpenAI",
      "status": "processed",
      "result": "AI 处理结果摘要..."
    },
    "created_at": "2023-01-01T11:59:00Z",
    "view_url": "https://example.com/view/12345678"
  }
}
```

## 错误码

| 错误码 | 描述 |
|--------|------|
| 0 | 成功 |
| 1001 | 无效的 API 令牌 |
| 1002 | 参数错误 |
| 1003 | 渠道不存在 |
| 1004 | AI 渠道不存在 |
| 1005 | 消息发送失败 |
| 1006 | 消息不存在 |

## 安全性考虑

1. **认证**：所有 API 请求都需要提供有效的 API 令牌
2. **HTTPS**：所有 API 通信都应使用 HTTPS 加密
3. **速率限制**：实施 API 调用速率限制，防止滥用
4. **日志记录**：记录所有 API 调用，便于审计和故障排查

## 实现注意事项

1. **简单性**：API 设计应尽可能简单，易于使用
2. **可靠性**：确保消息发送的可靠性，实现重试机制
3. **异步处理**：消息发送和 AI 处理应异步进行，不阻塞 API 响应
4. **错误处理**：提供清晰的错误信息和状态码 