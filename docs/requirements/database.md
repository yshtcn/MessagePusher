# MessagePusher 数据库设计文档

本文档描述了 MessagePusher 项目的数据库设计和需求。

## 数据库选择

MessagePusher 项目使用 SQLite 作为主要存储系统，用于存储结构化数据。SQLite 是一个轻量级的文件型数据库，不需要单独的服务器进程，适合个人项目和小型应用。它具有以下优势：

1. 零配置 - 无需安装和配置数据库服务器
2. 单文件存储 - 整个数据库存储在一个文件中，便于备份和迁移
3. 跨平台 - 支持所有主要操作系统
4. 可靠性高 - 支持ACID事务
5. 资源占用少 - 适合在资源有限的环境中运行

对于任务队列和临时数据，我们将使用Python内置的数据结构和SQLite表来实现，而不是依赖外部系统如Redis。

## 数据模型

### 1. 消息渠道表 (channels)

存储消息推送渠道配置。

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | string | 主键，渠道ID |
| name | string | 渠道名称 |
| api_url | string | API接口地址 |
| method | string | 请求方法（GET/POST/PUT等） |
| content_type | string | 内容类型（form/json/xml等） |
| params | json | 参数映射（JSON格式，定义如何将消息字段映射到API参数） |
| headers | json | 请求头（JSON格式，可为null） |
| placeholders | json | 占位符值（JSON格式，如API密钥等） |
| proxy | json | 代理配置（JSON格式，可为null） |
| max_length | integer | 最大消息长度 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |
| status | enum | 渠道状态（启用/禁用） |

### 2. AI渠道表 (ai_channels)

存储AI服务配置。

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | string | 主键，AI渠道ID |
| name | string | AI渠道名称 |
| api_url | string | API接口地址 |
| method | string | 请求方法（通常是POST） |
| model | string | 模型名称 |
| params | json | 模型参数（JSON格式，如temperature、max_tokens等） |
| headers | json | 请求头（JSON格式，如Authorization等） |
| placeholders | json | 占位符值（JSON格式，如API密钥等） |
| prompt | text | 自定义Prompt模板（可为null） |
| proxy | json | 代理配置（JSON格式，可为null） |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |
| status | enum | 渠道状态（启用/禁用） |

### 3. API令牌表 (api_tokens)

存储API访问令牌。

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | string | 主键，令牌ID |
| name | string | 令牌名称 |
| token | string | 访问令牌，唯一 |
| default_channels | json | 默认渠道ID列表（JSON数组） |
| default_ai | string | 默认AI渠道ID（可为null） |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |
| expires_at | timestamp | 过期时间（可为null） |
| status | enum | 令牌状态（启用/禁用） |

### 4. 消息表 (messages)

存储发送的消息。

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | string | 主键，消息ID |
| api_token_id | string | 外键，关联API令牌表 |
| title | string | 消息标题（可为null） |
| content | text | 消息内容（可为null） |
| url | string | 链接地址（可为null） |
| url_content | text | URL内容的摘要或简短描述（可为null） |
| file_storage | string | URL抓取内容的文件存储路径（可为null） |
| view_token | string | 用于查看完整内容的随机令牌，用于构建view_url |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

### 5. 消息渠道关联表 (message_channels)

存储消息与渠道的关联关系和发送状态。

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | string | 主键 |
| message_id | string | 外键，关联消息表 |
| channel_id | string | 外键，关联渠道表 |
| status | enum | 发送状态（等待/发送中/成功/失败） |
| error | text | 错误信息（可为null） |
| sent_at | timestamp | 发送时间（可为null） |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

### 6. 消息AI处理表 (message_ai)

存储消息的AI处理结果。

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | string | 主键 |
| message_id | string | 外键，关联消息表 |
| ai_channel_id | string | 外键，关联AI渠道表 |
| prompt | text | 使用的Prompt |
| result | text | AI处理结果 |
| status | enum | 处理状态（等待/处理中/成功/失败） |
| error | text | 错误信息（可为null） |
| processed_at | timestamp | 处理时间（可为null） |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

### 7. 系统配置表 (system_config)

存储系统全局配置信息。

| 字段名 | 类型 | 描述 |
|--------|------|------|
| key | string | 主键，配置键名 |
| value | text | 配置值 |
| description | string | 配置项描述 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

## 索引设计

为提高查询性能，需要在以下字段上创建索引：

1. channels 表：api_url
2. ai_channels 表：api_url, model
3. api_tokens 表：token
4. messages 表：api_token_id, created_at
5. message_channels 表：message_id, channel_id, status
6. message_ai 表：message_id, ai_channel_id, status

## 关系图

```
channels
  |
  +--- message_channels
        |
        v
messages --- message_ai --- ai_channels
  ^
  |
api_tokens

system_config  (独立表，不与其他表关联)
```

## 渠道配置示例

### Telegram 渠道配置示例

```json
{
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
    "token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID"
  }
}
```

### Bark 渠道配置示例

```json
{
  "api_url": "https://api.day.app/{device_key}/{title}/{content}",
  "method": "GET",
  "content_type": "form",
  "params": {
    "url": "{url}"
  },
  "headers": {},
  "placeholders": {
    "device_key": "YOUR_DEVICE_KEY"
  }
}
```

## AI渠道配置示例

### OpenAI 配置示例

```json
{
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
    "api_key": "YOUR_API_KEY"
  }
}
```

### 文心一言配置示例

```json
{
  "api_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions",
  "method": "POST",
  "model": "ernie-bot-4",
  "params": {
    "temperature": 0.7,
    "top_p": 0.8
  },
  "headers": {
    "Content-Type": "application/json"
  },
  "placeholders": {
    "access_token": "YOUR_ACCESS_TOKEN"
  }
}
```

## 数据库迁移

系统应支持数据库迁移功能，便于版本控制和升级：

1. 使用迁移工具（如 Flyway、Liquibase 或 ORM 自带的迁移工具）
2. 每次架构变更都创建新的迁移脚本
3. 迁移脚本应该是幂等的，可以重复执行
4. 提供回滚机制，以便在出现问题时恢复

## 数据安全

1. 敏感数据（如API密钥）应使用强哈希算法或加密存储
2. 定期备份数据库，并测试恢复流程
3. 实现审计日志，记录关键操作

## 扩展性

1. 设计应考虑未来可能的功能扩展
2. 使用JSON字段存储配置，便于添加新的配置项
3. 状态字段使用枚举类型，便于添加新的状态值
4. 预留足够的字段长度，避免因数据增长导致的溢出 

## 数据库初始化和创建

系统启动时会自动检查数据库是否存在，如果不存在则会执行以下初始化流程：

1. **数据库文件创建**
   - 在配置的路径创建SQLite数据库文件
   - 默认路径为应用根目录下的`data/messagepusher.db`
   - 用户可通过配置文件修改数据库路径

2. **表结构创建**
   - 系统会自动创建上述所有数据表
   - 创建必要的索引以优化查询性能
   - 设置表之间的外键关系

3. **初始数据填充**
   - 初始化系统配置表
     - 设置默认的系统参数
     - 配置默认的消息队列和重试策略
   - 创建默认的消息状态枚举值
   - 创建文件存储目录结构

4. **版本控制表**
   - 创建数据库版本控制表，记录当前数据库架构版本
   - 用于后续数据库迁移和升级

5. **验证步骤**
   - 执行基本查询验证数据库结构是否正确
   - 检查表之间的关系是否正确设置
   - 验证索引是否正确创建

6. **错误处理**
   - 如果数据库创建过程中出现错误，系统会记录详细日志
   - 对于可恢复的错误，系统会尝试自动修复
   - 对于严重错误，系统会提供明确的错误信息并安全退出

数据库初始化过程由中枢模块负责执行，确保在系统其他组件启动前完成数据库准备工作。初始化完成后，系统会在日志中记录数据库创建成功的信息。

## 文件存储

对于URL抓取的内容，系统采用以下存储策略：

1. **文件存储结构**
   - URL抓取的完整内容存储为文件，而不是直接存入数据库
   - 文件存储在配置的目录下，默认为`data/files/{yyyy-mm-dd}/{message_id}.html`
   - 支持按日期分目录存储，便于管理和备份

2. **内容访问机制**
   - 每条消息生成唯一的随机`view_token`，用于构建访问URL
   - 访问URL格式为`/view/{view_token}`，而不是直接使用消息ID
   - 通过随机令牌防止用户通过简单递增ID访问他人消息

3. **存储优化**
   - 对于超大内容，系统会自动进行压缩存储
   - 支持设置文件保留期限，自动清理过期文件
   - 提供文件存储使用统计和空间管理功能 