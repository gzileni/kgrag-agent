# KGrag Agent

## Dependencies

- [`kgrag-store`](https://github.com/gzileni/kgrag-store): Core data storage and graph management library.
- [`memory-agent`](https://github.com/gzileni/memory-agent): A Python library for advanced memory management in AI agent applications
- [`kgrag.mcp-server`](https://github.com/gzileni/krag_mcp_server): server that implements the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) for managing, ingesting, and querying structured and unstructured data

## [Development](DEV.md)

```bash
curl --location --request GET '' \
--header 'Content-Type: application/json' \
--data '{
    "user_input": "Cos'\''è il Machine Learning?"
}'
```

### Ingestion 

```bash
curl --location 'http://localhost:8001/agent' \
--header 'Content-Type: application/json' \
--data '{
    "user_input": "/Users/giuseppezileni/arxiv/2508.03696v1.pdf"
}'
```


