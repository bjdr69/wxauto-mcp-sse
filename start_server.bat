@echo off
chcp 65001
echo ========================================
echo 微信 MCP SSE 服务器启动脚本
echo WeChat MCP SSE Server Startup Script
echo ========================================
echo.
echo 服务器地址: http://localhost:25008
echo 传输协议: SSE (Server-Sent Events)
echo 协议版本: MCP 2024-11-05
echo.
echo 修复内容:
echo - 标准化 SSE 初始化流程
echo - 简化端点结构 (/sse + /messages)
echo - 标准化 MCP 消息处理
echo - 添加超时和心跳机制
echo ========================================
echo.

cd /d "%~dp0"
python wxauto_mcp_cherry_studio.py --port 25008

echo.
echo 服务器已停止
pause