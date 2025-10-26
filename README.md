# 🧠 vercel-mcp-http — Streamable HTTP MCP Server on Vercel (Python + FastAPI)

> **一站式模板项目**
> 使用 **Python + FastAPI + FastMCP** 构建一个 **Model Context Protocol (MCP)** 远程服务器，
> 支持 **Streamable HTTP** 传输协议，可原生接入 **VS Code** 或 **其他 MCP 客户端**，
> 并可 **一键部署到 Vercel**。

-----

## 📚 项目简介

**MCP（Model Context Protocol）** 是一种用于 AI 模型与外部工具/资源通信的标准协议。
通过 MCP，模型或 IDE（如 VS Code、Cursor、Continue 等）可以动态加载工具、访问资源。

本项目特性：

  - ✅ 使用 **FastMCP (Python SDK)** 实现 MCP 服务器
  - 🚀 部署在 **Vercel**，自动扩缩容、零配置
  - 🔗 采用 **Streamable HTTP** 协议（推荐），完美兼容 VS Code 原生配置
  - 🧩 提供示例工具 `echo`、`add`，以及资源 `status://health`
  - 🧠 可直接在 VS Code 中使用 MCP 工具或资源

-----

## 🏗️ 项目结构

```
vercel-mcp-http/

├── api/
│   └── index.py         # Vercel 入口：FastAPI 应用，挂载 MCP /mcp/
│
├── mcp_server.py        # MCP 逻辑定义：工具、资源、协议端点
│
├── requirements.txt     # 依赖声明
│
├── vercel.json          # 可选：Vercel 函数时长等配置
│
└── README.md            # 本文件
```

-----

## ⚙️ 技术栈与版本要求

| 组件 | 用途 | 推荐版本 |
| :--- | :--- | :--- |
| Python | 运行环境 | $\ge 3.10$ |
| FastAPI | Web 框架 | $\ge 0.110$ |
| FastMCP | MCP Python SDK（支持 HTTP 传输） | $\ge 2.0.0$ |
| Uvicorn | 本地调试服务器 | $\ge 0.29$ |
| Vercel | 云部署平台 | 最新 |

-----

## 🧩 核心文件说明

### `mcp_server.py` — MCP 服务器逻辑

```python
from typing import Any
from datetime import datetime, timezone
from fastmcp import FastMCP

mcp = FastMCP(name="vercel-mcp-http-demo")

# 工具1：回显文本
@mcp.tool
def echo(text: str) -> str:
    """回显一段文本，并附上服务器 UTC 时间"""
    now = datetime.now(timezone.utc).isoformat()
    return f"[server @ {now}] {text}"

# 工具2：两个数相加
@mcp.tool
def add(a: float, b: float) -> float:
    """两个数相加，返回和"""
    return a + b

# 资源1：服务器状态
@mcp.resource("status://health")
def health() -> dict[str, Any]:
    """服务器健康状态，可作为上下文引用"""
    return {"name": "vercel-mcp-http-demo", "ok": True}

# 生成 ASGI 应用（Streamable HTTP）
app = mcp.http_app()
```

### `api/index.py` — FastAPI 主入口（Vercel 识别）

```python
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from mcp_server import app as mcp_asgi_app

app = FastAPI(title="Vercel MCP (Streamable HTTP + FastAPI)")

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "service": "vercel-mcp-http", "mcp_endpoint": "/mcp/"}

# 挂载 MCP HTTP 端点
app.mount("/", mcp_asgi_app)
```

### `requirements.txt`

```
fastapi
uvicorn
fastmcp>=2.0.0
```

### `vercel.json`（可选）

```json
{
  "functions": {
    "api/**": {
      "maxDuration": 60
    }
  }
}
```

-----

## 🚀 本地运行与调试

### 1️⃣ 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2️⃣ 启动开发服务器

```bash
uvicorn api.index:app --reload --port 8000
```

### 3️⃣ 测试端点

**健康检查**
`http://127.0.0.1:8000/`

输出：

```json
{"status":"ok","service":"vercel-mcp-http","mcp_endpoint":"/mcp/"}
```

**MCP HTTP 端点**
`http://127.0.0.1:8000/mcp/`

⚠️ `/mcp/` 是 MCP 客户端连接端点（非人类可读接口）。

```bash
curl -i http://127.0.0.1:8000/mcp/
```
-----

## 🌐 部署到 Vercel

1.  推送项目到 GitHub（例如 `vercel-mcp-http`）。
2.  打开 Vercel Dashboard $\rightarrow$ New Project $\rightarrow$ 选择该仓库。
3.  Vercel 自动识别 FastAPI 并部署。

部署成功后访问：

`https://<your-app>.vercel.app/`

若返回：

```json
{"status":"ok","service":"vercel-mcp-http","mcp_endpoint":"/mcp/"}
```

即表示部署成功。记下 **MCP 端点**：

`https://<your-app>.vercel.app/mcp/`

### 🧠 在 VS Code 中使用 MCP

#### 🔹 VS Code 原生配置 (type: `"http"`)

创建 `.vscode/mcp.json`：

```json
{
  "servers": {
    "vercel-mcp-http": {
      "type": "http",
      "url": "https://<your-app>.vercel.app/mcp/"
    }
  }
}
```

确保 **URL 以 `/mcp/` 结尾**。

VS Code 从 2025 起原生支持 `type: "http"` 的远程 MCP。

#### 🔹 使用方式

打开 VS Code 的 Copilot Chat 或 Continue 插件：

```
#vercel-mcp-http.echo text:"你好 MCP"
#vercel-mcp-http.add a:5 b:7
```

或使用 MCP 面板浏览资源：

`status://health`

-----

## 🧩 MCP 概念速览

| 名称 | 含义 | 示例 |
| :--- | :--- | :--- |
| **Tool** | 工具（函数型调用） | `echo`, `add` |
| **Resource** | 资源（可浏览/读取的数据） | `status://health` |
| **Transport** | 通信协议 | Streamable HTTP |
| **Client** | 消费端（IDE/模型） | VS Code, Continue, Cursor |

-----

## 🔍 调试技巧

| 问题 | 可能原因 | 解决方法 |
| :--- | :--- | :--- |
| VS Code 无法连接 | URL 末尾漏 `/mcp/` | 添加 `/mcp/` |
| 返回 404 | 部署路径错误 | 确认入口文件为 `api/index.py` |
| 请求超时 | 函数时长不足 | 增加 `vercel.json` 中的 `maxDuration` |
| CORS 报错 | 本地跨域限制 | 已默认启用 `allow_origins=["*"]` |
| 工具不显示 | 缓存问题 | 重启 VS Code 或重新加载 MCP |

-----

## 🧪 HTTP 手动测试

使用 `curl` 测试端点：

```bash
curl -i https://<your-app>.vercel.app/mcp/
```

若返回 MCP 协议响应头，则部署成功。

-----

## 📦 扩展开发

添加新工具或资源示例：

```python
@mcp.tool
def multiply(a: float, b: float) -> float:
    """两个数相乘"""
    return a * b

@mcp.resource("info://version")
def version_info() -> dict:
    return {"version": "1.0.0", "author": "YourName"}
```

部署后 VS Code 会自动发现它们。

-----

## 🔐 安全建议

若需身份验证：

1.  使用 Vercel 环境变量 + Header Token 校验；
2.  使用 FastAPI `Depends()` 处理访问控制；
3.  默认启用 HTTPS，无需额外配置。

-----

## 🧾 许可证

MIT License © 2025

可自由修改、使用与分发。

-----

## 📚 参考资料

  * MCP 官方文档（Build Server）
  * MCP 官方文档（Build Client）
  * FastMCP Python SDK 文档
  * Vercel FastAPI 部署指南
  * VS Code MCP Servers 文档

-----

## 💬 致开发者

本项目是一个最小可部署模板，适合：

  * 学习 MCP 协议
  * 为 VS Code / Continue / Cursor 等 IDE 构建远程工具
  * 将 AI 功能服务化并托管在云端

部署一次，即可在 VS Code 中直接调用远程函数、读取资源数据，

让 AI 拥有真正的「访问外部世界」能力 🚀

作者： 你（或团队名）
项目名： `vercel-mcp-http`
部署地址示例： `https://your-app.vercel.app/mcp/`