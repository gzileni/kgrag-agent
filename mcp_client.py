from langchain_mcp_adapters.client import MultiServerMCPClient

kgrag_mcp_client = MultiServerMCPClient(
    {
        "kgrag": {
            # Ensure you start your kgrag server on port 8001
            "url": "http://localhost:8001/sse",
            "transport": "sse",
        }
    }
)