# 微信MCP工具使用说明

## MCP over SSE 协议修复状态

✅ **已修复** - Cherry Studio SSE 连接问题已完全解决

### 服务器信息
- **服务器地址**: http://localhost:25008
- **SSE端点**: http://localhost:25008/sse
- **消息端点**: http://localhost:25008/messages
- **协议版本**: MCP 2024-11-05
- **传输协议**: SSE (Server-Sent Events)

### 修复内容

#### 1. SSE 协议实现
- ✅ 标准化 SSE 初始化流程
- ✅ 符合 MCP SSE 规范的端点结构
- ✅ 正确的事件流格式
- ✅ 标准 JSON-RPC 2.0 消息处理

#### 2. 工具修复
- ✅ `send_message` - 发送微信消息
- ✅ `get_all_messages` - 获取聊天记录
- ✅ `get_contact_list` - 获取联系人列表
- ✅ 所有工具返回标准 MCP 格式

#### 3. 连接稳定性
- ✅ 添加心跳机制防止连接超时
- ✅ 异步消息处理
- ✅ 连接状态管理
- ✅ 错误处理和恢复

#### 4. 协议兼容性
- ✅ Cherry Studio 完全兼容
- ✅ Trae AI 完全兼容
- ✅ 标准 MCP 客户端兼容

### 测试验证

所有功能已通过以下测试：

1. **连接测试**
   ```powershell
   # 测试 SSE 连接
   curl -N http://localhost:25008/sse
   ```

2. **工具调用测试**
   ```powershell
   # 测试获取联系人
   $body = @{
       jsonrpc = "2.0"
       id = 1
       method = "tools/call"
       params = @{
           name = "get_contact_list"
           arguments = @{}
       }
   } | ConvertTo-Json -Depth 3
   
   Invoke-RestMethod -Uri "http://localhost:25008/messages" -Method POST -Body $body -ContentType "application/json"
   ```

3. **消息发送测试**
   ```powershell
   # 测试发送消息
   $body = @{
       jsonrpc = "2.0"
       id = 2
       method = "tools/call"
       params = @{
           name = "send_message"
           arguments = @{
               msg = "测试消息"
               to = "文件传输助手"
           }
       }
   } | ConvertTo-Json -Depth 3
   
   Invoke-RestMethod -Uri "http://localhost:25008/messages" -Method POST -Body $body -ContentType "application/json"
   ```

### 配置更新

请确保 Cherry Studio 配置文件包含以下设置：

```json
{
  "mcpServers": {
    "wxauto": {
      "command": "python",
      "args": ["wxauto_mcp_cherry_studio.py", "--port", "25008"],
      "transport": {
        "type": "sse",
        "url": "http://localhost:25008/sse"
      }
    }
  }
}
```

### 启动服务器

1. **使用批处理脚本**（推荐）：
   ```cmd
   start_server.bat
   ```

2. **直接运行**：
   ```cmd
   python wxauto_mcp_cherry_studio.py --port 25008
   ```

### 故障排除

如果遇到连接问题：

1. 检查服务器是否正常启动
2. 确认端口 25008 未被占用
3. 检查防火墙设置
4. 查看服务器日志输出

### 技术支持

如有问题，请检查：
- 服务器日志文件：`wxauto_logs/app_20250715.log`
- 健康检查端点：http://localhost:25008/health
- 服务器状态：http://localhost:25008/

---

**状态**: ✅ 完全可用  
**最后更新**: 2025-07-15  
**协议版本**: MCP 2024-11-05