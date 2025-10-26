# mcp_server.py
from typing import Any
from datetime import datetime, timezone

from fastmcp import FastMCP

# 给你的服务器起个名字（将显示在客户端）
mcp = FastMCP(name="vercel-mcp-http-demo")

# ---- 工具（Tools） ---------------------------------------------------------
@mcp.tool
def echo(text: str) -> str:
    """回显一段文本，并附上服务器 UTC 时间。"""
    now = datetime.now(timezone.utc).isoformat()
    return f"[server @ {now}] {text}"

@mcp.tool
def add(a: float, b: float) -> float:
    """两个数相加，返回和。"""
    return a + b

# ---- 资源（Resources） -----------------------------------------------------
# FastMCP v2 中，资源用 URI 标识符暴露，客户端可浏览/读取
@mcp.resource("status://health")
def health() -> dict[str, Any]:
    """返回服务器健康信息（可作为上下文注入到对话）"""
    return {
        "name": "vercel-mcp-http-demo",
        "ok": True,
    }

# ---- ASGI 应用（Streamable HTTP） ------------------------------------------
# 将 MCP Server 暴露为 ASGI 应用，端点前缀为 /mcp/ （注意末尾斜杠）
# 该子应用会处理 Streamable HTTP 全双工消息
app = mcp.http_app()
