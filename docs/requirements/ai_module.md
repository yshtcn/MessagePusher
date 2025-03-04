# MessagePusher AI模块需求文档

MessagePusher 项目的AI模块提供智能分析和处理功能，通过集成AI服务，增强消息内容的解读能力。本模块主要支持Ollama和OpenAI API，以便用户可以灵活选择本地部署或云端AI服务。

## 功能需求

### 1. AI服务集成

- 主要支持两种AI服务：
  - **Ollama**：本地部署的开源大语言模型服务，适合私有化部署和无需联网场景
  - **OpenAI API**：云端AI服务，提供强大的语言处理能力
- 次要支持其他AI服务（如有需要可扩展）
- 用户可以配置多个AI渠道，数量不受限制
- 每个AI渠道需要配置API接口地址、认证信息和模型选择
- 支持为每个AI渠道单独配置HTTP/SOCKS5代理

### 2. Prompt管理

- 系统提供全局默认Prompt（在config文件中配置）
- 用户可以为每个AI渠道自定义Prompt
- 为Ollama和OpenAI分别提供优化的默认Prompt模板
- Prompt用于指导AI如何解读和处理消息内容

### 3. 消息处理流程

- 当API请求中指定了AI编号时，系统会调用对应的AI服务
- AI服务会处理消息内容（包括标题、正文和链接抓取的内容）
- AI处理结果会被保存到数据库中
- 处理结果会通过指定的消息渠道发送给用户
- 如果消息内容超过渠道设定的最大长度，系统会提供链接让用户查看完整内容

### 4. API集成

- 用户可以在创建API时指定默认的AI配置
- API调用时可以通过参数指定使用哪个AI渠道进行处理
- 每次API调用只能指定一个AI渠道

## 技术需求

1. **API集成**：
   - 优先支持Ollama API和OpenAI API的调用
   - 处理异步响应和长时间运行的请求
   - 实现请求限流和错误处理机制
   - 支持不同模型的参数配置（如temperature、max_tokens等）

2. **安全性**：
   - 加密存储API密钥和敏感数据
   - 实现访问控制和权限管理
   - 提供数据脱敏和隐私保护功能

3. **性能**：
   - 优化API调用效率和响应时间
   - 实现缓存机制减少重复请求
   - 支持队列处理大量并发请求
   - 对于Ollama，提供本地资源使用限制选项

4. **代理支持**：
   - 支持为每个AI渠道配置独立的HTTP/SOCKS5代理
   - 处理代理连接异常和故障转移

## 用户界面要求

1. **AI渠道配置界面**：
   - 添加和管理AI服务，提供Ollama和OpenAI的快速配置模板
   - 配置API密钥和服务参数
   - 设置代理服务器
   - 配置自定义Prompt
   - 测试连接和验证设置
   - 提供模型选择下拉菜单（对于Ollama显示已安装模型，对于OpenAI显示可用模型）

2. **API管理界面**：
   - 创建和管理API
   - 为API指定默认的AI配置
   - 查看API使用统计

3. **消息查看界面**：
   - 显示消息原文和AI解读结果
   - 提供完整内容的链接访问

## 集成场景示例

### 场景1：使用Ollama本地处理新闻摘要

1. 用户配置Ollama服务（指向本地或局域网Ollama服务器）
2. 用户选择使用的模型（如llama2、mistral等）
3. 用户通过API发送一个新闻文章的URL
4. 系统抓取URL内容并保存到数据库
5. 系统调用Ollama服务，使用配置的Prompt解读文章内容
6. Ollama生成文章摘要、关键点和分析
7. 系统将原始消息和AI解读结果发送到指定的消息渠道

### 场景2：使用OpenAI处理复杂内容分析

1. 用户配置OpenAI服务（设置API密钥和模型选择）
2. 用户通过API发送一个复杂文档的URL
3. 系统抓取URL内容并保存到数据库
4. 系统调用OpenAI服务，使用GPT-4等高级模型分析内容
5. OpenAI生成深度分析和见解
6. 系统将分析结果发送到指定的消息渠道

## 数据流程

1. 用户调用API，指定消息内容和AI编号
2. 系统将消息内容和配置信息写入数据库
3. 如果消息包含URL，系统会抓取URL内容并保存
4. 系统调用指定的AI服务处理消息内容
5. AI处理结果写入数据库
6. 系统通过指定的消息渠道发送处理结果

## 技术实现建议

- AI服务SDK：
  - Ollama Python客户端（使用requests库调用Ollama API）
  - OpenAI Python客户端（官方SDK）
- 代理支持：支持HTTP和SOCKS5代理
- 内容抓取：使用网页抓取库处理URL内容
- 队列系统：使用Python内置队列处理异步AI请求
- 数据库：使用SQLite存储消息内容和AI处理结果 