# Anki MCP Server

[English Version](./README.md)

Anki MCP Server 是一个基于 FastMCP 的服务器，旨在通过 Anki-Connect 插件为 Anki 提供一个模型上下文协议（MCP）接口。这使得外部应用程序能够以结构化的方式与 Anki 进行交互，从而实现对卡片、牌组、笔记和模板的程序化管理。

## 🌟 功能

  * **全面的 Anki 操作**: 提供了一整套工具，用于管理 Anki 中的几乎所有方面，包括：
      * **卡片管理**: 添加、删除、暂停/取消暂停、查找卡片，以及获取/设置简易度因子。
      * **牌组管理**: 创建、删除、重命名牌组，并将卡片移动到不同牌组。
      * **笔记管理**: 创建、删除、更新笔记内容和标签。
      * **模板 (Note Type) 管理**: 创建、删除、修改模板和字段。
  * **异步架构**: 基于 `asyncio` 和 `httpx` 构建，可实现高效、非阻塞的 I/O 操作，从而能够同时处理多个请求。
  * **配置灵活**: 通过环境变量或 `.env` 文件轻松配置 Anki-Connect 的 URL、API 密钥和服务器日志级别。
  * **结构化数据模型**: 使用 pydantic 模型来定义所有 Anki-Connect API 的请求和响应，确保了类型安全和数据一致性。
  * **清晰的工具定义**: 每个 Anki-Connect 操作都封装在一个带有明确名称、描述和类型注解的 MCP 工具中。


## 🚀 快速开始

### **先决条件**

  * Python 3.8+
  * Anki 桌面应用程序
  * 已安装并启用的 [Anki-Connect](https://ankiweb.net/shared/info/2055492159) 插件

### **安装**

1.  **克隆仓库:**

    ```bash
    git clone https://github.com/ruiqurm/anki-mcp-server.git
    cd anki-mcp-server
    ```

2.  **安装依赖:**

    ```bash
    pip install -r requirements.txt
    ```

### **运行服务器**

您可以通过 `run_server.py` 脚本或直接作为 Python 模块来启动服务器：

**通过脚本:**

```bash
python run_server.py
```

**作为模块:**

```bash
python -m src.anki_mcp_server
```

服务器启动后，将连接到在 `http://localhost:8765` 上运行的 Anki-Connect。

## ⚙️ 配置

您可以通过在项目根目录中创建一个 `.env` 文件或设置环境变量来自定义配置：

  * `ANKI_CONNECT_URL`: Anki-Connect 服务器的 URL (默认为: `http://localhost:8765`)。
  * `ANKI_CONNECT_API_KEY`: Anki-Connect 的 API 密钥 (如果需要)。
  * `ANKI_CONNECT_TIMEOUT`: 请求的超时时间 (默认为: `30.0`)。
  * `LOG_LEVEL`: 服务器的日志级别 (默认为: `info`)。

## 🛠️ 使用方法

服务器启动后，您可以使用任何兼容 MCP 的客户端与其交互。服务器公开了大量工具，每个工具都对应一个 Anki-Connect 操作。

### **示例：查找卡片**

要查找包含特定标签的卡片，您可以调用 `anki_find_cards` 工具：

```json
{
  "tool_name": "anki_find_cards",
  "params": {
    "query": "tag:my-tag"
  }
}
```

### **示例：添加笔记**

要向特定牌组添加新笔记，您可以调用 `anki_add_note` 工具：

```json
{
  "tool_name": "anki_add_note",
  "params": {
    "note": {
      "deckName": "MyDeck",
      "modelName": "Basic",
      "fields": {
        "Front": "Hello",
        "Back": "World"
      },
      "tags": ["new-word"]
    }
  }
}
```