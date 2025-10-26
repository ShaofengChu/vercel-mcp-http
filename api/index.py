# api/index.py
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

# 导入我们在 mcp_server.py 里创建的 ASGI 子应用（/mcp/）
from mcp_server import app as mcp_asgi_app

app = FastAPI(title="Vercel MCP (Streamable HTTP + FastAPI)", lifespan=mcp_asgi_app.lifespan)

# 开放 CORS，便于不同来源的 IDE/客户端连接
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查
@app.get("/")
async def root():
    return {"status": "ok", "service": "vercel-mcp-http", "mcp_endpoint": "/mcp/"}

# **关键**：将 MCP 的 Streamable HTTP 端点挂到 /mcp/
# FastMCP 的 http_app() 自带 /mcp/ 前缀（末尾斜杠），这里直接 mount 到 "/"
# 之后完整路径就是 /mcp/
app.mount("/", mcp_asgi_app)
