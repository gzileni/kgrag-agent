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

### Description of variables 

- `APP_ENV`  
    Application environment. Typical values: `production`, `development`, `staging`. Affects logging, configuration and runtime behavior.

- `USER_AGENT`  
    Identifier used in HTTP requests (User-Agent). Use a descriptive value to help trace requests.

- `OPENAI_API_KEY`  
    API key for OpenAI (or compatible provider). Secret: do not commit to a public repository. Format: alphanumeric string.

- `AWS_ACCESS_KEY_ID`  
    AWS access key ID for S3 operations. Secret: do not commit. Format: string.

- `AWS_SECRET_ACCESS_KEY`  
    AWS secret access key for S3. Secret: do not commit. Format: string.

- `AWS_REGION`  
    AWS region where the bucket resides (e.g. `eu-central-1`).

- `AWS_BUCKET_NAME`  
    Name of the S3 bucket used for storing data/assets.

- `COLLECTION_NAME`  
    Name of the collection used in Qdrant or another vector DB to store vectors.

- `VECTORDB_SENTENCE_TYPE`  
    Type of embedding model to use for Qdrant: `local` (local model) or `hf` (Hugging Face automatic download). If `local`, also set `VECTORDB_SENTENCE_PATH`; if `hf`, set `VECTORDB_SENTENCE_MODEL`.

- `VECTORDB_SENTENCE_MODEL`  
    Name of the embedding model (e.g. `BAAI/bge-small-en-v1.5` or others listed in the file). For `hf` it will be downloaded from Hugging Face; ignored for `local`.

- `LLM_MODEL_TYPE`  
    Type of LLM provider: supported values in the project e.g. `openai`, `ollama`, `vllm`. Determines the invocation method.

- `LLM_URL`  
    Endpoint of the LLM service (e.g. `http://localhost:11434` for Ollama or a custom API URL).

- `LLM_MODEL_NAME`  
    Name of the LLM model to use on the selected provider (e.g. `tinyllama`, `gpt-4.1-mini`, etc.).

- `MODEL_EMBEDDING`  
    Name of the embedding model for general use (e.g. `nomic-embed-text`, `text-embedding-3-small`). Must be compatible with the chosen provider.

- `NEO4J_USERNAME`  
    Username for connecting to Neo4j.

- `NEO4J_PASSWORD`  
    Password for Neo4j. Secret: do not commit.

- `NEO4J_AUTH`  
    Authentication string for Neo4j, typically in the format `username/password`. Some clients require this combined form.

- `REDIS_URL`  
    Redis connection URL, e.g. `redis://host:port`. May include credentials if needed (be cautious with security).

- `REDIS_HOST`  
    Redis host (used if `REDIS_URL` is not used).

- `REDIS_PORT`  
    Redis port (e.g. `6379`).

- `REDIS_DB`  
    Redis database index to use (integer).

- `APP_VERSION`  
    Application/image version (semver or free-form string) used for tracking/telemetry.

- `A2A_CLIENT`  
    URL of the agent-to-agent (A2A) client used for internal agent communications, e.g. `http://kgrag_agent:8010`.

Security and operational notes:
- Do not place keys and secrets in public repositories. Use a secret manager or an .env file excluded from VCS.  
- Some variables (embedding/LLM models) must be compatible with the local runtime or remote services configured; check the providers' documentation if you encounter loading errors.  
- If you use `VECTORDB_SENTENCE_TYPE=local`, set the local model path via the dedicated variable (not included in the example file).  
- Ensure `NEO4J_AUTH` matches the actual credentials used by the Neo4j container and that the host/container ports in the compose file are correct.  
- For Redis in containerized environments prefer the service host on the overlay network (e.g. `redis://redis:6379`) rather than `localhost`.  
- Change access defaults (e.g. Grafana anonymous admin) before exposing to production.  
- Always rotate keys that have been leaked or accidentally published.

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
