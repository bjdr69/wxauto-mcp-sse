#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信自动化 MCP 服务器 (标准SSE实现)
符合官方MCP SSE协议规范
"""

import asyncio
import json
import logging
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ErrorData,
    INVALID_PARAMS,
    INTERNAL_ERROR
)
from mcp.shared.exceptions import McpError
import uvicorn
from wxauto import WeChat

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] [%(levelname)s] [%(filename)s:%(lineno)d]  %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('wxauto_logs/app_20250715.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 全局微信实例
wx_instance = None

def get_wx_instance():
    """获取微信实例"""
    global wx_instance
    if wx_instance is None:
        try:
            wx_instance = WeChat()
            logger.info("微信实例初始化成功")
        except Exception as e:
            logger.error(f"微信实例初始化失败: {e}")
            raise
    return wx_instance

# MCP 服务器实例
server = Server("wxauto-mcp-cherry-studio")

@server.list_tools()
async def list_tools():
    """列出可用工具"""
    return [
        Tool(
            name="send_message",
            description="发送微信消息",
            inputSchema={
                "type": "object",
                "properties": {
                    "msg": {
                        "type": "string",
                        "description": "要发送的消息内容"
                    },
                    "to": {
                        "type": "string",
                        "description": "接收者名称"
                    },
                    "at": {
                        "anyOf": [
                            {"type": "string"},
                            {"type": "array", "items": {"type": "string"}}
                        ],
                        "description": "要@的人员列表（可选）",
                        "default": None
                    }
                },
                "required": ["msg", "to"]
            },
            outputSchema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"}
                },
                "required": ["success", "message"]
            },
            annotations={
                "title": "发送微信消息",
                "readOnlyHint": False,
                "destructiveHint": False,
                "idempotentHint": False,
                "openWorldHint": False
            }
        ),
        Tool(
            name="get_all_messages",
            description="获取微信消息记录",
            inputSchema={
                "type": "object",
                "properties": {
                    "who": {
                        "type": "string",
                        "description": "联系人或群聊名称"
                    },
                    "load_more": {
                        "type": "boolean",
                        "description": "是否加载更多历史消息",
                        "default": False
                    }
                },
                "required": ["who"]
            },
            outputSchema={
                "type": "object",
                "properties": {
                    "messages": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "count": {"type": "integer"}
                },
                "required": ["messages", "count"]
            },
            annotations={
                 "title": "获取微信消息记录",
                 "readOnlyHint": True,
                 "destructiveHint": False,
                 "idempotentHint": True,
                 "openWorldHint": False
             }
        ),
        Tool(
            name="get_contact_list",
            description="获取微信联系人列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_known": {
                        "type": "boolean",
                        "description": "是否包含已知联系人",
                        "default": True
                    },
                    "known_contacts": {
                        "type": "array",
                        "description": "已知联系人列表",
                        "items": {"type": "string"},
                        "default": ["YINGJIE"]
                    }
                },
                "required": []
            },
            outputSchema={
                "type": "object",
                "properties": {
                    "contacts": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "total": {"type": "integer"}
                },
                "required": ["contacts", "total"]
            },
            annotations={
                 "title": "获取微信联系人列表",
                 "readOnlyHint": True,
                 "destructiveHint": False,
                 "idempotentHint": True,
                 "openWorldHint": False
             }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]):
    """调用工具"""
    logger.info(f"调用工具: {name}, 参数: {arguments}")
    
    if name == "send_message":
        return await send_message(arguments)
    elif name == "get_all_messages":
        return await get_all_messages(arguments)
    elif name == "get_contact_list":
        return await get_contact_list(arguments)
    else:
        raise McpError(ErrorData(code=INVALID_PARAMS, message=f"未知工具: {name}"))

async def send_message(arguments: Dict[str, Any]):
    """发送微信消息"""
    try:
        wx = get_wx_instance()
        msg = arguments.get("msg")
        to = arguments.get("to")
        at = arguments.get("at")
        
        if not msg or not to:
            raise ValueError("消息内容和接收者不能为空")
        
        logger.info(f"发送消息给 {to}: {msg}")
        
        # 发送消息
        if at:
            if isinstance(at, str):
                at = [at]
            wx.SendMsg(msg, to, at)
        else:
            wx.SendMsg(msg, to)
        
        return {
            "success": True,
            "message": "Message sent successfully"
        }
    except Exception as e:
        logger.error(f"发送消息失败: {e}")
        return {
            "success": False,
            "message": f"发送消息失败: {str(e)}"
        }

async def get_all_messages(arguments: Dict[str, Any]):
    """获取微信消息记录"""
    try:
        wx = get_wx_instance()
        who = arguments.get("who")
        load_more = arguments.get("load_more", False)
        
        if not who:
            raise ValueError("联系人名称不能为空")
        
        logger.info(f"获取 {who} 的消息记录")
        
        # 先切换到指定联系人的聊天窗口
        wx.ChatWith(who)
        
        # 获取消息
        if load_more:
            wx.LoadMoreMessage()
        
        messages = wx.GetAllMessage()  # 不传参数
        
        # 格式化消息
        formatted_messages = []
        for msg in messages:
            if hasattr(msg, 'sender') and hasattr(msg, 'content'):
                formatted_messages.append(f"{msg.sender}: {msg.content}")
            elif isinstance(msg, dict):
                formatted_messages.append(f"{msg.get('sender', 'Unknown')}: {msg.get('content', '')}")
            else:
                formatted_messages.append(str(msg))
        
        if not formatted_messages:
            formatted_messages = [f"未找到与 {who} 的聊天记录"]
        else:
            formatted_messages = formatted_messages[-20:]  # 只返回最近20条消息
        
        # 返回结构化数据以匹配 outputSchema
        return {
            "messages": formatted_messages,
            "count": len(formatted_messages)
        }
    except Exception as e:
        logger.error(f"获取消息失败: {e}")
        return {
            "messages": [f"获取消息失败: {str(e)}"],
            "count": 1
        }

async def get_contact_list(arguments: Dict[str, Any]):
    """获取微信联系人列表"""
    try:
        wx = get_wx_instance()
        include_known = arguments.get("include_known", True)
        known_contacts = arguments.get("known_contacts", ["YINGJIE"])
        
        logger.info("获取联系人列表")
        
        contact_list = []
        
        # 添加已知联系人
        if include_known:
            contact_list.extend(known_contacts)
        
        # 获取会话列表作为联系人列表
        try:
            wx.SwitchToChat()
            sessions = wx.GetSession()
            for session in sessions:
                if session.name and session.name not in contact_list:
                    # 过滤掉系统会话
                    if session.name not in ['折叠的群聊', '微信支付', '腾讯新闻', '微信运动', '朋友圈']:
                        contact_list.append(session.name)
        except Exception as e:
            logger.warning(f"获取会话列表失败: {e}")
        
        # 添加基础联系人
        basic_contacts = ["文件传输助手", "微信团队"]
        for contact in basic_contacts:
            if contact not in contact_list:
                contact_list.append(contact)
        
        if not contact_list:
            contact_list = ["未找到联系人"]
        
        # 返回结构化数据以匹配 outputSchema
        return {
            "contacts": contact_list,
            "total": len(contact_list)
        }
    except Exception as e:
        logger.error(f"获取联系人列表失败: {e}")
        return {
            "contacts": [f"获取联系人列表失败: {str(e)}"],
            "total": 1
        }

# SSE连接管理
class SSEConnection:
    def __init__(self, connection_id: str):
        self.connection_id = connection_id
        self.queue = asyncio.Queue()
        self.initialized = False
        self.client_info = None
        
    async def send_message(self, message: dict):
        await self.queue.put(message)
        
    async def get_message(self):
        return await self.queue.get()
    
    def set_init_client(self, init_client_data):
        """设置 initClient 数据"""
        self.init_client = init_client_data
        logger.info(f"设置 initClient: {init_client_data}")

# 全局连接管理
connections = {}

async def handle_mcp_message(connection: SSEConnection, message: dict):
    """处理MCP消息 - 符合标准MCP协议"""
    try:
        method = message.get("method")
        params = message.get("params", {})
        msg_id = message.get("id")
        
        logger.info(f"处理MCP请求: {method}, ID: {msg_id}")
        
        if method == "initialize":
            # 标准MCP初始化
            connection.client_info = params.get("clientInfo", {})
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "wxauto-mcp-standard-sse",
                        "version": "1.0.0"
                    }
                }
            }
            connection.initialized = True
            await connection.send_message(response)
            logger.info(f"MCP初始化成功，客户端: {connection.client_info}")
            
        elif method == "notifications/initialized":
            # 初始化完成通知
            logger.info("收到初始化完成通知")
            
        elif method == "tools/list":
            if not connection.initialized:
                raise Exception("连接未初始化")
                
            tools = await list_tools()
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": [tool.model_dump() for tool in tools]}
            }
            await connection.send_message(response)
            logger.info(f"返回工具列表: {len(tools)} 个工具")
            
        elif method == "tools/call":
            if not connection.initialized:
                raise Exception("连接未初始化")
                
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            logger.info(f"调用工具: {tool_name}, 参数: {arguments}")
            
            result = await call_tool(tool_name, arguments)
            
            # 处理结果：MCP 协议要求结果包含 content 字段
            if isinstance(result, dict):
                # 工具返回结构化数据，包装为 TextContent
                from mcp.types import TextContent
                import json
                content = TextContent(
                    type="text",
                    text=json.dumps(result, ensure_ascii=False, indent=2)
                )
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [content.model_dump()]}
                }
            else:
                # 工具返回TextContent列表
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [content.model_dump() for content in result]}
                }
            await connection.send_message(response)
            logger.info(f"工具调用成功")
            
        elif method == "ping":
            # 处理 ping 请求，用于检查服务器是否响应
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {}
            }
            await connection.send_message(response)
            logger.info(f"响应 ping 请求")
            
        else:
            error_response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"未知方法: {method}"}
            }
            await connection.send_message(error_response)
            logger.warning(f"未知方法: {method}")
            
    except Exception as e:
        logger.error(f"处理MCP消息失败: {e}", exc_info=True)
        error_response = {
            "jsonrpc": "2.0",
            "id": message.get("id") if message else None,
            "error": {"code": -32603, "message": str(e)}
        }
        await connection.send_message(error_response)

# FastAPI 应用
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化微信
    logger.info("正在初始化微信实例...")
    get_wx_instance()
    yield
    # 关闭时清理资源
    logger.info("正在清理资源...")

app = FastAPI(
    title="WeChat MCP Standard SSE Server",
    description="微信自动化 MCP 服务器 (标准SSE实现)",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/sse")
async def sse_endpoint(request: Request):
    """标准MCP SSE端点"""
    connection_id = str(uuid.uuid4())
    connection = SSEConnection(connection_id)
    connections[connection_id] = connection
    
    logger.info(f"新的SSE连接: {connection_id}")
    
    async def event_stream():
        try:
            # 发送端点URL（标准MCP SSE协议）
            # 根据MCP SSE规范，endpoint事件的数据应该是消息端点的URL
            endpoint_url = "/messages"
            yield f"event: endpoint\ndata: {endpoint_url}\n\n"
            logger.info(f"发送端点信息: {endpoint_url}")
            
            # 处理消息循环
            while True:
                try:
                    # 等待消息（带超时）
                    message = await asyncio.wait_for(connection.get_message(), timeout=30.0)
                    
                    # 发送JSON-RPC消息
                    message_json = json.dumps(message, ensure_ascii=False)
                    yield f"data: {message_json}\n\n"
                    
                except asyncio.TimeoutError:
                    # 发送心跳保持连接
                    yield f": heartbeat\n\n"
                except Exception as e:
                    logger.error(f"消息处理错误: {e}")
                    break
                    
        except asyncio.CancelledError:
            logger.info(f"SSE连接断开: {connection_id}")
        except Exception as e:
            logger.error(f"SSE流错误: {e}")
        finally:
            # 清理连接
            if connection_id in connections:
                del connections[connection_id]
                logger.info(f"清理SSE连接: {connection_id}")
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "X-Accel-Buffering": "no",
        }
    )

@app.post("/messages")
async def messages_endpoint(request: Request):
    """标准MCP消息端点"""
    try:
        body = await request.body()
        message_data = json.loads(body.decode('utf-8'))
        
        logger.info(f"收到MCP消息: {message_data}")
        
        # 找到活跃的连接
        if not connections:
            logger.error("没有活跃的SSE连接")
            raise HTTPException(status_code=400, detail="没有活跃的SSE连接")
        
        # 使用最新的连接
        connection_id = list(connections.keys())[-1]
        connection = connections[connection_id]
        
        # 异步处理MCP消息
        asyncio.create_task(handle_mcp_message(connection, message_data))
        
        # 立即返回HTTP 200
        return {"status": "ok"}
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析失败: {e}")
        raise HTTPException(status_code=400, detail="无效的JSON格式")
    except Exception as e:
        logger.error(f"处理MCP消息失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/health")
async def health_check():
    """健康检查端点"""
    try:
        # 检查微信实例
        wx = get_wx_instance()
        return {
            "status": "healthy",
            "connections": len(connections),
            "wechat": "connected",
            "initClient": "available"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "connections": len(connections),
            "initClient": "available"
        }

@app.get("/")
async def read_root():
    """根路径"""
    return {
        "message": "WeChat MCP Server (Standard SSE)",
        "protocol": "MCP over SSE",
        "version": "2024-11-05",
        "endpoints": {
            "sse": "/sse (GET for SSE stream)",
            "messages": "/messages (POST for JSON-RPC messages)"
        },
        "connections": len(connections)
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="WeChat MCP Cherry Studio Server")
    parser.add_argument("--host", default="0.0.0.0", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=25007, help="服务器端口")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info(f"启动 WeChat MCP Standard SSE 服务器: http://{args.host}:{args.port}")
    logger.info(f"SSE 端点: http://{args.host}:{args.port}/sse")
    logger.info(f"消息端点: http://{args.host}:{args.port}/messages")
    
    uvicorn.run(
        "wxauto_mcp_cherry_studio:app",
        host=args.host,
        port=args.port,
        reload=False,  # 禁用自动重载以避免连接问题
        log_level="debug" if args.debug else "info"
    )