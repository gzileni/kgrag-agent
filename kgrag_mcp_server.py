import uuid
from mcp.server.fastmcp import FastMCP
from krag import (
    PARSER_PROMPT,
    AGENT_PROMPT,
    kgrag
)
from starlette.applications import Starlette
from starlette.routing import Mount

# Initialize FastMCP server
mcp = FastMCP("KGraph")


@mcp.tool(
    name="query",
    description="Ingest a document into the KGraph system."
)
async def query(
    query: str = "",
    thread_id: str = str(uuid.uuid4())
):
    """
    Ingest a document into the KGraph system.
    Args:
        query (str): Query for the document to be ingested.
    """
    response = await kgrag.query(query)
    return {
        "jsonrpc": "2.0",
        "result": {
            "message": str(response)
        },
        "id": thread_id
    }


@mcp.tool(
    name="ingestion_document",
    description="Ingest a path of file into the KGraph system."
)
async def ingestion_document(
    path_file: str
):
    """
    Ingest a document into the KGraph system.
    Args:
        path_file (str): Path to the document file to be ingested.
    """
    async for d in kgrag.process_documents(path=path_file):
        return f"Document {d} ingested successfully."


@mcp.prompt(title="Parser Text Prompt")
def parser_text_prompt(text: str) -> str:
    """
    Generate a prompt for extracting relationships from text.
    Args:
        text (str): The input text to extract relationships from.
    Returns:
        str: The formatted prompt for the relationship extractor.
    """
    return PARSER_PROMPT


@mcp.prompt(title="Agent Query Prompt")
def agent_query_prompt(nodes_str: str, edges_str: str, user_query: str) -> str:
    """
    Generate a prompt for the agent to answer a user query
    using the knowledge graph.
    Args:
        nodes_str (str): String representation of nodes in the graph.
        edges_str (str): String representation of edges in the graph.
        user_query (str): The user's query to be answered.
    Returns:
        str: The formatted prompt for the agent.
    """
    return AGENT_PROMPT.format(
        nodes_str=nodes_str,
        edges_str=edges_str,
        user_query=user_query
    )


# Mount the SSE server to the existing ASGI server
app = Starlette(
    routes=[
        Mount('/', app=mcp.sse_app()),
    ]
)
