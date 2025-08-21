[![View on GitHub](https://img.shields.io/badge/View%20on-GitHub-181717?style=for-the-badge&logo=github)](https://github.com/gzileni/kgrag-agent)
[![GitHub stars](https://img.shields.io/github/stars/gzileni/kgrag-agent?style=social)](https://github.com/gzileni/kgrag-agent/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/gzileni/kgrag-agent?style=social)](https://github.com/gzileni/kgrag-agent/network)

## Agent description

Agent for ingesting and querying structured and unstructured content. Accepts PDF, CSV, JSON, and TXT files, extracts text and metadata, normalizes the content, and imports it into a semantic graph to enable complex queries over informational links.

### Key features
- Supported formats: PDF (with optional OCR), CSV, JSON, TXT.
- Extraction: parsing of tabular structures, extraction of text and metadata (author, timestamp, column names, etc.).
- Cleaning and normalization: noise removal, tokenization, segmentation into semantic chunks.
- Enrichment: extraction of entities, relationships, and semantic annotations to create nodes and edges.
- Graph ingestion: mapping entities to nodes, creating semantic edges, and storing them in the graph backend.
- Graph queries: searches by entity, paths between nodes, pattern matching and aggregations; support for textual and structured queries.
- Traceability: preserving references to original documents and text blocks to reconstruct context.

### Benefits
- Transforms diverse document formats into a queryable graph representation.
- Enables semantic analysis and discovery of hidden relationships across heterogeneous data.
- Eases integration with existing pipelines (e.g., kgrag-store, MCP server) for advanced search and reasoning.

### Example workflow
1. File reception → 2. Extraction and normalization → 3. Entity/relationship extraction → 4. Graph ingestion → 5. Execute queries and retrieve results

## Dependencies

- [`kgrag-store`](https://gzileni.github.io/kgrag-store/): Core data storage and graph management library.
- [`memory-agent`](https://gzileni.github.io/memory-agent): A Python library for advanced memory management in AI agent applications
- [`kgrag-mcp-server`](https://gzileni.github.io/kgrag_mcp_server): server that implements the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) for managing, ingesting, and querying structured and unstructured data

## [Development](DEV.md)

## A2A

## [Docker](./docker/README.md)


