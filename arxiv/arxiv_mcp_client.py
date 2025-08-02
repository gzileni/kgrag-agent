from langchain_mcp_adapters.client import MultiServerMCPClient

arxiv_mcp_client = MultiServerMCPClient(
    {
        "arxiv": {
            # Ensure you start your arxiv server on port 8001
            "url": "http://localhost:8001/sse",
            "transport": "sse",
        }
    }
)
