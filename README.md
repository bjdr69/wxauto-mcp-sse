# 微信自动化 MCP 服务器

## 项目简介

这是一个基于 MCP (Model Context Protocol) 的微信自动化工具服务器，支持通过 SSE (Server-Sent Events) 协议与 AI 客户端（如 Cherry Studio、Trae AI）进行通信，提供微信消息发送、获取聊天记录、获取联系人列表等功能。

**致谢**: 本项目基于 [barantt/wxauto-mcp](https://github.com/barantt/wxauto-mcp) 进行 SSE 协议适配和功能增强，感谢原作者的优秀工作！

## 功能特性

- 🚀 **发送微信消息**: 支持向个人或群聊发送文本消息，支持 @ 功能
- 📖 **获取聊天记录**: 获取指定联系人或群聊的消息历史
- 👥 **获取联系人列表**: 获取微信联系人和群聊列表
- 🔌 **MCP 协议支持**: 完全兼容 MCP 标准协议
- 🌐 **SSE 连接**: 基于 Server-Sent Events 的实时通信
- 🎯 **多客户端兼容**: 支持 Cherry Studio、Trae AI 等 MCP 客户端

## 项目结构

```
wxauto-mcp/
├── wxauto_mcp_cherry_studio.py    # 主服务器文件（SSE 协议）
├── wxauto_mcp.py                  # 标准 MCP 服务器（stdio 协议）
├── mcp_config.json                # MCP 客户端配置文件
├── requirements.txt               # Python 依赖
├── start_server.bat              # Windows 启动脚本
├── cherry_studio_sse_fix_summary.md  # Cherry Studio 兼容性修复说明
├── cherry_studio_troubleshooting.md  # 故障排除指南
├── 微信MCP工具使用说明.md         # 详细使用说明
├── 快速参考.md                   # 快速参考指南
└── wxauto_env/                    # Python 虚拟环境
```

## 快速开始

### 1. 环境准备

确保已安装 Python 3.8+ 和微信 PC 版客户端。

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动服务器

#### 方式一：使用批处理文件（推荐）
```bash
start_server.bat
```

#### 方式二：手动启动
```bash
python wxauto_mcp_cherry_studio.py --port 25008
```

### 4. 配置客户端

#### Cherry Studio 配置

在 Cherry Studio 的 MCP 服务器配置中添加：

```json
{
  "mcpServers": {
    "wxauto": {
      "url": "http://localhost:25008/sse",
      "type": "sse"
    }
  }
}
```

#### Trae AI 配置

在 Trae AI 的设置中添加 MCP 服务器：
- 服务器类型：SSE
- URL：`http://localhost:25008/sse`
- 名称：wxauto

## 可用工具

### 1. send_message - 发送微信消息

**功能**: 向指定联系人或群聊发送消息

**参数**:
- `msg` (string): 要发送的消息内容
- `to` (string): 接收者名称（联系人昵称或群聊名称）
- `at` (string|array, 可选): 要@的人员列表（仅群聊有效）

**示例**:
```json
{
  "msg": "你好，这是一条测试消息",
  "to": "张三"
}
```

### 2. get_all_messages - 获取聊天记录

**功能**: 获取指定联系人或群聊的消息历史

**参数**:
- `who` (string): 联系人或群聊名称
- `load_more` (boolean, 可选): 是否加载更多历史消息，默认 false

**示例**:
```json
{
  "who": "张三",
  "load_more": true
}
```

### 3. get_contact_list - 获取联系人列表

**功能**: 获取微信联系人和群聊列表

**参数**:
- `include_known` (boolean, 可选): 是否包含已知联系人，默认 true
- `known_contacts` (array, 可选): 已知联系人列表

**示例**:
```json
{
  "include_known": true,
  "known_contacts": ["张三", "李四"]
}
```

## 技术特性

### MCP 协议兼容性

- ✅ 完整的 MCP 1.0 协议支持
- ✅ 标准的 initialize/initialized 握手流程
- ✅ tools/list 工具列表获取
- ✅ tools/call 工具调用
- ✅ ping/pong 心跳检测
- ✅ 完整的 outputSchema 和 annotations 定义

### SSE 协议特性

- 🔄 实时双向通信
- 📡 自动重连机制
- 🎯 事件驱动架构
- 🔒 CORS 跨域支持

## 故障排除

### 常见问题

1. **微信未启动或未登录**
   - 确保微信 PC 版已启动并登录
   - 检查微信窗口是否可见

2. **端口被占用**
   - 修改启动端口：`python wxauto_mcp_cherry_studio.py --port 25009`
   - 更新客户端配置中的端口号

3. **客户端连接失败**
   - 检查防火墙设置
   - 确认服务器正在运行
   - 验证客户端配置的 URL 格式

### 调试模式

启动服务器时添加调试参数：
```bash
python wxauto_mcp_cherry_studio.py --port 25008 --debug
```

## 更新日志

### v1.0.0 (2024-01-15)
- ✅ 初始版本发布
- ✅ 支持基本的微信自动化功能
- ✅ MCP 协议完整实现
- ✅ Cherry Studio 和 Trae AI 兼容性
- ✅ SSE 协议支持
- ✅ 完整的工具定义和验证

## 致谢与归属

本项目基于 [barantt/wxauto-mcp](https://github.com/barantt/wxauto-mcp) 进行开发，主要贡献包括：

- **原项目**: [barantt/wxauto-mcp](https://github.com/barantt/wxauto-mcp) - 提供了基础的微信自动化 MCP 实现
- **本项目增强**: 添加了 SSE 协议支持，优化了与 Cherry Studio 和 Trae AI 的兼容性

感谢原作者 [@barantt](https://github.com/barantt) 的优秀工作，为微信自动化和 MCP 协议的结合提供了坚实的基础。

## 许可证

MIT License

本项目遵循原项目的开源许可证，继续以 MIT 许可证发布。

## 贡献

欢迎提交 Issue 和 Pull Request！如果您对原始的 wxauto-mcp 功能有改进建议，也请考虑向原项目 [barantt/wxauto-mcp](https://github.com/barantt/wxauto-mcp) 贡献。

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系。