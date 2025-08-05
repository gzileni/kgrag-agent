from config import settings
from langchain_mcp_adapters.client import MultiServerMCPClient

mcp_client = MultiServerMCPClient(
    {
        "kgrag": {
            # Ensure you start your kgrag server on port 8001
            "url": settings.MCP_SERVER_URL,
            "transport": "sse",
        }
    }
)
