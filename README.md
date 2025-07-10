# Anki MCP Server

[中文](./README.cn.md)


Anki MCP Server is a FastMCP-based server designed to provide a Model Context Protocol (MCP) interface for Anki through the Anki-Connect plugin. This allows external applications to interact with Anki in a structured way, enabling programmatic management of cards, decks, notes, and templates.

## 🌟 Features

  * **Comprehensive Anki Operations**: Provides a complete set of tools for managing almost every aspect of Anki, including:
      * **Card Management**: Add, delete, suspend/unsuspend, and find cards, as well as get/set ease factors.
      * **Deck Management**: Create, delete, and rename decks, and move cards between different decks.
      * **Note Management**: Create, delete, and update note content and tags.
      * **Template (Note Type) Management**: Create, delete, and modify templates and fields.
  * **Asynchronous Architecture**: Built on `asyncio` and `httpx`, it enables efficient, non-blocking I/O operations, allowing it to handle multiple requests concurrently.
  * **Flexible Configuration**: Easily configure the Anki-Connect URL, API key, and server log level through environment variables or a `.env` file.
  * **Structured Data Models**: Uses Pydantic models to define all Anki-Connect API requests and responses, ensuring type safety and data consistency.
  * **Clear Tool Definitions**: Each Anki-Connect operation is encapsulated in an MCP tool with a clear name, description, and type annotations.

## 🚀 Quick Start

### **Prerequisites**

  * Python 3.8+
  * Anki Desktop Application
  * [Anki-Connect](https://ankiweb.net/shared/info/2055492159) plugin installed and enabled

### **Installation**

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/ruiqurm/anki-mcp-server.git
    cd anki-mcp-server
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

### **Running the Server**

You can start the server via the `run_server.py` script or directly as a Python module:

**Via script:**

```bash
python run_server.py
```

**As a module:**

```bash
python -m src.anki_mcp_server
```

Once started, the server will connect to Anki-Connect running at `http://localhost:8765`.

## ⚙️ Configuration

You can customize the configuration by creating a `.env` file in the project's root directory or by setting environment variables:

  * `ANKI_CONNECT_URL`: The URL of the Anki-Connect server (default: `http://localhost:8765`).
  * `ANKI_CONNECT_API_KEY`: The API key for Anki-Connect (if required).
  * `ANKI_CONNECT_TIMEOUT`: The timeout for requests (default: `30.0`).
  * `LOG_LEVEL`: The log level for the server (default: `info`).

## 🛠️ Usage

Once the server is running, you can interact with it using any MCP-compatible client. The server exposes a large number of tools, each corresponding to an Anki-Connect action.

### **Example: Find Cards**

To find cards with a specific tag, you can call the `anki_find_cards` tool:

```json
{
  "tool_name": "anki_find_cards",
  "params": {
    "query": "tag:my-tag"
  }
}
```

### **Example: Add a Note**

To add a new note to a specific deck, you can call the `anki_add_note` tool:

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