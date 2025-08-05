# Krag Agent

Krag Agent is a modular system for managing, ingesting, and querying structured and unstructured data, designed for easy integration with graph databases (Neo4j), AWS S3 storage, Redis cache, vector search engines (Qdrant), and advanced language models (LLM). The project provides a scalable, containerized infrastructure via Docker Compose to orchestrate data pipelines, semantic enrichment, and analysis through advanced queries. Ideal for knowledge graph, AI, and information flow automation applications.

## 🔧 Environment Variables

Example organization for multiple environments:

```
.env.development
.env.staging
.env.production
.env.test
.env.openai.development
.env.local
```

### 🌍 General

| Variable               | Default              | Description                                                                 |
| ---------------------- | -------------------- | --------------------------------------------------------------------------- |
| `APP_ENV`              | `development`        | Execution environment (`development`, `staging`, `production`, `test`).     |
| `COLLECTION_NAME`      | `kgrag_data`         | Name of the collection for data ingestion.                                  |

---

### ☁️ AWS S3

| Variable                | Default          | Description                              |
| ----------------------- | ---------------- | ---------------------------------------- |
| `AWS_ACCESS_KEY_ID`     | **required**     | AWS access key for S3 access.            |
| `AWS_SECRET_ACCESS_KEY` | **required**     | AWS secret key for S3 access.            |
| `AWS_BUCKET_NAME`       | **required**     | Name of the S3 bucket.                   |
| `AWS_REGION`            | **required**     | AWS region.                              |

---

### 🗄️ Neo4j

| Variable         | Default                   | Description                                         |
| ---------------- | ------------------------- | --------------------------------------------------- |
| `NEO4J_URL`      | `neo4j://localhost:47687` | Neo4j connection URL.                               |
| `NEO4J_USERNAME` | `neo4j`                   | Username for Neo4j.                                 |
| `NEO4J_PASSWORD` | `n304j2025`               | Password for Neo4j.                                 |
| `NEO4J_DB_NAME`  | *(empty)*                 | Neo4j database name (if different from default).    |

---

### 🔄 Redis

| Variable     | Default                  | Description                |
| ------------ | ------------------------ | -------------------------- |
| `REDIS_URL`  | `redis://localhost:6379` | Full URL for Redis.        |
| `REDIS_HOST` | `localhost`              | Redis host.                |
| `REDIS_PORT` | `6379`                   | Redis port.                |
| `REDIS_DB`   | `4`                      | Redis database number.     |

---

### 🔍 Qdrant

| Variable     | Default                 | Description                |
| ------------ | ----------------------- | -------------------------- |
| `QDRANT_URL` | `http://localhost:6333` | Qdrant instance URL.       |

---

### 📊 Loki

| Variable   | Default                                  | Description                |
| ---------- | ---------------------------------------- | -------------------------- |
| `LOKI_URL` | `http://localhost:3100/loki/api/v1/push` | Loki push URL.             |

---

### 🤖 LLM (Large Language Model)

| Variable            | Default                  | Description                                         |
| ------------------- | ------------------------ | --------------------------------------------------- |
| `LLM_MODEL_TYPE`    | `openai`                 | Model type (`openai`, `azure`, `local`, etc.).      |
| `LLM_MODEL_NAME`    | `gpt-4.1-mini`           | Name of the LLM model to use.                       |
| `LLM_EMBEDDING_URL` | *(empty)*                | Custom embedding endpoint.                          |
| `MODEL_EMBEDDING`   | `text-embedding-3-small` | Model for embeddings.                               |
| `LLM_URL`           | *(empty)*                | LLM API endpoint.                                   |

---

### 🧠 Vector DB

| Variable                  | Default                  | Description                                 |
| ------------------------- | ------------------------ | ------------------------------------------- |
| `VECTORDB_SENTENCE_MODEL` | `BAAI/bge-small-en-v1.5` | Embedding model for vectors.                |
| `VECTORDB_SENTENCE_TYPE`  | `hf`                     | Model type (`hf`, `local`).                 |
| `VECTORDB_SENTENCE_PATH`  | *(empty)*                | Local path for vector model.

## ⚙️ Docker

This project uses **Docker Compose** to run the **KGrag Agent** stack.
The **Makefile** provides quick commands to start, stop, and restart services.

---

### 📦 Requirements

* [Docker](https://docs.docker.com/get-docker/) ≥ 20.x
* [Docker Compose](https://docs.docker.com/compose/) ≥ 2.x
* [Make](https://www.gnu.org/software/make/)

---

### 🚀 Available Commands

#### ▶️ Start the stack

Start all services in **detached** mode (`-d`):

```bash
make run
```

Internally runs:

```bash
docker-compose -p kgrag-agent up -d
```

---

#### ⏹️ Stop the stack

Stops and removes containers defined in `docker-compose.yml`:

```bash
make stop
```

Internally runs:

```bash
docker-compose down
```

---

#### 🔄 Restart the stack

Stops and restarts services:

```bash
make restart
```

Equivalent to:

```bash
make stop && make run
```

---

### 📜 Notes

* The stack uses the **Docker Compose project** named `kgrag-agent`.
* You can customize services by editing the `docker-compose.yml` file.
* To view logs in real time:

    ```bash
    docker-compose -p kgrag-agent logs -f
    ```

## 🧠 KGraph MCP Server

This project implements an **MCP (Model Context Protocol) Server** to interact with the **KGraph** system.
It allows you to **query** and **ingest documents** into a **Knowledge Graph** based on **GraphRAG**, using the MCP protocol.

---

### 🚀 Features

The server provides **tools** and **prompts** to interact with the graph via MCP:

#### **Tools**

##### 1️⃣ `query`

Queries the **Knowledge Graph** to obtain answers based on stored documents and relationships.

```python
@mcp.tool(
        name="query",
        description="Ingest a document into the KGraph system."
)
```

**Parameters**:

* `query` (`str`) → Question to ask the graph.
* `thread_id` (`str`) → Session ID (default: auto-generated).

**Example response**:

```json
{
    "jsonrpc": "2.0",
    "result": {
        "message": "Alan Turing collaborated with John von Neumann."
    },
    "id": "uuid-thread-id"
}
```

---

##### 2️⃣ `ingestion_document`

Ingests a document from the file system into the graph.

```python
@mcp.tool(
        name="ingestion_document",
        description="Ingest a path of file into the KGraph system."
)
```

**Parameters**:

* `path_file` (`str`) → Path to the file to ingest.

**Example**:

```json
"Document example.pdf ingested successfully."
```

---

#### **Prompts**

##### 📜 `parser_text_prompt`

Generates the **prompt** to extract relationships from text.

```python
@mcp.prompt(title="Parser Text Prompt")
```

Uses the `PARSER_PROMPT` constant defined in `kgrag_store`.

---

#### 🤖 `agent_query_prompt`

Generates the **prompt** to answer graph-based queries.

```python
@mcp.prompt(title="Agent Query Prompt")
```

Uses the `AGENT_PROMPT` constant and formats data from:

* `nodes_str` → list of nodes
* `edges_str` → list of relationships
* `user_query` → user question

---

### ⚙️ Server Startup

#### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

#### 2️⃣ Start

```bash
uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000
```

---

### 🔌 MCP Endpoint

The server exposes an **SSE (Server-Sent Events)** endpoint at `/`.

**Example call**:

```http
GET / HTTP/1.1
Host: localhost:8000
Accept: text/event-stream
```

---

### 📦 Architecture

```
+------------------+
|   MCP Client     |
+------------------+
                │
                ▼
+------------------+
| FastMCP Server   |
| (tools & prompts)|
+------------------+
                │
                ▼
+------------------+
|   KGraph Core    |
| (KGragRetriever  |
|  + KGragGraph)   |
+------------------+
                │
                ▼
+------------------+
| Neo4j & Qdrant   |
+------------------+
```
