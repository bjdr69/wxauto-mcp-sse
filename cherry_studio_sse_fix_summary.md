# Cherry Studio SSE 连接问题解决方案

## 问题背景

Cherry Studio 在连接 MCP over SSE 服务器时遇到连接问题，主要表现为：
- SSE 连接建立失败
- 工具调用无响应
- 连接不稳定，频繁断开

## 解决方案

### 1. 标准化 SSE 初始化流程

**问题**: 非标准的 SSE 握手流程导致 Cherry Studio 无法正确建立连接

**解决方案**:
```python
# 标准 MCP SSE 端点实现
@app.get("/sse")
async def sse_endpoint(request: Request):
    # 发送端点URL（符合MCP SSE规范）
    endpoint_url = "/messages"
    yield f"event: endpoint\ndata: {endpoint_url}\n\n"
```

**关键改进**:
- 遵循 MCP SSE 协议规范
- 正确发送 `endpoint` 事件
- 标准化事件流格式

### 2. 简化端点结构

**问题**: 复杂的端点结构和路由导致连接混乱

**解决方案**:
```
/sse      - SSE 连接端点 (GET)
/messages - JSON-RPC 消息端点 (POST)
```

**关键改进**:
- 清晰的职责分离
- 符合 MCP 协议标准
- 简化客户端配置

### 3. 标准化 MCP 消息处理

**问题**: 消息格式不符合 JSON-RPC 2.0 规范

**解决方案**:
```python
# 标准 JSON-RPC 2.0 响应格式
response = {
    "jsonrpc": "2.0",
    "id": msg_id,
    "result": {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}},
        "serverInfo": {
            "name": "wxauto-mcp-standard-sse",
            "version": "1.0.0"
        }
    }
}
```

**关键改进**:
- 严格遵循 JSON-RPC 2.0 规范
- 正确的消息 ID 处理
- 标准化错误响应

### 4. 添加超时和心跳机制

**问题**: 长时间无活动导致连接超时

**解决方案**:
```python
# 心跳机制
try:
    message = await asyncio.wait_for(connection.get_message(), timeout=30.0)
except asyncio.TimeoutError:
    # 发送心跳保持连接
    yield f": heartbeat\n\n"
```

**关键改进**:
- 30秒超时检测
- 自动心跳保持连接
- 防止连接意外断开

## 测试验证

### 1. 连接测试
```bash
# 测试 SSE 连接
curl -N http://localhost:25008/sse
```

**预期输出**:
```
event: endpoint
data: /messages

: heartbeat
```

### 2. 工具调用测试
```powershell
$body = @{
    jsonrpc = "2.0"
    id = 1
    method = "tools/list"
    params = @{}
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:25008/messages" -Method POST -Body $body -ContentType "application/json"
```

### 3. Cherry Studio 集成测试

配置文件 (`mcp_config.json`):
```json
{
  "mcpServers": {
    "wxauto": {
      "transport": {
        "type": "sse",
        "url": "http://localhost:25008/sse"
      }
    }
  }
}
```

## 技术细节

### MCP 协议版本
- **协议版本**: 2024-11-05
- **传输方式**: SSE (Server-Sent Events)
- **消息格式**: JSON-RPC 2.0

### 关键修复点

1. **初始化序列**:
   ```
   Client -> GET /sse
   Server -> event: endpoint\ndata: /messages
   Client -> POST /messages (initialize)
   Server -> JSON-RPC response
   ```

2. **消息流**:
   ```
   Client -> POST /messages (tools/list)
   Server -> SSE event with JSON-RPC response
   Client -> POST /messages (tools/call)
   Server -> SSE event with tool result
   ```

3. **错误处理**:
   ```python
   error_response = {
       "jsonrpc": "2.0",
       "id": message.get("id"),
       "error": {"code": -32603, "message": str(e)}
   }
   ```

## 兼容性

✅ **Cherry Studio** - 完全兼容  
✅ **Trae AI** - 完全兼容  
✅ **标准 MCP 客户端** - 完全兼容  

## 部署说明

1. **启动服务器**:
   ```cmd
   python wxauto_mcp_cherry_studio.py --port 25008
   ```

2. **验证连接**:
   ```cmd
   curl http://localhost:25008/health
   ```

3. **配置客户端**:
   - 使用 SSE 传输类型
   - 端点 URL: `http://localhost:25008/sse`

## 总结

通过标准化 SSE 实现、简化端点结构、规范消息格式和添加稳定性机制，成功解决了 Cherry Studio 的 SSE 连接问题。现在的实现完全符合 MCP 协议规范，具有良好的兼容性和稳定性。