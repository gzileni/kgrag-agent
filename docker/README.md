# Docker

This docker-compose brings up a small infrastructure for the kgrag project:

- `kgrag-mcp-server`: main server (API, Redis, Qdrant, Neo4j with mounted data)
- `kgrag-agent`: agent that connects to the MCP server (SSE)
- `kgrag-loki` + `kgrag-promtail`: log collection (Loki + Promtail)
- `kgrag-grafana`: Grafana UI preconfigured for Loki

## Running

Start the containers from the directory containing the docker-compose:

```bash
docker compose up -d
```

```bash
make run
```

Stop/remove:

```bash
docker compose down
```

or 

```bash
make stop
```

## Containers and exposed ports

- `kgrag_mcp_server`
    - API: `8000`
    - Redis: `6379`
    - Qdrant: `6333`, `6334`
    - Neo4j HTTP/Bolt: `7474`, `7687`
- `kgrag_agent`
    - Port: `8010` (also exposed internally)
- `kgrag-loki`
    - Port: `3100`
- `kgrag-grafana`
    - Port: `3000`

## Persistent volumes

- `qdrant_data` -> `/qdrant/storage`
- `redis_data` -> `/data`
- `neo4j_data` -> `/var/lib/neo4j/data`
- `grafana_data` -> `/var/lib/grafana`
- `loki_log` -> `/var/log`

## Network

- Dedicated bridge network: `kgrag-network` (subnet: `172.16.110.0/24`)

## Main environment variables (define in `.env`)

- `APP_ENV`
- `LLM_MODEL_TYPE`
- `OPENAI_API_KEY`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `AWS_BUCKET_NAME`
- `COLLECTION_NAME`
- `LLM_MODEL_NAME`
- `MODEL_EMBEDDING`
- `LLM_URL`
- `NEO4J_USERNAME`
- `NEO4J_PASSWORD`
- `NEO4J_AUTH`
- `USER_AGENT`

## Operational notes

- Grafana is preconfigured to use Loki as a datasource; the entrypoint automatically creates the provisioning.
- `kgrag-agent` connects to the MCP server via the internal URL: `http://kgrag_mcp_server:8000/sse`
- Redis and Qdrant are exposed on the same host as the `kgrag_mcp_server` container; internal clients should point to service names (e.g. `redis://kgrag_mcp_server:6379`).
- Ensure sensitive variables (`.env`) are not committed to the repository.

## Useful commands

- View logs for a service:

```bash
docker compose logs -f kgrag_mcp_server
```

- Access Grafana: http://localhost:3000
- Check container status:

```bash
docker compose ps
```

## Common issues

- Ports in use: verify local ports (3000, 3100, 8000, etc.) are not already occupied.
- Volume permissions: if Neo4j or Qdrant fail to start, check host volume permissions.
- Missing variables: containers may fail if credentials are missing (e.g. `OPENAI_API_KEY`, `NEO4J_*`).

## Minimal `.env` example

```env
APP_ENV=development
LLM_MODEL_TYPE=openai
OPENAI_API_KEY=your_openai_key
LLM_URL=http://your-llm:port
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=secret
NEO4J_AUTH=neo4j/secret
```

## Contact and maintenance

- Containers use images published on GHCR and Docker Hub; to update images:

```bash
docker compose pull && docker compose up -d
```
